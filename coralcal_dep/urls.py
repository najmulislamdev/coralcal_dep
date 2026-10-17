from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('ks', include('knowledge_series.urls')),
    path('dd/', include('doctor_development.urls')),
    path('gift/', include('dr_gift_catalogs.urls')),
    path('dep/admin/', include('dep_admin.urls')),
    path('anniversary/', include('anniversary.urls')),
    path('rgc/', include('green_corner.urls')),
    path('doctors_opinion/', include('doctors_opinion.urls')),
    path('doctors_data/', include('doctors_data.urls')),
    path('dac/', include('doctors_ai_course.urls')),
    path('plant/', include('plant_module.urls')),
    path('dac2/', include('doctors_ai_course2.urls')),
    path('boishakh-gift/', include('dr_boishakh_catalog.urls')),
    path('gift_catalogs_2/', include('gift_catalogs_2.urls')),
    path('gvc/', include('gift_voucher_catalog.urls')),
    path('nfc/', include('nfc_card_info.urls')),
    path('odd/', include('orthopedic_dr_dev.urls')),
    path('ddc/', include('doctor_dev_catalogue.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)