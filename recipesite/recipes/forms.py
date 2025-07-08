from django import forms
from .models import Recipe

# Custom class for creating and editing Recipe objects
class RecipeForm(forms.ModelForm):
    class Meta:
        # The model to build the form for
        model = Recipe
        # Which form fields will be included in the form
        exclude = ['user', 'created_at']