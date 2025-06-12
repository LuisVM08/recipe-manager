from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'recipesns'

urlpatterns = [
    path('', views.RecipeListView.as_view(), name='recipe_list'),
    path('<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('create/', views.RecipeCreateView.as_view(), name='recipe_create'),
    path('<int:pk>/update/', views.RecipeUpdateView.as_view(), name='recipe_update'),
    path('<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('table/', views.RecipeTableView.as_view(), name='recipe_table'),
]
