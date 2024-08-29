from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_key_input, name='api_key_input'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('result/', views.result_view, name='result'),
]