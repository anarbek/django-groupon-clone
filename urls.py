from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Index page
    url(r'^$', 'engine.views.index', name='index'),

    # Checkout urls
    url(r'^deals/groupon-clone/(?P<slug>\S+)/checkout/$', 'engine.views.deal_checkout', name='deal-checkout'),
    url(r'^deals/(?P<slug>\S+)/(?P<quantity>\d+)/checkout/complete/$', 'engine.views.deal_checkout_complete', name='deal-checkout-complete'),
    url(r'^checkout/error$', 'engine.views.deal_checkout_error', name='deal-checkout-error'),
    url(r'^deals/groupon-clone/(?P<slug>\S+)/$', 'engine.views.deal_detail', name='deal-detail'),
    
    url(r'^(?P<city_slug>\S+)/subscribe$', 'engine.views.city_subscribe', name='city-subscribe'),
    url(r'^deals/(?P<city_slug>\w+)$', 'engine.views.city_deals', name='city-deals'),

    url(r'^deals/groupon-clone/$', 'engine.views.deal_detail', name='todays-deal'),
    # FIXME: implement recent deals
    url(r'^deals/groupon-clone/$', 'engine.views.deal_detail', name='recent-deals'),
    
    url(r'^suggestions$', 'engine.views.suggestions', name='suggestions'),

    # Login/logout
    url(r'^user/signup/$', 'engine.views.user_signup', name='user-signup'),
    url(r'^user/login/$', 'engine.views.user_login', name='user-login'),
    url(r'^user/logout/$', 'engine.views.user_logout', name='user_logout'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url(r'^adminmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PATH_ADMINMEDIA}),

    url('^setup/$', 'socialregistration.views.setup', name='socialregistration_setup'),

    url('^logout/$', 'socialregistration.views.logout', name='social_logout'),

    # Static stuff (apache should serve this in production)
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
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
