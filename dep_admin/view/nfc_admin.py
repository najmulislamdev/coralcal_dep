from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import openpyxl
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Q 
from nfc_card_info.models import NfcCardInfo
from core.models import UserProfile

@login_required
def nfc_admin_view(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc") 
        
        data = NfcCardInfo.objects.select_related("territory").all()
        # Filter based on the user's profile
        try:
            profile = request.user.userprofile
            if profile.user_type == "zone":
                data = data.filter(territory__zone_name = profile.zone_name)
            elif profile.user_type == "region":
                data = data.filter(territory__region_name = profile.region_name)
        except UserProfile.DoesNotExist:
            if not request.user.is_superuser:
                data = NfcCardInfo.objects.none()
        # Filter based on search query
        search_query = request.GET.get("search","")
        if search_query:
            data = data.filter(
                Q(dr_rpl_id__icontains=search_query) |
                Q(dr_name__icontains=search_query) |
                Q(territory__territory__icontains=search_query) |
                Q(territory__territory_name__icontains=search_query) |
                Q(territory__region_name__icontains=search_query) |
                Q(territory__zone_name__icontains=search_query) | 
                Q(institute__icontains=search_query) |
                Q(degree__icontains=search_query)
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
            sort_by = "dr_rpl_id"
        elif sort_by == "dr_name":
            sort_by = "dr_name"
        if direction == "desc":
            sort_by = f"-{sort_by}" 
        data = data.order_by(sort_by)

        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
        context = {
            'data': page_obj,
            'search_query': search_query,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page_number': page_number,
            'total_pages': paginator.num_pages,
        }
        return render(request, 'nfc_admin.html', context)

@login_required 
def nfc_export(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Doctor's NFC Card Info"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name','Degree', 'Specialty', 'Designation', 'Institute', 'Territory ID', 'Territory Name', 'Region', 'Zone']
    worksheet.append(headers)
    data = NfcCardInfo.objects.select_related("territory").all()
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_rpl_id,
            obj.dr_name,
            obj.degree,
            obj.specialty,
            obj.designation,
            obj.institute,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name
        ]
        worksheet.append(row)
    
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or '')) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 5
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="doctors_nfc_card_data.xlsx"'
    return response