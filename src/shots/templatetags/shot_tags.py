from django import template
from shots.choice import STATUS_CHOICES

register = template.Library()


@register.simple_tag
def get_status_choices():
    return STATUS_CHOICES
