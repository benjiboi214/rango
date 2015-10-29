from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
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

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
    url(r'^search/$', include('haystack.urls')),
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    (r'^accounts/', include('registration.backends.simple.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )