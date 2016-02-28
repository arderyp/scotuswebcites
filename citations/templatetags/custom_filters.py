from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def yyyymmdd(date):
    return date.strftime("%Y.%m.%d")
