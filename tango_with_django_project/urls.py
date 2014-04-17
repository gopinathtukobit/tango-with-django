from django.conf.urls import patterns, include, url
from rango import views
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',views.index, name ='index'),
	url(r'^rango/about/$',views.about,name ='about'),
	url(r'^rango/add_category/$',views.add_category, name ='add_category'),
	url(r'^rango/category/(?P<category_name_url>\w+)/$',views.category, name ='category'),
	url(r'^rango/category/(?P<category_name_url>\w+)/add_page/$',views.add_page, name ='add_page'),
	url(r'^rango/register/$', views.register, name='register'),
	url(r'^rango/login/$', views.user_login, name='login'),
	url(r'^rango/restricted/', views.restricted, name='restricted'),
	url(r'^rango/logout/$', views.user_logout, name='logout'),
	url(r'^rango/search/$',views.search, name='search'),
	url(r'^rango/profile/$', views.profile, name='profile'),



	
	
	url(r'^admin/', include(admin.site.urls)),


    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )