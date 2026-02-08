from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Electronics
import os

@receiver(post_delete, sender=Electronics)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Electronics` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(pre_save, sender=Electronics)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when corresponding `Electronics` object is updated
    with a new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Electronics.objects.get(pk=instance.pk).image
    except Electronics.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
