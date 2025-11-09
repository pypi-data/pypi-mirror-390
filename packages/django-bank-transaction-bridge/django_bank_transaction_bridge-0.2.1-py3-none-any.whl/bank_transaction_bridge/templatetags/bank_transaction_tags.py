from django import template


register = template.Library()


@register.simple_tag
def update_current_query(request, **kwargs):
    query = request.GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return f"{request.path}?{query.urlencode()}" if query else request.path
