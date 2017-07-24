from django.conf.urls import url

from . import views

# urlpatterns = [
#     url(r'^get_token/$', views.get_token),
#     url(r'^login/$', views.login, name='login'),
#     url(r'^get_user_info/$', views.get_user_info),
#     url(r'^logout/$', views.logout),
#     url(r'^upload/$', views.upload),
#     # url(r'^checkout/$', views.checkout),
# ]
urlpatterns = [] + views.urlpatterns
