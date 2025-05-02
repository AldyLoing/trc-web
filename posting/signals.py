from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import CustomUser

@receiver(post_save, sender=User)
def after_create_user(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(id_user=instance, nomor_hape=instance.nomor_hape)