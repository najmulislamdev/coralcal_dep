from django.db import models
from core.models import Territory
from doctor_dev_catalogue.constants import ITEMS, ITEMS_BY_CODE, SIZE_LABELS

# Create your models here.
class DoctorDevCatalogue(models.Model):
    """
    A doctor's item choice from the Doctor Development Catalogue.
    """
    ITEM_CHOICES = [(item['code'], item['code']) for item in ITEMS]
    SIZE_CHOICES = [(code, code) for code in SIZE_LABELS]

    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='doctor_dev_catalogues')
    dr_id = models.CharField(max_length=20)
    dr_name = models.CharField(max_length=100)
    item = models.CharField(max_length=10, choices=ITEM_CHOICES)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dr_name} - {self.item} ({self.territory})"

    @property
    def item_image(self):
        item = ITEMS_BY_CODE.get(self.item)
        return item['image'] if item else ''

    @property
    def size_label(self):
        return SIZE_LABELS.get(self.size, '')

    class Meta:
        db_table = 'doctor_dev_catalogue'
        verbose_name = "Doctor Development Catalogue"
        verbose_name_plural = "Doctor Development Catalogue"
