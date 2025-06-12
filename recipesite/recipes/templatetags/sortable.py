from django import template
from django.utils.html import format_html
from urllib.parse import urlencode

# registers template tag file with Django. This must be done in every file that has custom template to define it
register = template.Library()

# Decorator that tells Django that the function is a simple tag you can use in templates like
@register.simple_tag
def sortable_column(field, label, current_sort=None, current_dir='asc'):
    toggle_dir = 'desc' if current_sort == field and current_dir == 'asc' else 'asc'
    arrow = ''
    if current_sort == field:
        arrow = '↑' if current_dir == 'asc' else '↓'

    # Builds a URL query string like ?sort=cost%dir=desc. Clicking the column will reload the page with this sort
    # direction
    query_string = urlencode({'sort': field, 'dir': toggle_dir})

    # returns a clickable <a> tag
    return format_html('<a href="?{}">{} {}</a>', query_string, label, arrow)