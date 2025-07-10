from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import RecipeForm
from .models import Recipe
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
import re
from html import unescape
import requests
from django.conf import settings
from django.db import models
from django.http import Http404

# Create your views here.

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 6

    # Order the queryset by the most recent first
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.filter(
                models.Q(is_public=True) | models.Q(user=self.request.user)
            ).order_by('-created_at')
        else:
            return Recipe.objects.filter(is_public=True).order_by('-created_at')


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'specific_recipe'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_public and obj.user != self.request.user:
            raise Http404("Recipe not found.")
        return obj

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

        base_qs = Recipe.objects.all()
        if self.request.user.is_authenticated:
            base_qs = base_qs.filter(
                models.Q(is_public=True) | models.Q(user=self.request.user)
            )
        else:
            base_qs = base_qs.filter(is_public=True)

        return base_qs.order_by(order)

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

# Basic list of common ingredients (expand as needed)
COMMON_INGREDIENTS = [
    'chicken', 'beef', 'pork', 'tofu', 'salmon', 'shrimp',
    'rice', 'beans', 'cheese', 'potato', 'egg', 'tomato',
    'lettuce', 'onion', 'garlic', 'carrot', 'broccoli',
    'spinach', 'mushroom', 'pepper', 'bacon', 'turkey',
    'chocolate', 'strawberry', 'banana', 'apple'
]

def extract_known_ingredient(query):
    query_lower = query.lower()
    for ingredient in COMMON_INGREDIENTS:
        if ingredient in query_lower:
            return ingredient
    return None

def clean_html(text):
    text = unescape(text)
    return re.sub('<[^<]+?>', '', text)  # Remove HTML tags

def autofill_recipe(request):
    name = request.GET.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False})

    api_key = settings.SPOONACULAR_API_KEY
    ingredient = extract_known_ingredient(name)

    search_params = {
        'apiKey': api_key,
        'query': name,
        'number': 3,
        'instructionsRequired': True,
    }
    if ingredient:
        search_params['titleMatch'] = ingredient

    try:
        # Step 1: Search for recipes
        search_response = requests.get('https://api.spoonacular.com/recipes/complexSearch', params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data['results']:
            return JsonResponse({'success': False})

        # Step 2: Try up to 3 recipes for a good match
        for result in search_data['results']:
            recipe_id = result['id']
            info_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
            info_params = { 'apiKey': api_key, 'includeNutrition': False }

            info_response = requests.get(info_url, params=info_params)
            info_response.raise_for_status()
            info_data = info_response.json()

            description = clean_html(info_data.get('summary', ''))
            ingredients = ', '.join(
                [i['original'] for i in info_data.get('extendedIngredients', [])]
            )
            time = info_data.get('readyInMinutes', 0)
            cost = round(info_data.get('pricePerServing', 0) / 100)

            if ingredients:
                return JsonResponse({
                    'success': True,
                    'description': description,
                    'ingredients': ingredients,
                    'time': time,
                    'cost': cost
                })

        return JsonResponse({'success': False})

    except Exception as e:
        print('Spoonacular error:', e)
        return JsonResponse({'success': False})