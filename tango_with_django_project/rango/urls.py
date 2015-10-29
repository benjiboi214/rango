from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
    
    #see the following if the category regex is confusing.
    #the way it passes the slug to the following function.
    #https://docs.djangoproject.com/en/1.8/topics/http/urls/#views-extra-options
    #https://docs.djangoproject.com/en/1.8/ref/urls/
    
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^benweb/$', views.benweb, name='benweb'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^search/$', views.search, name='search'),
    url(r'^goto/$', views.track_url, name='goto'),
    #url(r'^logout/$', views.user_logout, name="logout"),
    #url(r'^register/$', views.register, name="register"),
    #url(r'^login/$', views.user_login, name="login"),
)
#Comment out original Login, Logut and Register function for review later.