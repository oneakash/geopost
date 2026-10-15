from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .forms import PropertySearchForm
from .management.commands.generate_location_embeddings import Command
from .semantic import embed_text


class SemanticSearchTests(SimpleTestCase):
    @patch("properties.semantic.get_embedding_model")
    def test_embed_text_normalizes_and_returns_a_list(self, get_model):
        model = Mock()
        model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        get_model.return_value = model

        result = embed_text("a quiet family home")

        self.assertEqual(result, [0.1, 0.2, 0.3])
        model.encode.assert_called_once_with(
            "a quiet family home",
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    def test_empty_semantic_query_is_allowed_for_regular_search(self):
        form = PropertySearchForm(data={"semantic_query": ""})

        self.assertTrue(form.is_valid())

    def test_location_text_contains_the_searchable_location_fields(self):
        location = Mock(
            name="Gulshan 2",
            address="Road 12",
            city="Dhaka",
            state="Dhaka",
            country="Bangladesh",
        )

        self.assertEqual(
            Command.location_text(location),
            "Gulshan 2, Road 12, Dhaka, Dhaka, Bangladesh",
        )
