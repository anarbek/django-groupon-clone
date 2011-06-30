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
    url(r'^user/signup/$', 'engine.views.user_signup', name='user_signup'),
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

"""
Created on 22.09.2009
Updated on 19.12.2009

@author: alen, pinda
"""

# Setup Facebook URLs if there's an API key specified
if getattr(settings, 'FACEBOOK_API_KEY', None) is not None:
    urlpatterns = urlpatterns + patterns('',
        url('^facebook/login/$', 'socialregistration.views.facebook_login',
            name='facebook_login'),

        url('^facebook/connect/$', 'socialregistration.views.facebook_connect',
            name='facebook_connect'),

        url('^xd_receiver.htm', 'django.views.generic.simple.direct_to_template',
            {'template':'socialregistration/xd_receiver.html'},
            name='facebook_xd_receiver'),
    )

#Setup Twitter URLs if there's an API key specified
if getattr(settings, 'TWITTER_CONSUMER_KEY', None) is not None:
    urlpatterns = urlpatterns + patterns('',
        url('^twitter/redirect/$', 'socialregistration.views.oauth_redirect',
            dict(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                secret_key=settings.TWITTER_CONSUMER_SECRET_KEY,
                request_token_url=settings.TWITTER_REQUEST_TOKEN_URL,
                access_token_url=settings.TWITTER_ACCESS_TOKEN_URL,
                authorization_url=settings.TWITTER_AUTHORIZATION_URL,
                callback_url='twitter_callback'
            ),
            name='twitter_redirect'),

        url('^twitter/callback/$', 'socialregistration.views.oauth_callback',
            dict(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                secret_key=settings.TWITTER_CONSUMER_SECRET_KEY,
                request_token_url=settings.TWITTER_REQUEST_TOKEN_URL,
                access_token_url=settings.TWITTER_ACCESS_TOKEN_URL,
                authorization_url=settings.TWITTER_AUTHORIZATION_URL,
                callback_url='twitter'
            ),
            name='twitter_callback'
        ),
        url('^twitter/$', 'socialregistration.views.twitter', name='twitter'),
    )

# Setup FriendFeed URLs if there's an API key specified
if getattr(settings, 'FRIENDFEED_CONSUMER_KEY', None) is not None:
    urlpatterns = urlpatterns + patterns('',
        url('^friendfeed/redirect/$', 'socialregistration.views.oauth_redirect',
            dict(
                consumer_key=settings.FRIENDFEED_CONSUMER_KEY,
                secret_key=settings.FRIENDFEED_CONSUMER_SECRET_KEY,
                request_token_url=settings.FRIENDFEED_REQUEST_TOKEN_URL,
                access_token_url=settings.FRIENDFEED_ACCESS_TOKEN_URL,
                authorization_url=settings.FRIENDFEED_AUTHORIZATION_URL,
                callback_url='friendfeed_callback'
            ),
            name='friendfeed_redirect'),

        url('^friendfeed/callback/$', 'socialregistration.views.oauth_callback',
            dict(
                consumer_key=settings.FRIENDFEED_CONSUMER_KEY,
                secret_key=settings.FRIENDFEED_CONSUMER_SECRET_KEY,
                request_token_url=settings.FRIENDFEED_REQUEST_TOKEN_URL,
                access_token_url=settings.FRIENDFEED_ACCESS_TOKEN_URL,
                authorization_url=settings.FRIENDFEED_AUTHORIZATION_URL,
                callback_url='friendfeed'
            ),
            name='friendfeed_callback'
        ),
        url('^friendfeed/$', 'socialregistration.views.friendfeed', name='friendfeed'),
    )

urlpatterns = urlpatterns + patterns('',
    url('^openid/redirect/$', 'socialregistration.views.openid_redirect', name='openid_redirect'),
    url('^openid/callback/$', 'socialregistration.views.openid_callback', name='openid_callback')
)
