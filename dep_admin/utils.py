from django.db.models import Q
from core.models import UserProfile
from anniversary.models import Anniversary
from knowledge_series.models import BookWishes
from dr_gift_catalogs.models import DrGiftCatalog
from green_corner.models import GreenCorner
from doctors_opinion.models import DoctorOpinion
from doctors_data.models import Doctor
from doctors_ai_course.models import DoctorAiCourse
from plant_module.models import PlantModule
from doctors_ai_course2.models import DoctorAiCourseUp
from doctor_development.models import DoctorDevelopment
from dr_boishakh_catalog.models import PohelaBoishakhCatalog
from orthopedic_dr_dev.models import OrthopedicDr
from doctor_dev_catalogue.models import DoctorDevCatalogue


def filter_knowledge_series_data(request):
    data = BookWishes.objects.select_related('territory').all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif  profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = BookWishes.objects.none()
            
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(book__icontains=search_query) | 
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query)
        )
    # Sorting
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    return data

def filter_anniversary_data(request):
    data = Anniversary.objects.select_related('territory')
    
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif  profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = Anniversary.objects.none()
    
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        try:
            data = data.filter(
                Q(dr_id__icontains = search_query) |
                Q(dr_name__icontains = search_query) |
                Q(anniversary_date__icontains = search_query) |
                Q(territory__territory__icontains = search_query) |
                Q(territory__territory_name__icontains = search_query) |
                Q(territory__region_name__icontains = search_query) |
                Q(territory__zone_name__icontains = search_query)
            )
        except ValueError:
            data = data.filter(
                Q(dr_id__icontains = search_query) |
                Q(dr_name__icontains = search_query) |
                Q(territory__territory__icontains = search_query) |
                Q(territory__territory_name__icontains = search_query) |
                Q(territory__region_name__icontains = search_query) |
                Q(territory__zone_name__icontains = search_query)
            )
    
    # Filter based on sort and direction.
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = None
    if sort == "territory":
        sort_by = "territory__territory"
    elif sort == "territory_name":
        sort_by = "territory__territory_name"
    elif sort == "region":
        sort_by = "territory__region_name"
    elif sort == "zone":
        sort_by = "territory__zone_name"
    elif sort == "dr_id":
        sort_by = "dr_id"
    elif sort == "dr_name":
        sort_by = "dr_name"
        
    if direction == "desc":
        sort_by = f"-{sort_by}"
    
    if sort_by:
        data = data.order_by(sort_by)
    return data

def filter_gift_catalogs_data(request, model=None):
    if model:
        data = model.objects.select_related('territory').all()
    else:
        data = DrGiftCatalog.objects.select_related('territory').all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name = profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name = profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = DrGiftCatalog.objects.none()
    
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query) | 
            Q(gift__icontains=search_query)
        )
    
    # Soring
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    
    return data

def filter_green_corner_data(request):
    data = GreenCorner.objects.select_related("territory").all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name = profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name = profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = GreenCorner.objects.none()
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(first_flower_plant__icontains = search_query) |
            Q(second_flower_plant__icontains = search_query) |
            Q(third_flower_plant__icontains = search_query) |
            Q(first_medicinal_plant__icontains = search_query) |
            Q(second_medicinal_plant__icontains = search_query) |
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query)
        )
    # Soring
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    
    return data

def filter_doctors_opinion_data(request):
    data = DoctorOpinion.objects.select_related("territory").all()
    # Filter based on the user's profile
    try:
        profile = request.user.userprofile
        if profile.user_type == "zone":
            data = data.filter(territory__zone_name = profile.zone_name)
        elif profile.user_type == "region":
            data = data.filter(territory__region_name = profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = DoctorOpinion.objects.none()
    # Filter based on search query
    search_query = request.GET.get("search","")
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query) | 
            Q(dr_address__icontains=search_query) |
            Q(dr_phone__icontains=search_query)
        )
    # Sorting
    sort = request.GET.get("sort","territory")
    direction = request.GET.get("direction","asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}" 
    data = data.order_by(sort_by)
    
    return data

def filter_doctors_data(request):
    data = Doctor.objects.all()
    # Filter based on search query
    search_query = request.GET.get("search","")
    if search_query:
        data = data.filter(
            Q(id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(speciality__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(chambers__district__icontains=search_query) |
            Q(chambers__upazila__icontains=search_query) |
            Q(chambers__thana__icontains=search_query) |
            Q(chambers__address__icontains=search_query) |
            Q(chambers__phone__icontains=search_query)
        ).distinct()
    # Sorting
    sort = request.GET.get("sort","dr_id")
    direction = request.GET.get("direction","asc")
    sort_by = {
        "dr_id": "id",
        "dr_name": "name"
    }.get(sort, sort)
    if direction == "desc":
        sort_by = f"-{sort_by}"    
    data = data.order_by(sort_by)
    return data


def filter_doctor_ai_course_data(request, model=2):
    if model == 1:
        data = DoctorAiCourse.objects.select_related('territory')
    else:
        data = DoctorAiCourseUp.objects.select_related('territory')
    
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif  profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = Anniversary.objects.none()
    
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        try:
            data = data.filter(
                Q(rpl_id__icontains = search_query) |
                Q(name__icontains = search_query) |
                Q(specialty__icontains = search_query) |
                Q(designation__icontains = search_query) |
                Q(territory__territory__icontains = search_query) |
                Q(territory__territory_name__icontains = search_query) |
                Q(territory__region_name__icontains = search_query) |
                Q(territory__zone_name__icontains = search_query)
            )
        except ValueError:
            data = data.filter(
                Q(rpl_id__icontains = search_query) |
                Q(name__icontains = search_query) |
                Q(territory__territory__icontains = search_query) |
                Q(territory__territory_name__icontains = search_query) |
                Q(territory__region_name__icontains = search_query) |
                Q(territory__zone_name__icontains = search_query)
            )
    
    # Filter based on sort and direction.
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = None
    if sort == "territory":
        sort_by = "territory__territory"
    elif sort == "territory_name":
        sort_by = "territory__territory_name"
    elif sort == "region":
        sort_by = "territory__region_name"
    elif sort == "zone":
        sort_by = "territory__zone_name"
    elif sort == "dr_id":
        sort_by = "rpl_id"
    elif sort == "dr_name":
        sort_by = "name"
        
    if direction == "desc":
        sort_by = f"-{sort_by}"
    
    if sort_by:
        data = data.order_by(sort_by)
    return data


def filter_plant_module_data(request):
    data = PlantModule.objects.select_related("territory").all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name = profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name = profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = GreenCorner.objects.none()
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(plants__icontains = search_query) |
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query)
        )
    # Soring
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    
    return data




def filter_doctor_development_data(request):
    data = DoctorDevelopment.objects.select_related('territory').all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif  profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = DoctorDevelopment.objects.none()
            
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(gift__icontains=search_query) | 
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query)
        )
    # Sorting
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    return data

# pohela boishakh
def filter_boishakh_catalogs_data(request):
    data = PohelaBoishakhCatalog.objects.select_related('territory').all()
    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name = profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name = profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = PohelaBoishakhCatalog.objects.none()
    
    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(territory__territory__icontains=search_query) |
            Q(territory__territory_name__icontains=search_query) |
            Q(territory__region_name__icontains=search_query) |
            Q(territory__zone_name__icontains=search_query) | 
            Q(gift__icontains=search_query)
        )
    
    # Soring
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = sort
    if sort_by == "territory":
        sort_by = "territory__territory"
    elif sort_by == "territory_name":
        sort_by = "territory__territory_name"
    elif sort_by == "region":
        sort_by = "territory__region_name"
    elif sort_by == "zone":
        sort_by = "territory__zone_name"
    elif sort_by == "dr_id":
        sort_by = "dr_id"
    elif sort_by == "dr_name":
        sort_by = "dr_name"
    if direction == "desc":
        sort_by = f"-{sort_by}"
    data = data.order_by(sort_by)
    
    return data


def filter_orthopedic_dr_dev_data(request):
    data = OrthopedicDr.objects.select_related('territory')

    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = OrthopedicDr.objects.none()

    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains = search_query) |
            Q(dr_name__icontains = search_query) |
            Q(territory__territory__icontains = search_query) |
            Q(territory__territory_name__icontains = search_query) |
            Q(territory__region_name__icontains = search_query) |
            Q(territory__zone_name__icontains = search_query)
        )

    # Filter based on sort and direction.
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = None
    if sort == "territory":
        sort_by = "territory__territory"
    elif sort == "territory_name":
        sort_by = "territory__territory_name"
    elif sort == "region":
        sort_by = "territory__region_name"
    elif sort == "zone":
        sort_by = "territory__zone_name"
    elif sort == "dr_id":
        sort_by = "dr_id"
    elif sort == "dr_name":
        sort_by = "dr_name"

    if direction == "desc":
        sort_by = f"-{sort_by}"

    if sort_by:
        data = data.order_by(sort_by)
    return data


def filter_doctor_dev_catalogue_data(request):
    data = DoctorDevCatalogue.objects.select_related('territory')

    # Filter based on the User's profile.
    try:
        profile = request.user.userprofile
        if profile.user_type == 'zone':
            data = data.filter(territory__zone_name=profile.zone_name)
        elif profile.user_type == 'region':
            data = data.filter(territory__region_name=profile.region_name)
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            data = DoctorDevCatalogue.objects.none()

    # Filter Based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        data = data.filter(
            Q(dr_id__icontains = search_query) |
            Q(dr_name__icontains = search_query) |
            Q(item__icontains = search_query) |
            Q(size__iexact = search_query) |
            Q(territory__territory__icontains = search_query) |
            Q(territory__territory_name__icontains = search_query) |
            Q(territory__region_name__icontains = search_query) |
            Q(territory__zone_name__icontains = search_query)
        )

    # Filter based on sort and direction.
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    sort_by = None
    if sort == "territory":
        sort_by = "territory__territory"
    elif sort == "territory_name":
        sort_by = "territory__territory_name"
    elif sort == "region":
        sort_by = "territory__region_name"
    elif sort == "zone":
        sort_by = "territory__zone_name"
    elif sort in ("dr_id", "dr_name", "item", "size", "created_at"):
        sort_by = sort

    if sort_by:
        if direction == "desc":
            sort_by = f"-{sort_by}"
        data = data.order_by(sort_by)
    return data
