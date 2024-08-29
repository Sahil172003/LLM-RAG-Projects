from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate, name='generate'),
    path('download_json/', views.download_json, name='download_json'),
    path('download_parquet/', views.download_parquet, name='download_parquet'),
]