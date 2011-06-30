
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from paypalxpress.driver import PayPal
from paypalxpress.models import PayPalResponse

import datetime
import logging
from urllib import quote

from engine.models import City, EmailSubscribe, Coupon, STATUS_ACTIVE, Deal,\
    STATUS_ONHOLD
from engine.forms import SignupForm, LoginForm, EmailSubForm, DealCheckoutForm


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
            
            return HttpResponseRedirect('/')
    else:
        initial_data = {}
        form = SignupForm(initial=initial_data)
            
    return render_to_response('user_signup.html', 
                              {
                               'form' : form,
                               }, 
                              context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_login(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST)
        
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return HttpResponseRedirect('/')
    else:
        initial_data = {}
        form = LoginForm(initial=initial_data)
            
    return render_to_response('user_login.html', {
                'form' : form,
              }, context_instance=RequestContext(request))

    
def city_subscribe(request, city_slug):
    try:
        city = City.objects.get(slug=city_slug)
    except:
        return HttpResponseRedirect('/deals/groupon-clone/')
    
    if request.method == 'POST': # If the form has been submitted...
        form = EmailSubForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            esub = EmailSubscribe()
            esub.email = cd.get('email')
            ecity = City.objects.get(id=int(cd.get('city')))
            esub.city = ecity
            esub.save()
            
            user_msg = "Thanks for subscribing!"
            messages.add_message(request, messages.SUCCESS, user_msg)
            return HttpResponseRedirect(reverse('index'))
        else:
            initial_data = { 'city': city.id }
            form = EmailSubForm(initial=initial_data)
    
    return render_to_response('email_subscribe.html', {
                'city' : city,
                'form' : form,
              }, context_instance=RequestContext(request))


@login_required
def profile(request):
    coupons = Coupon.objects.filter(user=request.user, status=STATUS_ACTIVE)

#@login_required  # unlock to make fb work!!
def index(request):
    try:
        user_msg = request.GET.get('user_msg', None)
    except:
        user_msg = None
    
    if user_msg:
        return HttpResponseRedirect('/deals/groupon-clone/?user_msg=' + user_msg)
    else:
        return HttpResponseRedirect('/deals/groupon-clone/')


#  return render_to_response('index.html', {
#             #   'now' : now,
#              }, context_instance=RequestContext( request ) )


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


def deal_checkout(request, slug):
    user_msg = ""
    try:
        deal = Deal.objects.get(slug=slug)
    except:
        return HttpResponseRedirect('/')
    must_login_error = False
    must_login_email = None
    user = None

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
            quantity = request.POST.get('quantity', 0)
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
                    messages.add_message(request, messages.ERROR, "Unable to perform checkout. Please consult our support team.")
                    return HttpResponseRedirect(reverse('index'))
            else:
                #unable to checkout selected quantity
                messages.add_message(request, messages.ERROR, "Unable to checkout specified quantity.")
    else:
        logging.warning('Create form')
        initial_data = {}
        form = DealCheckoutForm(initial=initial_data)
        
    return render_to_response('deal_checkout.html', {
                'form' : form,
                'deal' : deal,
                'user_msg' : user_msg,
                'must_login_error' : must_login_error,
                'must_login_email' : must_login_email,
              }, context_instance=RequestContext(request))


def deal_checkout_error(request):
    # TODO: Implement checkout error
    return HttpResponse("Deal Checkout Error")


def deal_detail(request, slug=None):
    try:
        user_msg = request.GET.get('user_msg', None)
    except:
        user_msg = None
    
    if slug == None:
        deal = Deal.objects.all()[0]
    else:
        deal = Deal.objects.get(slug=slug)
    
    if not deal.is_expired(): 
        countdown_time = deal.date_published.strftime("%Y,%m,%d") #+ ' 11:59 PM'
    else:
        countdown_time = -1
    
    return render_to_response('deal_detail.html', {
             #   'now' : now,
                'user_msg' : user_msg,
                'deal' : deal,
                'countdown_time' : countdown_time,
              }, context_instance=RequestContext(request))

   
def city_deals(request, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    # TODO: filter only deals that didn't expired
    city_deal = Deal.objects.all().filter(city=city)
    countdown_time = -1
    deal = None
    if len(city_deal):
        deal = city_deal[0]
        if not deal.is_expired(): 
            countdown_time = deal.date_published.strftime("%Y,%m,%d") #+ ' 11:59 PM'
    else:
        messages.error(request, "There are no deals opened for this city.")
    
    return render_to_response('deal_detail.html', {
             #   'now' : now,
                'deal' : deal,
                'countdown_time' : countdown_time,
              }, context_instance=RequestContext(request))
        
    return HttpResponse("City %s" % city_slug)


#TODO: Implement suggestions / suggest a business
def suggestions(request):
    return HttpResponse('Suggestions')
