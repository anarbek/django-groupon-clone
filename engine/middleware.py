'''
Created on Jul 2, 2011

@author: madalinoprea
'''
class ProfileMiddleware(object):
    def process_request(self, request):
        '''
        Updates user attributes with Facebook info.
        
        @param request:
        '''
        if not request.user.is_anonymous():
            profile = request.user.get_profile()
            if profile and not profile.is_filled():
                # Is this a facebook authenticated used
                if getattr(request, 'facebook'):
                    if request.facebook.user:
                        me = request.facebook.graph.get_object('me')
                        profile.fill_from_facebook(me)
                        
        return None