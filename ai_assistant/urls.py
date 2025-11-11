from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.ConversationMessageView.as_view(), name='conversation-message'),
]