import pytest
from django.urls import reverse
from django.test import Client
from recipes.models import Recipe
from django.contrib.auth.models import User

# ---------- Fixtures for test setup ----------

@pytest.fixture
def client():
    """
    Returns a Django test client for simulating HTTP requests.
    """
    return Client()

@pytest.fixture
def user(db):
    """
    Creates and returns a standard test user.
    """
    return User.objects.create_user(username='testuser', password='password')

@pytest.fixture
def other_user(db):
    """
    Creates a second user for ownership/permission testing.
    """
    return User.objects.create_user(username='otheruser', password='password')

@pytest.fixture
def recipe(db, user):
    """
    Creates a public Recipe object owned by 'testuser'.
    """
    return Recipe.objects.create(
        name="Test Recipe",
        description="A simple test recipe.",
        cost=10,
        time=15,
        ingredients="Eggs, Flour, Sugar",
        diet="Vegetarian",
        user=user,
        is_public=True
    )

@pytest.fixture
def private_recipe(db, user):
    """
    Creates a non-public Recipe object for visibility tests.
    """
    return Recipe.objects.create(
        name="Private Recipe",
        description="A hidden test recipe.",
        cost=20,
        time=30,
        ingredients="Milk, Butter, Chocolate",
        diet="Gluten-Free",
        user=user,
        is_public=False
    )

# ---------- URL Tests ----------

@pytest.mark.django_db
def test_recipe_list_url(client):
    """
    Ensures the recipe list view returns HTTP 200.
    Assumes it filters or displays public recipes.
    """
    url = reverse('recipesns:recipe_list')
    response = client.get(url)
    assert response.status_code == 200

def test_recipe_detail_public_recipe(client, recipe):
    """
    Confirms a public recipe detail page is accessible.
    """
    url = reverse('recipesns:recipe_detail', args=[recipe.pk])
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.xfail(reason="Access control not implemented yet")
def test_recipe_detail_private_recipe_unauthorized(client, private_recipe):
    """
    Verifies that a private recipe is not accessible by anonymous users.
    Expecting 404 or redirect depending on view logic.
    """
    url = reverse('recipesns:recipe_detail', args=[private_recipe.pk])
    response = client.get(url)
    assert response.status_code in [403, 404]

def test_recipe_create_url_authenticated(client, user):
    """
    Confirms that an authenticated user can access the recipe creation view.
    """
    client.login(username='testuser', password='password')
    url = reverse('recipesns:recipe_create')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.xfail(reason="Access control not implemented yet")
def test_recipe_create_url_unauthenticated(client):
    """
    Verifies that unauthenticated users are redirected when trying to access the create view.
    """
    url = reverse('recipesns:recipe_create')
    response = client.get(url)
    assert response.status_code == 302  # Redirect to login


def test_recipe_update_owner(client, recipe, user):
    """
    Checks that the recipe owner can access the update view.
    """
    client.login(username='testuser', password='password')
    url = reverse('recipesns:recipe_update', args=[recipe.pk])
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.xfail(reason="Access control not implemented yet")
def test_recipe_update_non_owner(client, recipe, other_user):
    """
    Ensures that a different user cannot access the update view of someone else's recipe.
    """
    client.login(username='otheruser', password='password')
    url = reverse('recipesns:recipe_update', args=[recipe.pk])
    response = client.get(url)
    assert response.status_code in [403, 404]

def test_recipe_delete_owner(client, recipe, user):
    """
    Confirms that the recipe owner can access the delete view.
    """
    client.login(username='testuser', password='password')
    url = reverse('recipesns:recipe_delete', args=[recipe.pk])
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.xfail(reason="Access control not implemented yet")
def test_recipe_delete_non_owner(client, recipe, other_user):
    """
    Ensures that unauthorized users cannot access the delete view.
    """
    client.login(username='otheruser', password='password')
    url = reverse('recipesns:recipe_delete', args=[recipe.pk])
    response = client.get(url)
    assert response.status_code in [403, 404]

@pytest.mark.django_db
def test_recipe_table_view(client):
    """
    Confirms that the custom recipe table view returns a 200 response.
    """
    url = reverse('recipesns:recipe_table')
    response = client.get(url)
    assert response.status_code == 200
