from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from pegelstand.models import PegelZeit
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	#url(r'^/$', views.contact, name='contact'),
	#url(r'^abfrage/$', views.abfrage, name='abfrage'),	
]