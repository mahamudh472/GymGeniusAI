from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gallery'
    
    def ready(self):
        import apps.gallery.signals  # Register signals
