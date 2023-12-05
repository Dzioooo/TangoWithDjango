from django.urls import path
from rango.api.v1 import views

urlpatterns = [
    path('Category/', views.CategoryList.as_view()),
    path('Category/details/<int:pk>', views.CategoryDetail.as_view())
]