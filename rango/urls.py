from django.urls import path

from rango import views
from rango import views_ajax

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/', views.show_category,
         name='show_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page,
         name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('restricted/', views.restricted, name='restricted'),
    path('search/', views.search, name='search'),
    path('goto/', views.track_url, name='goto'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profiles/', views.list_profiles, name='list_profiles'),
    path('like/', views_ajax.like_category, name='like_category'),
    path('suggest/', views_ajax.suggest_category, name='suggest_category'),
    path('add/', views_ajax.auto_add_page, name='auto_add_page'),
]
