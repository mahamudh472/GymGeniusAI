from django.urls import path

from utils.views import FAQListView, FavoriteListView, FavoriteToggleView, SearchResultsView, ContactOptionListView


urlpatterns = [
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/toggle/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('search/', SearchResultsView.as_view(), name='search-results'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('contact-options/', ContactOptionListView.as_view(), name='contact-option-list'),  
]