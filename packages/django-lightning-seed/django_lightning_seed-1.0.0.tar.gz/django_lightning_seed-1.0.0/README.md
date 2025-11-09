# django-lightning-seed

⚡️A blazing-fast Django management command for seeding data

[![CI](https://github.com/spider-hand/django-lightning-seed/actions/workflows/ci.yml/badge.svg)](https://github.com/spider-hand/django-lightning-seed/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![python](https://img.shields.io/badge/python-3.13-blue)]() [![codecov](https://codecov.io/github/spider-hand/django-lightning-seed/graph/badge.svg?token=39R0AH357O)](https://codecov.io/github/spider-hand/django-lightning-seed)

## Installation

```bash
pip install django-lightning-seed
```

Then add it to your `INSTALLED_APPS`:

```py
INSTALLED_APPS = [
    ...
    "django_lightning_seed",
]
```

## Usage

```bash
python manage.py lightning_seed
```

### Options

| Option    | Description                                 | Default | Example                  |
| --------- | ------------------------------------------- | ------- | ------------------------ |
| `--model` | Specify the model as `app_label.ModelName`. |         | `--model tests.TestUser` |
| `--count` | Number of records to insert.                | 100,000 | `--count 50000`          |

### Supported Field Types

| Category     | Field Types                                                                  |
| ------------ | ---------------------------------------------------------------------------- |
| Numeric      | `IntegerField`, `BigIntegerField`, `FloatField`, `DecimalField`              |
| String       | `CharField`, `TextField`, `SlugField`, `EmailField`, `URLField`, `UUIDField` |
| Date / Time  | `DateField`, `DateTimeField`, `TimeField`                                    |
| Boolean      | `BooleanField`                                                               |
| JSON         | `JSONField`                                                                  |
| Relationship | `ForeignKey`                                                                 |

## License

[MIT](./LICENSE)
