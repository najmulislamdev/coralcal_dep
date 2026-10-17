from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from core.models import Territory, UserProfile
from dep_admin.models import AccessControl
from doctor_dev_catalogue.models import DoctorDevCatalogue
from doctor_dev_catalogue.constants import (
    ACCESS_KEY, DEFAULT_ENTRY_LIMIT, COVER_IMAGE, ITEMS, ITEMS_BY_CODE, SIZE_LABELS,
)

# Create your views here.
def get_access_control():
    return AccessControl.objects.filter(key=ACCESS_KEY).first()


def get_entry_limit(access=None):
    """
    How many entries one territory may submit, as set on the Access Control page.
    """
    access = access or get_access_control()
    if access and access.entry_limit:
        return access.entry_limit
    return DEFAULT_ENTRY_LIMIT


def get_profile(user):
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return None


def is_admin_user(user):
    """
    Superusers and every non-territory profile (admin, zone, region) work from
    the dep_admin listing; territory users work from their own history page.
    """
    if user.is_superuser:
        return True
    profile = get_profile(user)
    return bool(profile and profile.user_type != 'territory')


def get_scoped_entry(request, pk):
    """
    Fetch an entry the current user is allowed to touch: a territory only its
    own entries, a zone / region user only entries inside their area.
    """
    entries = DoctorDevCatalogue.objects.select_related('territory')
    if not request.user.is_superuser:
        profile = get_profile(request.user)
        if not profile:
            raise Http404
        if profile.user_type == 'territory':
            entries = entries.filter(territory__territory=request.user.username)
        elif profile.user_type == 'zone':
            entries = entries.filter(territory__zone_name=profile.zone_name)
        elif profile.user_type == 'region':
            entries = entries.filter(territory__region_name=profile.region_name)
    return get_object_or_404(entries, pk=pk)


def redirect_after_change(request):
    """
    Admins go back to the dep_admin listing (keeping its filters when passed in
    `next`), territory users go back to their history page.
    """
    if is_admin_user(request.user):
        next_query = request.GET.get('next', '')
        url = reverse('ddc_admin')
        return redirect(url + next_query if next_query.startswith('?') else url)
    return redirect('ddc_history')


def clean_post(request):
    """
    Validate the submitted form. Returns (data, error); size is only kept for
    items that need one.
    """
    dr_id = (request.POST.get('dr_id') or '').strip()
    dr_name = (request.POST.get('dr_name') or '').strip()
    item_code = request.POST.get('item')
    size = request.POST.get('size') or None

    if not (dr_id and dr_name):
        return None, "Doctor RPL ID and Doctor Name are required."

    item = ITEMS_BY_CODE.get(item_code)
    if not item:
        return None, "Please select an item."

    if item['needs_size']:
        if size not in SIZE_LABELS:
            return None, f"Please select a size for {item_code}."
    else:
        size = None

    return {'dr_id': dr_id, 'dr_name': dr_name, 'item': item_code, 'size': size}, None


def form_context(obj=None, **extra):
    context = {
        'obj': obj,
        'items': ITEMS,
        'sizes': SIZE_LABELS.items(),
        'cover_image': COVER_IMAGE,
    }
    context.update(extra)
    return context


@login_required
def ddc_form(request):
    territory = Territory.objects.filter(territory=request.user.username).first()
    if not territory:
        messages.error(request, "No territory found for this user.")
        return redirect('home')

    access = get_access_control()
    if not (access and access.is_active):
        messages.error(request, "Doctor Development Catalogue is not active now.")
        return redirect('home')

    entry_limit = get_entry_limit(access)
    entry_count = DoctorDevCatalogue.objects.filter(territory=territory).count()
    if entry_count >= entry_limit:
        messages.success(request, f"You have already submitted {entry_count} of {entry_limit} entries. You can edit them from here.")
        return redirect('ddc_history')

    if request.method == 'POST':
        data, error = clean_post(request)
        if error:
            messages.error(request, error)
            return redirect('ddc_form')

        try:
            DoctorDevCatalogue.objects.create(territory=territory, **data)
            messages.success(request, f"Successfully submitted {data['item']} for {data['dr_name']}.")
        except Exception as e:
            messages.error(request, f"Error saving data: {str(e)}")
            print(f"Error saving data: {str(e)}")
            return redirect('ddc_form')
        return redirect('ddc_history')

    return render(request, 'ddc_form.html', form_context(entry_count=entry_count, entry_limit=entry_limit))


@login_required
def ddc_history(request):
    territory = Territory.objects.filter(territory=request.user.username).first()
    if not territory:
        messages.error(request, "No territory found for this user.")
        return redirect('home')

    search_query = request.GET.get("search", "")
    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("direction", "desc")
    per_page = int(request.GET.get("per_page") or 10)
    page = request.GET.get("page", 1)

    entries = DoctorDevCatalogue.objects.filter(territory=territory)
    entry_count = entries.count()

    # search filter
    if search_query:
        entries = entries.filter(
            Q(dr_id__icontains=search_query) |
            Q(dr_name__icontains=search_query) |
            Q(item__icontains=search_query) |
            Q(size__iexact=search_query)
        )

    # sorting
    if sort not in ('dr_id', 'dr_name', 'item', 'size', 'created_at'):
        sort = 'created_at'
    entries = entries.order_by(f"-{sort}" if direction == "desc" else sort)

    # pagination
    paginator = Paginator(entries, per_page)
    page_obj = paginator.get_page(page)

    access = get_access_control()
    entry_limit = get_entry_limit(access)
    context = {
        'data': page_obj,
        'search_query': search_query,
        'sort': sort,
        'direction': direction,
        'per_page': per_page,
        'entry_count': entry_count,
        'entry_limit': entry_limit,
        'can_add': bool(access and access.is_active) and entry_count < entry_limit,
    }
    return render(request, 'ddc_history.html', context)


@login_required
def ddc_edit(request, pk):
    obj = get_scoped_entry(request, pk)

    if request.method == 'POST':
        data, error = clean_post(request)
        if error:
            messages.error(request, error)
            return redirect(request.get_full_path())

        try:
            for field, value in data.items():
                setattr(obj, field, value)
            obj.save()
            messages.success(request, "Doctor Development Catalogue entry updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating data: {str(e)}")
            print(f"Error updating data: {str(e)}")
        return redirect_after_change(request)

    return render(request, 'ddc_form.html', form_context(obj, is_admin_edit=is_admin_user(request.user)))


@login_required
def ddc_delete(request, pk):
    obj = get_scoped_entry(request, pk)
    try:
        obj.delete()
        messages.success(request, "Doctor Development Catalogue entry deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        print(f"Error deleting data: {str(e)}")
    return redirect_after_change(request)
