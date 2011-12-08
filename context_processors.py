'''
Created on Jun 28, 2011

@author: madalinoprea
'''

from django.conf import settings
from django.contrib.sites.models import Site
from engine.models import City

def exposed_settings(request):
    try:
        city = City.objects.get(pk=settings.DEFAULT_CITY)
    except:
        city = "";
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'WEBSITE_TITLE': settings.WEBSITE_TITLE,
        'WEBSITE_URL': settings.WEBSITE_URL,
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'COMPANY_EMAIL_INFO': settings.COMPANY_EMAIL_INFO,
        'FACEBOOK_API_KEY': settings.FACEBOOK_API_KEY,
        'CURRENT_SITE': Site.objects.get_current(),
        'city': city,
        }
    
