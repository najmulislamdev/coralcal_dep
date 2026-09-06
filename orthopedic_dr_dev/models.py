import os
from django.core.files.storage import FileSystemStorage
from django.db import models
from core.models import Territory

# Create your models here.
def get_image_upload_path(instance, filename):
    """
    Generate a structured upload path and filename for images.
    
    Args:
        instance (image): The Image instance.
        filename (str): The name of the uploaded file.
        
    Returns:
        str: The constructed upload path.
    """
    
    # Extract file extension
    ext = os.path.splitext(filename)[1]
    
    territory_obj = Territory.objects.get(territory=instance.territory.territory)
    zone = territory_obj.zone_name
    region = territory_obj.region_name
    dr_folder = f"{instance.dr_id}-{instance.dr_name.replace(' ', '_')}" if instance.dr_name else instance.dr_id
    # Construct filename
    filename = f"{instance.territory.territory}_{instance.dr_id}_{instance.dr_name}{ext}"
    
    # Construct path and return
    return os.path.join('orthopedic_dr_development',zone, region, instance.territory.territory,dr_folder, filename)


class OverwriteStorage(FileSystemStorage):
    """
    Storage that replaces a file instead of renaming around it.

    The upload path is derived from the territory, doctor id and doctor name, so
    re-uploading for the same doctor targets the exact same path. The default
    storage would keep the old file and suffix the new one; here the path stays
    stable and the newest upload wins.
    """

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return super().get_available_name(name, max_length=max_length)


class OrthopedicDr(models.Model):
    """
    Model to represent a doctor's gift catalog.
    """
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='orthopedic_dr_devs')
    dr_id = models.CharField(max_length=20, unique=True)
    dr_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_upload_path, storage=OverwriteStorage(), blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dr_name} - ({self.territory})"
    
    class Meta:
        db_table = 'orthopedic_dr_dev'
        verbose_name = "Orthopedic Doctor Development"
        verbose_name_plural = "Orthopedic Doctor Development"