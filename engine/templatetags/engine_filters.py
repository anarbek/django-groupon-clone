'''
Created on Jul 2, 2011

@author: madalinoprea
'''
from django import template
import locale

register = template.Library()

@register.filter(name='currency')
def currency(value):
    loc = locale.localeconv()
    
    return locale.currency(value, loc['currency_symbol'], grouping=True)