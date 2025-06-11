from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import RecipeForm
from .models import Recipe
from django.urls import reverse_lazy

# Create your views here.

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 4

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'specific_recipe'

class RecipeCreateView(CreateView):
    model = Recipe
    template_name = 'recipes/recipe_create_update.html'
    form_class = RecipeForm
    success_url = reverse_lazy('recipesns:recipe_list')


class RecipeUpdateView(UpdateView):
    model = Recipe
    template_name = 'recipes/recipe_create_update.html'
    form_class = RecipeForm
    success_url = reverse_lazy('recipesns:recipe_list')

class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = 'recipes/recipe_delete.html'
    success_url = reverse_lazy('recipesns:recipe_list')