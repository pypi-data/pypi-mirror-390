from django.apps import apps
from django.core.management import call_command, CommandError
from django.test import TestCase
from django.db import connection
from django.db import models
from tests.models import TestParent, TestChild


class LightningSeedCommandTests(TestCase):
    def setUp(self):
        TestParent.objects.all().delete()
        TestChild.objects.all().delete()

    def run_command_for_model(self, model, **options):
        """
        Helper method to run lightning_seed for a specific model with mocked input.
        """
        # Identify the model index dynamically
        app_models = list(apps.get_models())
        model_index = app_models.index(model) + 1

        # Mock input() to return the index
        def fake_input(prompt):
            return str(model_index)

        original_input = __builtins__["input"]
        __builtins__["input"] = fake_input

        try:
            call_command("lightning_seed", **options)
        finally:
            __builtins__["input"] = original_input

    def test_command_not_postgresql(self):
        """
        Ensure that the command raises an error when not using PostgreSQL.
        """
        connection.vendor = "sqlite"
        with self.assertRaises(CommandError) as context:
            self.run_command_for_model(TestParent)
        self.assertIn(
            "❌ This command only supports PostgreSQL.", str(context.exception)
        )
        connection.vendor = "postgresql"

    def test_invalid_model_specification(self):
        """
        Ensure that the command raises an error for invalid model specification.
        """
        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed", model="invalidmodel")
        self.assertIn(
            "❌ Model must be specified as 'app_label.ModelName'.",
            str(context.exception),
        )

    def test_model_not_found(self):
        """
        Ensure that the command raises an error when the specified model is not found.
        """
        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed", model="nonexistent.AppModel")
        self.assertIn(
            "❌ Model 'nonexistent.AppModel' not found.", str(context.exception)
        )

    def test_invalid_model_selection(self):
        """
        Ensure that the command raises an error for invalid model selection.
        """

        def fake_input_invalid(prompt):
            return "9999"  # Invalid index

        __builtins__["input"] = fake_input_invalid

        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed")
        self.assertIn("❌ Invalid model selection.", str(context.exception))

    def test_no_insertable_fields_model(self):
        """
        Ensure that the command raises an error when the model has no insertable fields.
        """

        class EmptyModel(models.Model):
            class Meta:
                app_label = "tests"
                db_table = "empty_model"

        apps.register_model("tests", EmptyModel)

        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed", model="tests.EmptyModel")

        self.assertIn(
            "❌ Selected model has no insertable fields.", str(context.exception)
        )

    def test_child_without_parent(self):
        """
        Ensure that inserting a child model without a parent raises an error.
        """
        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed", model="tests.TestChild", count=10)

        self.assertIn(
            f"❌ Parent model '{TestParent.__name__}' has no records. Please seed it first.",
            str(context.exception),
        )

    def test_association(self):
        """
        Ensure that the command can handle model associations correctly.
        """
        self.run_command_for_model(TestParent, count=5)
        self.run_command_for_model(TestChild, count=5)
        self.assertEqual(TestChild.objects.count(), 5)

    def test_unsupported_field_type(self):
        """
        Ensure that unsupported field types raise the proper CommandError.
        """

        class UnsupportedModel(models.Model):
            binary = models.BinaryField()  # unsupported in generator

            class Meta:
                app_label = "tests"
                db_table = "unsupported_model"

        apps.register_model("tests", UnsupportedModel)

        with self.assertRaises(CommandError) as context:
            call_command("lightning_seed", model="tests.UnsupportedModel")

        self.assertIn(
            "❌ Unsupported field type: 'BinaryField' field 'binary'.",
            str(context.exception),
        )

    def test_command_inserts_data(self):
        """
        Ensure that the command inserts data into TestParent.
        """
        self.run_command_for_model(TestParent)
        self.assertGreater(TestParent.objects.count(), 0)

    def test_command_count_option(self):
        """
        Ensure that the --count option works as expected.
        """
        self.run_command_for_model(TestParent, count=50)
        self.assertEqual(TestParent.objects.count(), 50)

    def test_command_model_option(self):
        """
        Ensure that the --model option works as expected.
        """
        call_command("lightning_seed", model="tests.TestParent", count=30)
        self.assertEqual(TestParent.objects.count(), 30)
