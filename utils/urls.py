from django.urls import path


from utils.views import (
    FAQListView, 
    FavoriteListView, 
    FavoriteToggleView,
    MarkAllNotificationsReadView,
    PrivacyPolicyView, 
    SearchResultsView, 
    ContactOptionListView,
    NotificationListView,
    NotificationDetailView,
    register_device_token,
    unregister_device_token,
    create_demo_notification,
    NotificationSettingsView,
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
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('register_device_token/', register_device_token, name='register-device-token'),
    path('unregister_device_token/', unregister_device_token, name='unregister-device-token'),
    path('create_demo_notification/', create_demo_notification, name='create-demo-notification'),
    path('notification-settings/', NotificationSettingsView.as_view(), name='notification-settings'),
]