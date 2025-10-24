from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('conversation/', views.ConversationView.as_view(), name='conversation'),
]