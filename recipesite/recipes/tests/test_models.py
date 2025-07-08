import pytest
from django.contrib.auth.models import User
from recipes.models import Recipe  # Adjust 'recipes' to your actual app name
from django.utils import timezone


@pytest.mark.django_db
def test_create_recipe():
    """
    Test creating a Recipe instance with valid data.
    This covers:
    - Model instantiation
    - Field assignments
    - Relationship to User
    - Default values
    """
    # Test user for the recipe
    user = User.objects.create_user(username='testuser', password='password')

    # The recipe linked to the user
    recipe = Recipe.objects.create(
        name="Pasta",
        description="Delicious creamy pasta.",
        cost=15,
        time=30,
        ingredients="Pasta, Cream, Cheese",
        diet="Vegetarian",
        user=user,
    )

    # Check that all fields are correctly assigned
    assert recipe.name == "Pasta"
    assert recipe.description == "Delicious creamy pasta."
    assert recipe.cost == 15
    assert recipe.time == 30
    assert recipe.ingredients == "Pasta, Cream, Cheese"
    assert recipe.diet == "Vegetarian"
    assert recipe.user == user

    # Check default field values
    assert recipe.is_public is True
    assert isinstance(recipe.created_at, timezone.datetime)


@pytest.mark.django_db
def test_recipe_str_representation():
    """
    Test the __str__ method of the Recipe model.
    Ensures it returns the recipe name as expected.
    """
    recipe = Recipe(name="Salad")
    assert str(recipe) == "Salad"


@pytest.mark.django_db
def test_recipe_null_user_allowed():
    """
    Test that the Recipe model allows a null user.
    """
    recipe = Recipe.objects.create(
        name="Soup",
        description="Hearty vegetable soup.",
        cost=10,
        time=20,
        ingredients="Carrots, Potatoes, Onion",
        diet="Vegan",
        user=None,
    )
    assert recipe.user is None
