from django.urls import path
from . import views

urlpatterns = [
    path('', views.GalleryViewset.as_view({'get': 'list', 'post': 'create'}), name='gallery-list'),
    path('<int:pk>/', views.GalleryImageDetail.as_view(), name='gallery-detail'),
]