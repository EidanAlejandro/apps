# requests/templatetags/dict_filters.py
from django import template
register = template.Library()

@register.filter(name='get_item') # Le damos un nombre al filtro
def get_item(dictionary, key):
    """ Permite acceder a un diccionario usando una variable como clave en templates """
    if isinstance(dictionary, dict): # Asegurarse que es un diccionario
        return dictionary.get(key)
    return None # Devolver None si no es un diccionario o la clave no existe