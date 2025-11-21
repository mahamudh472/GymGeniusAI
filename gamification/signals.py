from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserRank
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_gamification_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserRank and UserStreak when a new user is created.
    This ensures all users have gamification profiles from the start.
    """
    if created:
        from .utils import get_or_create_user_rank
        # This will create UserRank and UserStreak
        get_or_create_user_rank(instance)
