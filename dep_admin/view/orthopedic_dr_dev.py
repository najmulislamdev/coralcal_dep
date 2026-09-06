from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import openpyxl, os, zipfile
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from dep_admin import utils

@login_required
def orthopedic_dr_dev(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = int(request.GET.get('page') or 1)
        per_page = int(request.GET.get("per_page") or 10)
        sort = request.GET.get("sort", "territory")
        direction = request.GET.get("direction", "asc")
        # Get data using the utils function
        data = utils.filter_orthopedic_dr_dev_data(request)
        paginator = Paginator(data, per_page)
        page_obj = paginator.get_page(page_number)
    return render(request, 'orthopedic_dr_dev.html',{'data':page_obj, 'search_query':search_query, 'per_page':per_page, 'sort':sort, 'direction':direction})

@login_required
def export_orthopedic_dr_dev(request):
    """
    Export the Orthopedic Dr. Development data to an Excel file.
    """
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Orthopedic Dr. Development"

    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Submitted At']
    worksheet.append(headers)

    # Get data using the utils function
    data = utils.filter_orthopedic_dr_dev_data(request)

    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.territory.territory,
            obj.territory.territory_name,
            obj.territory.region_name,
            obj.territory.zone_name,
            obj.created_at.strftime('%Y-%m-%d')
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
    response['Content-Disposition'] = 'attachment; filename="orthopedic_dr_dev_data.xlsx"'

    return response

@login_required
def download_orthopedic_dr_dev(request):
    """
    Download the Orthopedic Dr. Development data as an Excel file bundled with the images.
    """
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Orthopedic Dr. Development"

    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Submitted At']
    worksheet.append(headers)
    # Get data using the utils function
    data = utils.filter_orthopedic_dr_dev_data(request)
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
            obj.created_at.strftime('%Y-%m-%d')
        ]
        worksheet.append(row)
        if obj.image:  # Check if image exists
            image_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
            if os.path.exists(image_path):
                image_paths.add(image_path)

    # Save the workbook to a BytesIO (in memory) object
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Create zip in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add filtered images to the zip file
        for image_path in image_paths:
            relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
            zip_file.write(image_path, relative_path)
        # Add the Excel file
        zip_file.writestr('orthopedic_dr_dev_data.xlsx', buffer.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="orthopedic_dr_dev_bundle.zip"'
    return response
