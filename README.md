## Status
 * Phase: Alpha / Under development

## Installation
 * Checkout the project
 * Make sure all requirements are installed: `pip install -r requirements.txt`
 * Adjust your settings (DB, etc)
 * Create DB structure and import initial data: `./manage.py syncdb`
 
 
## Backlog
 * Add user registration: django-registration
 * <strike>Refactor cities variable required by all the templates; create a template tag or use template processor</strike>
 * <strike>Add flatpages for static content</strike>
 * Clean up inline CSS and JS
 * Clean up template: indentation needs to be corrected
 * Implement buy for friend
 * Implement Reviews ?!
 * Localization (views, templates)
 * Add url to Advetiser (maybe)
 * <strike>Move header.html inclusion from all the templates to base.html</strike>
 * <strike>Review usage of  the following apps: countries, debug_toolbar, facebook, socialregistration, photologue, etc; 
add them to requirements.txt and delete them from repo.</strike>
 * <strike>Install django-socialregistration in requirements; clean up url entries</strike>
 * <strike>Implemented simple version for robots.txt</strike>

 
## Original README
Massive Coupon - An Open Source Crowd Buying engine

Here it is boys and girls ... a decent starting point for your own Groupon clone. I wrote this over 2 weekends and spent some coin designing it - and now I'm giving it all away for FREE!

Why am I doing this?  Why not?  I decided not to launch due to increasing competition - so my loss is your gain!  I hope to see some cool development and branches come out of this thing.   The open-source community has hooked me up big time over the years - Linux, Apache, Python, Django and on and on....  so I'm hoping this will help someone out.

Features:

- Nice Design (all html / css / graphics included!)
- Basic Groupon functionality (deal timeouts, tipping point, checkout, paypal express integration)


The engine is written in Python + Django .. any decent Django coder should be able to get it up and running.  I didn't have too much time to clean it up .. so it's 'as is'.

Good luck and happy group buying!


Rob Platek
SocialWire.ca
