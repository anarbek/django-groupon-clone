from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
urlpatterns = patterns('',
    # Index page
    url(r'^$', 'engine.views.index', name='index'),

    # Checkout urls
    url(r'^deals/(?P<slug>\S+)/checkout/$', 'engine.views.deal_checkout', name='deal-checkout'),
    url(r'^deals/(?P<slug>\S+)/(?P<quantity>\d+)/checkout/complete/$', 'engine.views.deal_checkout_complete', name='deal-checkout-complete'),
    url(r'^checkout/error$', 'engine.views.deal_checkout_error', name='deal-checkout-error'),
    url(r'^deals/(?P<slug>\S+)$', 'engine.views.deal_detail', name='deal-detail'),
    
    url(r'^deals$', 'engine.views.deal_detail', name='todays-deal'),
    # FIXME: implement recent deals
    url(r'^deals$', 'engine.views.deal_detail', name='recent-deals'),
    url(r'^(?P<city_slug>\S+)/subscribe$', 'engine.views.city_subscribe', name='city-subscribe'),
    url(r'^(?P<city_slug>\w+)$', 'engine.views.city_deals', name='city-deals'),
    
    url(r'^suggestions$', 'engine.views.suggestions', name='suggestions'),

    # User pages
    url(r'^user/myaccount$', 'engine.views.myaccount', name='my-account'),
    url(r'^users/new', 'engine.views.user_signup', name='user-signup'),
#    url(r'users/(?P<username>/w+)/pages..')
#    url(r'^login$', 'engine.views.user_login', name='user-login'),
    url(r'^user/logout$', 'django.contrib.auth.views.logout', name='user-logout'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^social/', include('socialregistration.urls')),
    
    #FIXME: robots.txt wil not work like this
    (r'^(robots.txt)$', 'django.views.static.serve', {'document_root': '/var/www/massivecoupon/'}),
)

# Flatpages url
urlpatterns+= patterns('django.contrib.flatpages.views',
    url(r'^about-us/$', 'flatpage', {'url': '/about-us/'}, name='about-us'),
    url(r'^contact-us/$', 'flatpage', {'url': '/contact-us/'}, name='contact-us'),
    url(r'^how-coupon-works/$', 'flatpage', {'url': '/how-coupon-works/'}, name='howitworks'),
    url(r'^terms-and-conditions/$', 'flatpage', {'url': '/terms/'}, name='terms'),
    url(r'^faq/$', 'flatpage', {'url': '/faq/'}, name='faq'),
    url(r'^press/$', 'flatpage', {'url': '/press/'}, name='press'),
)

# Add static files
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )