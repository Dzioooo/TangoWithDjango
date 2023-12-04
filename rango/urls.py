from django.urls import path

from rango import views
from rango import views_ajax

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('add_category/', views.AddCategoryView.as_view(),
         name='add_category'),
    path('category/<slug:category_name_slug>/',
         views.ShowCategoryView.as_view(), name='show_category'),
    path('category/<slug:category_name_slug>/add_page/',
         views.AddPageView.as_view(),
         name='add_page'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('restricted/', views.RestrictedView.as_view(), name='restricted'),
    path('goto/', views.TrackUrlView.as_view(), name='goto'),
    path('register_profile/', views.RegisterProfileView.as_view(),
         name='register_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    path('like/', views_ajax.LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', views_ajax.CategorySearchView.as_view(), 
         name='suggest_category'),
    path('add/', views_ajax.AutoAddPageView.as_view(), name='auto_add_page'),
]
