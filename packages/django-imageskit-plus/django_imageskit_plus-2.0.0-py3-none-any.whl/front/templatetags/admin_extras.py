from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    """Получить атрибут объекта по имени"""
    return getattr(obj, attr_name, '')

@register.filter
def is_image(value):
    """Проверить, является ли значение изображением"""
    return hasattr(value, 'url')