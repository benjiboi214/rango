from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/cats.html', takes_context=True)
def get_category_list(context):
    if 'category' in context:
        return {'cats': Category.objects.all(), 'act_cat': context['category']}
    else:
        return {'cats': Category.objects.all(), 'act_cat': None}