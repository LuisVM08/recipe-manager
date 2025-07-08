from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import RecipeForm
from .models import Recipe
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 6

    # Order the queryset by the most recent first
    def get_queryset(self):
        return Recipe.objects.order_by('-created_at')

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

class RecipeTableView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_table.html'
    context_object_name = 'recipes'

    # Defines what the data will be used as the main object in the template
    def get_queryset(self):
        sort_by = self.request.GET.get('sort', 'cost')
        direction = self.request.GET.get('dir', 'asc')
        valid_fields = ['name', 'description', 'cost', 'time', 'is_public']

        if sort_by not in valid_fields:
            sort_by = 'cost'

        order = sort_by if direction == 'asc' else f"-{sort_by}"
        return Recipe.objects.order_by(order)

    # Override to make get_context_data to include sort state in template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'name')
        context['current_dir'] = self.request.GET.get('dir', 'asc')
        return context


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

