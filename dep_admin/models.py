from django.db import models

# Create your models here.
class AccessControl(models.Model):
    key=models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)
    # Max entries per territory, for modules that limit it (null = not used).
    entry_limit = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_control'
        verbose_name = 'Access Control'
        verbose_name_plural = 'Access Control'
        
    def __str__(self):
        return self.key+"-"+str(self.is_active)