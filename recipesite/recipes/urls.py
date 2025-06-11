from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'recipesns'

urlpatterns = [
    path('', views.RecipeListView.as_view(), name='recipe_list'),
    path('<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
]
