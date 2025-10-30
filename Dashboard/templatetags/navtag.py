from django import template

register = template.Library()


@register.inclusion_tag('dashboard/partials/side-nav.html', takes_context=True)
def show_side_nav(context, string):
    cat = string.split('-')[0]
    current = "-".join(string.split('-')[1:])

    return {'cat': cat, 'current': current}
