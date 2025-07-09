from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import RecipeForm
from .models import Recipe
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
import requests
from django.conf import settings
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

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        else:
            form.instance.user = None  # Explicitly set None, or just omit this line
        return super().form_valid(form)


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

def autofill_recipe(request):
    name = request.GET.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False})

    api_key = settings.SPOONACULAR_API_KEY
    search_url = 'https://api.spoonacular.com/recipes/complexSearch'
    info_url_template = 'https://api.spoonacular.com/recipes/{id}/information'

    try:
        # Step 1: Search for recipes by name
        search_params = {
            'apiKey': api_key,
            'query': name,
            'number': 1,
        }
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data['results']:
            return JsonResponse({'success': False})

        recipe_id = search_data['results'][0]['id']

        # Step 2: Get recipe details
        info_url = info_url_template.format(id=recipe_id)
        info_params = {
            'apiKey': api_key,
            'includeNutrition': False
        }
        info_response = requests.get(info_url, params=info_params)
        info_response.raise_for_status()
        info_data = info_response.json()

        # Extract fields
        description = info_data.get('summary', '')
        ingredients = ', '.join(
            [ingredient['original'] for ingredient in info_data.get('extendedIngredients', [])]
        )
        time = info_data.get('readyInMinutes', 0)
        cost = round(info_data.get('pricePerServing', 0) / 100)  # Convert cents to dollars (rough estimate)

        return JsonResponse({
            'success': True,
            'description': description,
            'ingredients': ingredients,
            'time': time,
            'cost': cost
        })

    except Exception as e:
        print('Error during Spoonacular API call:', e)
        return JsonResponse({'success': False})