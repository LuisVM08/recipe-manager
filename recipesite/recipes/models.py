from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.


class Recipe(models.Model):
    # The name/title of the recipe
    name = models.CharField(max_length=100)

    # A detailed description of the recipe (e.g., how it tastes, when to serve it)
    description = models.TextField()

    # Estimated cost to prepare the recipe
    cost = models.IntegerField()

    # Estimated time to prepare the recipe (in minutes)
    time = models.IntegerField()

    # List of ingredients required for the recipe
    ingredients = models.TextField()

    # Dietary information or classification (e.g., "vegan", "gluten-free")
    diet = models.TextField()

    # ForeignKey linking each recipe to a specific user (the recipe's author)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # Boolean flag to indicate if the recipe should be publicly visible to others
    is_public = models.BooleanField(default=True)

    # Timestamp for when the recipe was created; defaults to the current time
    created_at = models.DateTimeField(default=timezone.now)

    # String representation of the object
    def __str__(self):
        return self.name