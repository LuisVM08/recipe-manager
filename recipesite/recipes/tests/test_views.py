import pytest
from django.urls import reverse
from recipes.models import Recipe
from django.contrib.auth.models import User

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def user(db):
    """
    Creates a test user for assigning to recipes and logging in.
    """
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def recipe(user):
    """
    Creates and returns a sample Recipe instance linked to a test user.
    """
    return Recipe.objects.create(
        name="Chocolate Cake",
        description="Rich chocolate flavor",
        cost=10,
        time=45,
        ingredients="Flour, Sugar, Cocoa, Eggs",
        diet="Vegetarian",
        user=user,
        is_public=True,
    )


@pytest.fixture
def recipe_data(user):
    """
    Sample valid POST data for creating a new Recipe instance.
    """
    return {
        "name": "Banana Bread",
        "description": "Sweet and moist",
        "cost": 5,
        "time": 60,
        "ingredients": "Bananas, Flour, Sugar, Eggs",
        "diet": "Vegetarian",
        "user": user.id,
        "is_public": True,
    }


# ----------------------------------------------------------------------
# ListView Tests
# ----------------------------------------------------------------------

def test_recipe_list_view(client, recipe):
    """
    Tests that the recipe list view returns HTTP 200 and contains expected context data.
    """
    url = reverse("recipesns:recipe_list")
    response = client.get(url)

    assert response.status_code == 200
    assert "recipes" in response.context
    assert recipe in response.context["recipes"]


# ----------------------------------------------------------------------
# DetailView Tests
# ----------------------------------------------------------------------

def test_recipe_detail_view(client, recipe):
    """
    Tests that the detail view for a valid recipe returns HTTP 200 and the correct object.
    """
    url = reverse("recipesns:recipe_detail", args=[recipe.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert "specific_recipe" in response.context
    assert response.context["specific_recipe"] == recipe

@pytest.mark.django_db
def test_recipe_detail_view_404(client):
    """
    Ensures the detail view returns HTTP 404 when the recipe does not exist.
    """
    url = reverse("recipesns:recipe_detail", args=[9999])
    response = client.get(url)

    assert response.status_code == 404


# ----------------------------------------------------------------------
# CreateView Tests
# ----------------------------------------------------------------------

@pytest.mark.django_db
def test_recipe_create_view_get(client):
    """
    Tests that the recipe creation form is displayed correctly via GET request.
    """
    url = reverse("recipesns:recipe_create")
    response = client.get(url)

    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_recipe_create_view_post(client, recipe_data):
    """
    Tests POST request to create a new recipe and checks for a successful redirect.
    Simulates an authenticated user.
    """
    url = reverse("recipesns:recipe_create")

    # Authenticate the user
    user = User.objects.get(id=recipe_data["user"])
    client.force_login(user)

    response = client.post(url, data=recipe_data)

    # Verify redirect and database change
    assert response.status_code == 302
    assert Recipe.objects.filter(name="Banana Bread").exists()


# ----------------------------------------------------------------------
# Pagination Test
# ----------------------------------------------------------------------

def test_recipe_list_pagination(client, user):
    """
    Verifies that the recipe list view paginates correctly (6 per page).
    """
    Recipe.objects.bulk_create([
        Recipe(
            name=f"Recipe {i}",
            description="Sample description",
            cost=5,
            time=20,
            ingredients="Sample ingredients",
            diet="None",
            user=user,
            is_public=True
        ) for i in range(10)
    ])

    url = reverse("recipesns:recipe_list")
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context["recipes"]) == 6  # paginate_by = 6


# ----------------------------------------------------------------------
# UpdateView Tests
# ----------------------------------------------------------------------

def test_recipe_update_view_get(client, recipe):
    """
    Tests that the update form loads correctly with the existing recipe data.
    """
    client.force_login(recipe.user)
    url = reverse("recipesns:recipe_update", args=[recipe.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].instance == recipe


def test_recipe_update_view_post(client, recipe):
    """
    Tests that submitting the update form modifies the recipe and redirects.
    """
    client.force_login(recipe.user)
    url = reverse("recipesns:recipe_update", args=[recipe.pk])
    updated_data = {
        "name": "Updated Cake",
        "description": "Even better chocolate cake",
        "cost": 12,
        "time": 50,
        "ingredients": "Cocoa, Sugar, Eggs, Butter",
        "diet": "Vegan",
        "user": recipe.user.id,
        "is_public": True,
    }
    response = client.post(url, updated_data)

    recipe.refresh_from_db()
    assert response.status_code == 302
    assert recipe.name == "Updated Cake"
    assert recipe.description == "Even better chocolate cake"


# ----------------------------------------------------------------------
# DeleteView Tests
# ----------------------------------------------------------------------

def test_recipe_delete_view_get(client, recipe):
    """
    Tests that the delete confirmation page renders correctly.
    """
    client.force_login(recipe.user)
    url = reverse("recipesns:recipe_delete", args=[recipe.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert "object" in response.context
    assert response.context["object"] == recipe


def test_recipe_delete_view_post(client, recipe):
    """
    Tests that submitting the delete form removes the recipe.
    """
    client.force_login(recipe.user)
    url = reverse("recipesns:recipe_delete", args=[recipe.pk])
    response = client.post(url)

    assert response.status_code == 302
    assert not Recipe.objects.filter(pk=recipe.pk).exists()


# ----------------------------------------------------------------------
# RecipeTableView (Sortable ListView) Tests
# ----------------------------------------------------------------------

def test_recipe_table_view_default_sort(client, user):
    """
    Tests default sorting behavior (by cost ascending).
    """
    Recipe.objects.create(name="Zebra Cake", description="desc", cost=15, time=10,
                          ingredients="...", diet="None", user=user, is_public=True)
    Recipe.objects.create(name="Apple Pie", description="desc", cost=5, time=15,
                          ingredients="...", diet="None", user=user, is_public=True)

    url = reverse("recipesns:recipe_table")
    response = client.get(url)

    assert response.status_code == 200
    recipes = list(response.context["recipes"])
    assert recipes[0].cost <= recipes[1].cost  # ascending by default


def test_recipe_table_view_custom_sort(client, user):
    """
    Tests sorting behavior when using query parameters (?sort=name&dir=desc).
    """
    Recipe.objects.create(name="Apple Pie", description="desc", cost=5, time=15,
                          ingredients="...", diet="None", user=user, is_public=True)
    Recipe.objects.create(name="Zebra Cake", description="desc", cost=10, time=10,
                          ingredients="...", diet="None", user=user, is_public=True)

    url = reverse("recipesns:recipe_table") + "?sort=name&dir=desc"
    response = client.get(url)

    assert response.status_code == 200
    recipes = list(response.context["recipes"])
    assert recipes[0].name > recipes[1].name  # descending order

    # Confirm context includes sort state
    assert response.context["current_sort"] == "name"
    assert response.context["current_dir"] == "desc"
