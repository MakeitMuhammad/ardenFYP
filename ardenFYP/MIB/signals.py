# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile, SocialLink

# Signal to create UserProfile when a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Signal to save UserProfile when a CustomUser is saved
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Signal to create SocialLink when a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_social_links(sender, instance, created, **kwargs):
    if created:
        SocialLink.objects.create(user=instance)
