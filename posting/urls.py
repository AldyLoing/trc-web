from django.urls import path

from . import views

app_name = 'trc-web'

urlpatterns = [
    path('', views.PendaftaranView.as_view(), name='index'), 
]