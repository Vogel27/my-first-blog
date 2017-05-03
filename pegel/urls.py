from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from pegel.models import Pegel, PegelZeit
from . import views


urlpatterns = [ #url(r'^$', ListView.as_view(queryset=Post.objects.all().order_by("-date")[:25], template_name="blog/blog.html")),
				#url(r'^(?P<pk>\d+)$', DetailView.as_view(model=Post, template_name = 'blog/post.html')),
				url(r'^$', views.index, name='index'),
				url(r'^detail$', ListView.as_view(queryset=Pegel.objects.all(), template_name="pegel/pegeldetail.html")),
				
				]
