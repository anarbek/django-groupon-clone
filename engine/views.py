from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from paypalxpress.driver import PayPal
from paypalxpress.models import PayPalResponse

import datetime
import logging
from urllib import quote

from mario.utils import render_to

from engine.models import City, EmailSubscribe, Coupon, STATUS_ACTIVE, Deal,\
    STATUS_ONHOLD
from engine.forms import SignupForm, LoginForm, EmailSubForm, DealCheckoutForm

@login_required
@render_to('myaccount.html')
def myaccount(request):
    return {'coupons': request.user.coupon_set.all()}

def user_signup(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SignupForm(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            user = User()
            user.username = cd.get('email')  #str(uuid.uuid4())[:30]
            user.first_name = cd.get('full_name')
            user.email = cd.get('email')
            user.save() #FIXME: why save twice
            user.set_password(cd.get('password'))
            user.save()
            
            user = authenticate(username=user.username, password=cd.get('password'))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to a success page.
                else:
                    messages.add_message(request, messages.ERROR, "User %s is disabled. Please contact us." % user.username)
                # Return a 'disabled account' error message
            else:
                messages.add_message(request, messages.ERROR, "Unable to authenticate.")
            
            return HttpResponseRedirect(reverse('index'))
    else:
        initial_data = {}
        form = SignupForm(initial=initial_data)
            
    return render_to_response('user_signup.html', 
                              {
                               'form' : form,
                               }, 
                              context_instance=RequestContext(request))


@render_to('email_subscribe.html')
def city_subscribe(request, city_slug):
    try:
        city = City.objects.get(slug=city_slug)
    except:
        messages.error(request, _('Cannot request subscription for a non existent city.'))
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'POST': # If the form has been submitted...
        form = EmailSubForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Thanks for subscribing!'))
            return HttpResponseRedirect(reverse('index'))
    else:
        initial_data = { 'city': city.id, 'email': 'E.g. you@domain.com' }
        form = EmailSubForm(initial=initial_data)
    
    return {'city' : city, 'form' : form}


def index(request):
    return HttpResponseRedirect(reverse('todays-deal'))

def _debug_checkout_complete(request, deal, quantity):
    return {'error': False}

def _paypal_checkout_complete(request, deal, quantity, token):
    result = {'error': True}
    token = request.GET.get('token', None)
    payerid = request.GET.get('PayerID', None)
    
    if token and payerid:
        # TODO: i have no idea how many they bought!
        p = PayPal()
        rc = p.DoExpressCheckoutPayment("CAD", quantity * deal.deal_price, token, payerid, PAYMENTACTION="Authorization")
        if rc:  # payment is looking good
            response = PayPalResponse()
            response.fill_from_response(p.GetPaymentResponse())
            response.status = PayPalResponse.get_default_status()
            response.save()
            result['error'] = False
        else:
            result['message'] = 'Empty payment'
    else:
        result['message']= 'Token or payerid are empty.'


def deal_checkout_complete(request, slug, quantity):
    quantity = int(quantity)
    deal = get_object_or_404(Deal, slug=slug)
    result = None
    
    # TODO: Check if we can deliver requested quantity
    
    if settings.DEBUG:
        result = _debug_checkout_complete(request, deal, quantity)
    else:
        result = _paypal_checkout_complete(request, deal, quantity)
    
    if result['error']:
        # FIXME: add error processing
        messages.error(request, "Unable to complete checkout: %s" % result['message'])
        return HttpResponseRedirect(reverse(''))
    
    # FIXME: Checkout code needs to be reviewed
    if deal.is_deal_on:
        num_sold = deal.num_sold()
        #FIXME: Transactions
        for i in range(quantity):
            coupon = Coupon()
            coupon.user = request.user
            coupon.deal = deal
            coupon.status = STATUS_ONHOLD
            coupon.save()
            num_sold = num_sold + 1
            
            # update the deal object 
            if num_sold >= deal.tipping_point:
                deal.tipped_at = datetime.datetime.now()
                deal.is_deal_on = True
                deal.save()
        messages.success(request, "Thanks for purchasing a %s coupons for %s! It will arrive in your profile within 24 hours." %
                         (quantity, deal.title))
    else:
        messages.error(request, 'Deal is closed now. You cannot complete checkout.')
    
    return HttpResponseRedirect(reverse('index'))


def _checkout(deal, quantity):
    if settings.DEBUG:
        return {'error': False, 'redirect_url': reverse('deal-checkout-complete', args=(deal.slug, quantity))}
        
    # FIXME: I need to remove hardcodings
    total_price = quantity * deal.deal_price
    p = PayPal()
    rc = p.SetExpressCheckout(total_price, "CAD", "http://www.massivecoupon.com/deals/" + deal.slug + "/" + str(quantity) + "/checkout/complete/", "http://www.massivecoupon.com/", PAYMENTACTION="Authorization")
    if rc:
        token = p.api_response['TOKEN'][0]
        return {'error': False, 'redirect_url': p.paypal_url()}
    else:
        return {'error': True, 'redirect_url': reverse('deal-checkout-error')}

@render_to('deal_checkout.html')
def deal_checkout(request, slug):
    '''
    FIXME: Clean this mess
    
    @param request:
    @param slug: deal slug
    '''
    try:
        deal = Deal.objects.get(slug=slug)
    except:
        messages.error(request, _('Cannot load requested deal.'))
        return HttpResponseRedirect('/')
    
    must_login_error = False
    must_login_email = None
    user = None
    form = None

    if request.method == 'POST': # If the form has been submitted...
        # try create user
        if request.user.is_authenticated():
            user = request.user
        else:
            form = DealCheckoutForm(request.POST)
            if form.is_valid():
                try:
                    # FIXME: use form's cleaned_data not raw POST
                    user = User.objects.get(email=form.cleaned_data['email'])
                    must_login_error = True
                    must_login_email = request.POST['email']
                    form = DealCheckoutForm(initial={})
                    user_msg = 'An account already exists for ' + user.email + '. Please sign in first.'
                    
                    user = User()
                    user.username = form.cleaned_data['email']  #str(uuid.uuid4())[:30]
                    user.first_name = form.cleaned_data['full_name']
                    user.email = form.cleaned_data['email']
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    
                    user = authenticate(username=user.username, password=form.cleaned_data['password'])
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                        else:
                            messages.add_message(request, messages.ERROR, "Unable to login with these credentails.")
                            user = None
                            # Return a 'disabled account' error message
                    else:
                        messages.add_message(request, messages.ERROR, "Cannot create/auth user.")
                        # Return an 'invalid login' error message.
                        pass
                except Exception, e:
                    logging.warning("Exception: %s" % e)
                    user = None
            else:
                user = None
                logging.warning("Invalid form")

        # If we have a current user now (already authenticated)
        if user:
            # TODO: check if requested quantity can be purchased
            try:
                quantity = int(request.POST.get('quantity', 0))
            except Exception:
                quantity = 0
            if quantity:
                # Perform checkout  
                result = _checkout(deal, quantity)
                if result['error']:
                    logging.error("Checkout error %s: %s" % (slug, result))
                else:
                    logging.error("Checkout success")
                if result['redirect_url']:
                    return HttpResponseRedirect(result['redirect_url'])
                else:
                    # This should never happen
                    messages.error(request, _('Unable to perform checkout. Please consult our support team.'))
                    return HttpResponseRedirect(reverse('index'))
            else:
                #unable to checkout selected quantity
                messages.error(request, _('Selected quantity is not valid. Please correct quantity.'))
    else:
        form = DealCheckoutForm(initial={})
        
    return {'form' : form,
            'deal' : deal,
            'must_login_error' : must_login_error,
            'must_login_email' : must_login_email,
            'city': deal.city
            }

def deal_checkout_error(request):
    # TODO: Implement checkout error
    return HttpResponse("Deal Checkout Error")


@render_to('deal_detail.html')
def deal_detail(request, slug=None):
    if slug == None:
        deal = Deal.objects.all()[0]
    else:
        deal = get_object_or_404(Deal, slug=slug)
    
    if not deal.is_expired(): 
        countdown_time = deal.date_published.strftime("%Y,%m,%d") #+ ' 11:59 PM'
    else:
        countdown_time = -1
    
    return {'deal' : deal, 'countdown_time' : countdown_time}


@render_to('deal_detail.html')
def city_deals(request, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    deals = city.deal_set.all()
    countdown_time = -1
    deal = None
    if len(deals):
        deal = deals[0]
        if not deal.is_expired(): 
            countdown_time = deal.date_published.strftime("%Y,%m,%d") #+ ' 11:59 PM'
    else:
        messages.error(request, _('There are no open deals opened for city %(city)s.') % {'city': city.name})
        return HttpResponseRedirect(reverse('index'))
    
    return {'deal' : deal, 'countdown_time' : countdown_time, 'city': city}


#TODO: Implement suggestions / suggest a business
def suggestions(request):
    return HttpResponse('Suggestions')
