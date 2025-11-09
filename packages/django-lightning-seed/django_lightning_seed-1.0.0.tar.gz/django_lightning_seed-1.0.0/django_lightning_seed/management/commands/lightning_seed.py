from django.core.management.base import BaseCommand, CommandError
from django.db import connection, models
from django.apps import apps
from faker import Faker
import polars as pl
import numpy as np
from io import StringIO
import uuid
import json
from datetime import datetime, date, time


class Command(BaseCommand):
    help = "⚡️ Generate seed data with lightning speed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100000,
            help="Number of records to generate (default: 100000)",
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Model to seed, specified as 'app_label.ModelName'.",
        )

    def generate(self, fields, num_records, fake):
        """
        Generate fake data for the given fields.
        """
        data = {}
        for field in fields:
            # Generate numbers
            if isinstance(field, models.IntegerField):
                if isinstance(field, models.BigIntegerField):
                    data[field.name] = np.random.randint(
                        1, 10**12 + 1, size=num_records
                    ).tolist()
                else:
                    data[field.name] = np.random.randint(
                        1, 1001, size=num_records
                    ).tolist()
            elif isinstance(field, models.FloatField):
                data[field.name] = np.random.uniform(0, 1000, size=num_records).tolist()
            elif isinstance(field, models.DecimalField):
                data[field.name] = np.round(
                    np.random.uniform(0, 9999, size=num_records), field.decimal_places
                ).tolist()

            # Generate strings
            elif isinstance(field, models.EmailField) or "email" in field.name:
                data[field.name] = [
                    f"user_{uuid.uuid4().hex}@example.com" for _ in range(num_records)
                ]
            elif isinstance(field, models.URLField) or "url" in field.name:
                data[field.name] = [
                    f"https://example.com/{uuid.uuid4().hex[:6]}"
                    for _ in range(num_records)
                ]
            elif isinstance(field, models.SlugField) or "slug" in field.name:
                data[field.name] = [
                    f"slug-{uuid.uuid4().hex}" for _ in range(num_records)
                ]
            elif isinstance(field, models.UUIDField):
                data[field.name] = [str(uuid.uuid4()) for _ in range(num_records)]
            elif isinstance(field, models.CharField):
                data[field.name] = [fake.word() for _ in range(num_records)]
            elif isinstance(field, models.TextField):
                data[field.name] = [
                    fake.paragraph(nb_sentences=3) for _ in range(num_records)
                ]

            # Generate dates and times
            elif isinstance(field, models.DateTimeField):
                # Generate random timestamps for this year
                start_date = datetime(datetime.now().year, 1, 1)
                end_date = datetime(datetime.now().year, 12, 31, 23, 59, 59)
                start_timestamp = start_date.timestamp()
                end_timestamp = end_date.timestamp()
                random_timestamps = np.random.uniform(
                    start_timestamp, end_timestamp, size=num_records
                )
                data[field.name] = [
                    datetime.fromtimestamp(ts).isoformat() for ts in random_timestamps
                ]
            elif isinstance(field, models.DateField):
                # Generate random dates for this year
                start_date = date(datetime.now().year, 1, 1)
                end_date = date(datetime.now().year, 12, 31)
                start_ordinal = start_date.toordinal()
                end_ordinal = end_date.toordinal()
                random_ordinals = np.random.randint(
                    start_ordinal, end_ordinal + 1, size=num_records
                )
                data[field.name] = [
                    date.fromordinal(ordinal).isoformat() for ordinal in random_ordinals
                ]
            elif isinstance(field, models.TimeField):
                # Generate random times (0-86399 seconds in a day)
                random_seconds = np.random.randint(0, 86400, size=num_records)
                data[field.name] = [
                    time(
                        hour=s // 3600, minute=(s % 3600) // 60, second=s % 60
                    ).isoformat()
                    for s in random_seconds
                ]

            # Generate booleans
            elif isinstance(field, models.BooleanField):
                data[field.name] = np.random.choice(
                    [True, False], size=num_records
                ).tolist()

            # Fill JSON with empty dicts
            elif isinstance(field, models.JSONField):
                data[field.name] = [json.dumps({}) for _ in range(num_records)]

            # ForeignKey
            elif isinstance(field, models.ForeignKey):
                parent_model = field.related_model
                parent_ids = list(parent_model.objects.values_list("id", flat=True))
                if not parent_ids:
                    raise CommandError(
                        f"❌ Parent model '{parent_model.__name__}' has no records. Please seed it first."
                    )
                data[field.column] = np.random.choice(
                    parent_ids, size=num_records
                ).tolist()

            # ManyToManyField
            elif isinstance(field, models.ManyToManyField):
                self.stdout.write(
                    f"⚠️ Skipping '{field.get_internal_type()}' field '{field.name}'."
                )

            else:
                raise CommandError(
                    f"❌ Unsupported field type: '{field.get_internal_type()}' field '{field.name}'."
                )
        return data

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            raise CommandError("❌ This command only supports PostgreSQL.")

        fake = Faker()
        num_records = options["count"]
        model_option = options.get("model")

        model = None

        if model_option:
            try:
                app_label, model_name = model_option.split(".")
            except ValueError:
                raise CommandError(
                    "❌ Model must be specified as 'app_label.ModelName'."
                )

            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                raise CommandError(f"❌ Model '{model_option}' not found.")
        else:
            # Get models
            app_models = list(apps.get_models())
            self.stdout.write("Available models:")
            for i, model in enumerate(app_models):
                self.stdout.write(f"{i + 1}. {model.__name__}")

            # Select model
            try:
                index = int(input("Select model index: ")) - 1
                model = app_models[index]
            except (ValueError, IndexError):
                raise CommandError("❌ Invalid model selection.")

        table_name = model._meta.db_table
        fields = [
            f for f in model._meta.get_fields() if f.concrete and not f.auto_created
        ]

        if not fields:
            raise CommandError("❌ Selected model has no insertable fields.")

        self.stdout.write(f"Selected model: {model.__name__}")
        self.stdout.write(f"Table name: {table_name}")
        self.stdout.write(f"Fields: {', '.join([f.name for f in fields])}")
        self.stdout.write("⚙️ Generating fake data...")

        # Generate fake data for each field
        data = self.generate(fields, num_records, fake)
        df = pl.DataFrame(data)

        # Bulk insert using COPY
        self.stdout.write("💾 Inserting data into the database...")

        csv_buffer = StringIO()
        df.write_csv(csv_buffer, include_header=False)
        csv_buffer.seek(0)

        with connection.cursor() as cursor:
            cursor.copy_from(
                file=csv_buffer,
                table=table_name,
                sep=",",
                columns=list(df.columns),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"⚡️ Inserted {num_records} records into {table_name} successfully!"
            )
        )
