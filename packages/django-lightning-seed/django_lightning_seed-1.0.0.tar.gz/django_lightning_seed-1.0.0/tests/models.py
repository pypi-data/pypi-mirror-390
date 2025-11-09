from django.db import models

# Create your models here.


class TestBaseModel(models.Model):
    # String fields
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField()
    website_url = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    uuid = models.UUIDField(unique=True, editable=False)

    # Numeric fields
    age = models.IntegerField()
    score = models.FloatField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    followers = models.BigIntegerField()

    # Date and time fields
    joined_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField()
    wake_time = models.TimeField()

    # Boolean field
    is_active = models.BooleanField()

    # JSON field
    json = models.JSONField()

    class Meta:
        abstract = True


class TestParent(TestBaseModel):
    class Meta:
        db_table = "test_user"


class TestChild(TestBaseModel):
    parent = models.ForeignKey(
        TestParent, on_delete=models.CASCADE, related_name="children"
    )
    parents = models.ManyToManyField(TestParent, related_name="many_children")

    class Meta:
        db_table = "test_child"
