#Custom Registration View. Inheritance comes in to play majorly here, inheriting from the 
#existing RegistrationForm in forms and inheriting from RegistrationView here.
from registration.backends.simple.views import RegistrationView
from rango.forms import UserProfileRegistrationForm
from rango.models import UserProfile

class MyRegistrationView(RegistrationView):
    
    form_class = UserProfileRegistrationForm
    
    def register(self, request, form_class):
        new_user = super(MyRegistrationView, self).register(request, form_class)
        user_profile = UserProfile()
        user_profile.user = new_user
        user_profile.website = form_class.cleaned_data['website']
        user_profile.picture = form_class.cleaned_data['picture']
        user_profile.save()
        return user_profile
    
    def get_success_url(self, request, user):
        return '/rango'