import pytest
from django.contrib.auth.models import User
from recipes.forms import RecipeForm
from recipes.models import Recipe


@pytest.fixture
def valid_recipe_data():
    """
    Provides a dictionary of valid data for creating a RecipeForm.
    Shared across tests for consistency and reduce repetition.
    """
    return {
        "name": "Vegan Tacos",
        "description": "Delicious and spicy tacos.",
        "cost": 12,
        "time": 30,
        "ingredients": "Tortilla, Beans, Avocado",
        "diet": "Vegan",
        "is_public": True,
    }


def test_recipe_form_valid(valid_recipe_data):
    """
    Test that RecipeForm is valid when all required fields are present and correct.
    """
    form = RecipeForm(data=valid_recipe_data)
    assert form.is_valid()


def test_recipe_form_missing_required_field(valid_recipe_data):
    """
    Test that RecipeForm is invalid if a required field ('name') is missing.
    """
    data = valid_recipe_data.copy()
    data.pop("name")  # Simulate missing required field
    form = RecipeForm(data=data)

    assert not form.is_valid()
    assert "name" in form.errors  # Ensure the error is specific to 'name'


def test_recipe_form_excluded_fields():
    """
    Ensure that 'user' and 'created_at' fields are not exposed in the form.
    These should be set automatically in the view/backend, not user-editable.
    """
    form = RecipeForm()

    # Check excluded fields are not in form
    assert "user" not in form.fields
    assert "created_at" not in form.fields


@pytest.mark.django_db
def test_recipe_form_save_with_user(valid_recipe_data):
    """
    Test that a valid RecipeForm can be saved with a user assigned manually.
    Simulates view behavior using commit=False to inject the user before saving.
    """
    # Create a user instance to associate with the recipe
    user = User.objects.create_user(username="chef", password="safepassword")

    form = RecipeForm(data=valid_recipe_data)
    assert form.is_valid()  # Double-check that input is valid

    # Save form without committing to DB, so we can add the user
    recipe = form.save(commit=False)
    recipe.user = user
    recipe.save()

    # Confirm the recipe was saved and correctly linked to the user
    saved = Recipe.objects.get(pk=recipe.pk)
    assert saved.name == valid_recipe_data["name"]
    assert saved.user == user
