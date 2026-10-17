from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from knowledge_series.models import BookWishes
from doctor_development.models import DoctorDevelopment
from django.core.paginator import Paginator
import openpyxl , os, zipfile, shutil, json
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from .models import AccessControl
from openpyxl.styles import Alignment
from doctors_data.models import Doctor, Chamber
from . import utils
import tempfile
import os
from django.core.management import call_command

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def knowledge_series(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")        
        # Get data usnig utils filter function
        data = utils.filter_knowledge_series_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
    return render(request, 'knowledge_series.html', {
        'data': page_obj, 'search_query': search_query, 'per_page': per_page, 'sort': sort, 'direction': direction
    })
    
@login_required 
def export_knowledge_series(request):
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Knowledge Series Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Book']
    worksheet.append(headers)
    
    # Get data using the utils function
    data = utils.filter_knowledge_series_data(request)
    
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.book
        ]
        worksheet.append(row)
    
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="knowledge_series_data.xlsx"'
    
    return response

@login_required
def delete_knowledge_series_data(request, id):
    territory = request.user.username
    if request.user.is_superuser:
        territory = request.GET.get('territory')
    # territory_obj = Territory.objects.get(territory=territory)
    # ks_obj = BookWishes.objects.filter(territory__territory=territory)
    obj = BookWishes.objects.get(id=id)
    try:
        obj.delete()
        
        messages.success(request, f"Data deleted successfully.")
        if request.user.is_superuser:
            return redirect('knowledge_series')
        return redirect('home')
    except BookWishes.DoesNotExist:
        messages.error(request, "Invalid Item selected.")
        if request.user.is_superuser:
            return redirect('knowledge_series')
        return redirect('home')
    
@login_required 
def download_gift_catalogs(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Gift Catalogs Data"
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Gift Choice']
    worksheet.append(headers)
    data = utils.filter_gift_catalogs_data(request)
    image_paths = set()
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.gift
        ]
        worksheet.append(row)
        if obj.conference_image:
            image_path = os.path.join(settings.MEDIA_ROOT, obj.conference_image.name)
            if os.path.exists(image_path):
                image_paths.add(image_path)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image_path in image_paths:
            relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
            zip_file.write(image_path, relative_path)
        # Add the Excel file
        zip_file.writestr('gift_catalogs_data.xlsx', buffer.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="gift_catalogs_data_bundle.zip"'
    return response

@login_required 
def export_gift_catalogs(request):
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Gift Catalogs Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Gift Choice']
    worksheet.append(headers)
    data = utils.filter_gift_catalogs_data(request)
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.gift
        ]
        worksheet.append(row)
    
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="gift_catalogs_data.xlsx"'
    
    return response

@login_required
def gift_catalogs(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")
        # Get data using the utils function
        data = utils.filter_gift_catalogs_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)    
    return render(request, 'gift_catalogs.html',{'data':page_obj, 'search_query':search_query, 'per_page':per_page, 'sort':sort, 'direction':direction})  

@login_required
def anniversary(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")
        # Get data using the utils function
        data = utils.filter_anniversary_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)    
    return render(request, 'anniversary.html',{'data':page_obj, 'search_query':search_query, 'per_page':per_page, 'sort':sort, 'direction':direction}) 

@login_required 
def export_anniversary(request):
    """
    Export the Anniversary(Enlighted Together) data to an Excel file.
    """
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Anniversary Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Anniversary Date']
    worksheet.append(headers)
    
    # Get data using the utils function
    data = utils.filter_anniversary_data(request)
    
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.anniversary_date.strftime('%Y-%m-%d')
        ]
        worksheet.append(row)
    
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="anniversary_data.xlsx"'
    
    return response

@login_required 
def download_anniverysary(request):
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Anniversary Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Anniversary Date']
    worksheet.append(headers)
    # Get data using the utils function
    data = utils.filter_anniversary_data(request)
    # Collect image paths for filtering
    image_paths = set()
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.anniversary_date
        ]
        worksheet.append(row)
        if obj.image:  # Check if image exists
            image_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
            if os.path.exists(image_path):
                image_paths.add(image_path)
                
    # Save the workbook to a BytesIO (in memory) object
    buffer =BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create zip in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add filteres images to the zip file
        for image_path in image_paths:
            relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
            zip_file.write(image_path, relative_path)    
        # Add the Excel file
        zip_file.writestr('anniversary_data.xlsx', buffer.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="anniversary_data_bundle.zip"'
    return response

@login_required
def green_corner(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")        
        data = utils.filter_green_corner_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
    return render(request, 'green_corner.html', {
        'data': page_obj, 'search_query': search_query, 'per_page': per_page, 'sort': sort, 'direction': direction
    })

@login_required 
def export_rgc(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Radiant Green Corner Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Dr. Address', 'RM Mobile', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Flower Plants', 'Medicinal Plants']
    worksheet.append(headers)
    data = utils.filter_green_corner_data(request)
    # Populate the worksheet with data
    for obj in data:
        flower_plants = f'{obj.first_flower_plant}, {obj.second_flower_plant}, {obj.third_flower_plant}.'
        medicinal_plants = f'{obj.first_medicinal_plant}, {obj.second_medicinal_plant}.'
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.dr_address,
            obj.rm_phone,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            flower_plants,
            medicinal_plants
        ]
        worksheet.append(row)
    
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="radiant_green_corner_data.xlsx"'
    
    return response
    
def access_control_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Per-territory entry limits travel next to the toggles as {key: limit}.
        entry_limits = data.pop('entry_limits', {})
        for key, limit in entry_limits.items():
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                continue
            if limit >= 1:
                AccessControl.objects.filter(key=key).update(entry_limit=limit)
        for key, value in data.items():
            try:
                obj = AccessControl.objects.get(key=key)
                obj.is_active = value
                obj.save()
            except Exception as e:
                messages.error(request, f"Error updating {key}: {str(e)}")
                return redirect('access_control')
        messages.success(request, f"Successfully updated {key}.")
        return redirect('access_control')
                
    if request.method == 'GET':
        access_controls = AccessControl.objects.all()
        access_control_states = {item.key: item.is_active for item in access_controls}
        entry_limits = {item.key: item.entry_limit for item in access_controls}
        return render(request, 'access_control.html', {'access_control': access_control_states, 'entry_limits': entry_limits})


@login_required
def doctors_opinion_view(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc") 
        data = utils.filter_doctors_opinion_data(request)
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
        return render(request, 'doctors_opinion.html', context)

@login_required 
def dop_export(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Doctor's Opinion Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name','Dr. Address', 'Dr. Mobile', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Indications']
    worksheet.append(headers)
    data = utils.filter_doctors_opinion_data(request)
    # Populate the worksheet with data
    for obj in data:
        indications_text = "\n".join(f"{i+1}. {ind.indication_text}" for i, ind in enumerate(obj.indications.all()))
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.dr_address,
            obj.dr_phone,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            indications_text
        ]
        worksheet.append(row)
        # Apply wrapText only to the last cell (Indications column)
        indications_cell = worksheet.cell(row=worksheet.max_row, column=9)  # 9th column = Indications
        indications_cell.alignment = Alignment(wrap_text=True)
    
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or '')) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 5
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="doctors_opinion_data.xlsx"'
    return response

@login_required
def doctors_data(request):
    if request.method == 'GET':
        # Get query params with default values
        search_query = request.GET.get('search_query', '')
        sort = request.GET.get('sort', 'dr_id')
        direction = request.GET.get('direction', 'asc')
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page_number', 1))
        # Base queryset
        data = utils.filter_doctors_data(request)
        # Pagination
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)

        # Serialize chambers to JSON for each doctor
        for doctor in page_obj:
            chambers_list = []
            for ch in doctor.chambers.all():
                chambers_list.append({
                    "address": ch.address,
                    "phone": ch.phone,
                    "division": ch.division,
                    "district": ch.district,
                    "upazila": ch.upazila,
                    "thana": ch.thana,
                    "visiting_days": ch.visiting_days or ''
                })
            doctor.chambers_json = json.dumps(chambers_list)

        # Pass context to template
        context = {
            'data': page_obj,
            'search_query': search_query,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page_number': page_number,
            'total_pages': paginator.num_pages,
        }

        return render(request, 'doctors.html', context)

@login_required
def doctors_data_export(request):
    wb = openpyxl.Workbook()

    # --- Sheet 1: Doctors ---
    ws_doctors = wb.active
    ws_doctors.title = "Doctors"
    ws_doctors.append(['ID', 'Name', 'Speciality', 'Designation'])

    doctors = utils.filter_doctors_data(request)
    for doc in doctors:
        ws_doctors.append([doc.id, doc.name, doc.speciality, doc.designation])

    # --- Sheet 2: Chambers ---
    ws_chambers = wb.create_sheet(title="Chambers")
    ws_chambers.append(['Doctor ID', 'Doctor Name', 'Address', 'Phone', 'District', 'Upazila', 'Thana'])

    chambers = Chamber.objects.select_related('doctor').all()
    for ch in chambers:
        ws_chambers.append([
            ch.doctor.id,
            ch.doctor.name,
            ch.address,
            ch.phone,
            ch.district,
            ch.upazila,
            ch.thana
        ])

    # Set response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=doctors_and_chambers.xlsx'
    wb.save(response)
    return response


@login_required
def doctors_ai_course(request):
    if request.method == 'GET':
        # Get query params with default values
        search_query = request.GET.get('search_query', '')
        sort = request.GET.get('sort', 'territory')
        direction = request.GET.get('direction', 'asc')
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page_number', 1))
        # Base queryset
        data = utils.filter_doctor_ai_course_data(request, model=1)
        
        # Pagination
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
        
        # Pass context to template
        context = {
            'data': page_obj,
            'search_query': search_query,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page_number': page_number,
            'total_pages': paginator.num_pages,
        }

        return render(request, 'doctors_ai_course.html', context)
  
@login_required  
def territory_upload(request):
    if request.method == 'POST':
        if 'territory_file' in request.FILES:
            territory_file = request.FILES['territory_file']
            # check file type excel or not.
            if not territory_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, "Please upload an Excel file.")
                return redirect('territory_upload')
            suffix = os.path.splitext(territory_file.name)[1]
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    
            try:
                for chunk in territory_file.chunks():
                    tmp_file.write(chunk)
                tmp_file.close()
                # Call your existing management command
                call_command(
                    'add_territories', 
                    file_path=tmp_file.name
                )
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('territory_upload')
            finally:
                # Always clean up temp file
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
            try:
                call_command(
                    'create_users'
                )
                messages.success(request, "Territories added successfully! Users Sync Successfully!")
            except Exception as e:
                messages.error(request, f"Error processing user creation: {str(e)}")
            return redirect('territory_upload')
        else:
            messages.error(request, "Please select a file.")
    return render(request, 'territory_upload.html')


@login_required
def download_territory_template(request):
    file_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'territories.xlsx')
    
    if not os.path.exists(file_path):
        messages.error(request, "Territory template file not found.")
        return redirect('territory_upload')

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename="territory_template.xlsx"'
        return response
    
@login_required
def plant_module(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")        
        data = utils.filter_plant_module_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
    return render(request, 'plant_module.html', {
        'data': page_obj, 'search_query': search_query, 'per_page': per_page, 'sort': sort, 'direction': direction
    })
    
@login_required 
def export_plant_module(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "HerStory Plant Catalogue Data"
    
    # Define the header row
    headers = ['Zone','Region','Territory ID','Territory Name','Dr. Name','Dr. RPL ID','Specialty', 'Designation', 'Location','Plant']
    worksheet.append(headers)
    data = utils.filter_plant_module_data(request)
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.territory.zone_name,
            obj.territory.region_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.dr_name,
            obj.dr_id,
            obj.specialty,
            obj.designation,
            obj.location,
            obj.plants

        ]
        worksheet.append(row)
    
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="HerStory_Plant_Catalogue_data.xlsx"'
    
    return response

@login_required
def doctors_ai_course2(request):
    if request.method == 'GET':
        # Get query params with default values
        search_query = request.GET.get('search_query', '')
        sort = request.GET.get('sort', 'territory')
        direction = request.GET.get('direction', 'asc')
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page_number', 1))
        # Base queryset
        data = utils.filter_doctor_ai_course_data(request)
        
        # Pagination
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
        
        # Pass context to template
        context = {
            'data': page_obj,
            'search_query': search_query,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page_number': page_number,
            'total_pages': paginator.num_pages,
        }

        return render(request, 'doctors_ai_course2.html', context)
    



@login_required
def doctor_development(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")        
        # Get data usnig utils filter function
        data = utils.filter_doctor_development_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
    return render(request, 'doctor_development.html', {
        'data': page_obj, 'search_query': search_query, 'per_page': per_page, 'sort': sort, 'direction': direction
    })
    
@login_required 
def export_doctor_development(request):
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Doctor Development 1Q26"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Gift']
    worksheet.append(headers)
    
    # Get data using the utils function
    data = utils.filter_doctor_development_data(request)
    
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.gift
        ]
        worksheet.append(row)
    
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="doctor_development_data.xlsx"'
    
    return response

@login_required
def delete_doctor_development_data(request, id):
    territory = request.user.username
    if request.user.is_superuser:
        territory = request.GET.get('territory')
    # territory_obj = Territory.objects.get(territory=territory)
    # ks_obj = BookWishes.objects.filter(territory__territory=territory)
    obj = DoctorDevelopment.objects.get(id=id)
    try:
        obj.delete()
        
        messages.success(request, f"Data deleted successfully.")
        if request.user.is_superuser:
            return redirect('doctor_development')
        return redirect('home')
    except BookWishes.DoesNotExist:
        messages.error(request, "Invalid Item selected.")
        if request.user.is_superuser:
            return redirect('doctor_development')
        return redirect('home')
    

# pohela boishakh catalog
@login_required 
def download_boishakh_catalogs(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Pohela Boishakh Catalogs Data"
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Gift Choices', "Size"]
    worksheet.append(headers)
    data = utils.filter_boishakh_catalogs_data(request)
    image_paths = set()
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.gifts,
            obj.size,
        ]
        worksheet.append(row)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image_path in image_paths:
            relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
            zip_file.write(image_path, relative_path)
        # Add the Excel file
        zip_file.writestr('boishakh_catalogs_data.xlsx', buffer.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="boishakh_catalogs_data_bundle.zip"'
    return response

@login_required 
def export_boishakh_catalogs(request):
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Pohela Boishakh Catalogs Data"
    
    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Gift Choices', "Size"]
    worksheet.append(headers)
    data = utils.filter_boishakh_catalogs_data(request)
    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.gifts,
            obj.size,
        ]
        worksheet.append(row)
    
    # Save the workbook to a BytesIO object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Create a response with the Excel file
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="gift_catalogs_data.xlsx"'
    
    return response

@login_required
def boishakh_catalogs(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")
        # Get data using the utils function
        data = utils.filter_boishakh_catalogs_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)    
    return render(request, 'boishakh_catalogs.html',{'data':page_obj, 'search_query':search_query, 'per_page':per_page, 'sort':sort, 'direction':direction})  
