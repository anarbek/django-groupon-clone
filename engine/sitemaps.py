'''
Created on Jul 3, 2011

@author: madalinoprea
'''
from django.contrib.sitemaps import Sitemap
from engine.models import Deal

class DealSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    
    def items(self):
        return Deal.objects.filter(is_deal_on=True)
    
    def lastmod(self, obj):
        return obj.last_mod