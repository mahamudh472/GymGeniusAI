from django.urls import path

from utils.views import (
    FAQListView, 
    FavoriteListView, 
    FavoriteToggleView,
    MarkAllNotificationsReadView, 
    SearchResultsView, 
    ContactOptionListView,
    NotificationListView,
    NotificationDetailView
)


urlpatterns = [
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/toggle/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('search/', SearchResultsView.as_view(), name='search-results'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('contact-options/', ContactOptionListView.as_view(), name='contact-option-list'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
]