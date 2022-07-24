from django import template

register = template.Library()

@register.filter(name='show_error')
def show_error(dictionary):
    try:
        print(dictionary.values())
        return list(dictionary.values())[0][0]
    except (TypeError, IndexError, AttributeError):
        return ''

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)