from django import template
from engine.models import City

register = template.Library()

@register.inclusion_tag('engine/_city_slider.html')
def show_city_slider():
    cities = City.objects.all().filter(is_active=True).order_by('order')
    return {'cities': cities}
