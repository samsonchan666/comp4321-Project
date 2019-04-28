from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.result, name='result'),
    path('remote/<int:page_id>/', views.remote, name='remote'),
    path('similar', views.similar, name='similar'),
]