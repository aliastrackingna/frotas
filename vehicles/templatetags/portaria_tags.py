from django import template

register = template.Library()

@register.simple_tag
def get_registro(registros, viagem_id):
    return registros.get(viagem_id)