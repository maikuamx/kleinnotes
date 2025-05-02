from django import template

register = template.Library()

@register.filter
def get_choice_display(obj, field_name):
    """
    Returns the display value for a choice field
    Usage: {{ object|get_choice_display:"field_name" }}
    """
    choices = {
        'N': 'Nunca',
        'P': 'Pasado',
        'A': 'Presente'
    }
    value = getattr(obj, field_name, '')
    return choices.get(value, value)