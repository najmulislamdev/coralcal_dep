from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import openpyxl
from io import BytesIO
from django.http import HttpResponse
from dep_admin import utils

@login_required
def ddc_admin(request):
    search_query = request.GET.get('search', '')
    page_number = int(request.GET.get('page') or 1)
    per_page = int(request.GET.get("per_page") or 10)
    sort = request.GET.get("sort", "territory")
    direction = request.GET.get("direction", "asc")
    # Get data using the utils function
    data = utils.filter_doctor_dev_catalogue_data(request)
    paginator = Paginator(data, per_page)
    page_obj = paginator.get_page(page_number)
    return render(request, 'doctor_dev_catalogue.html', {'data':page_obj, 'search_query':search_query, 'per_page':per_page, 'sort':sort, 'direction':direction})

@login_required
def ddc_export(request):
    """
    Export the Doctor Development Catalogue data to an Excel file.
    """
    # Create a new workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Dr. Development Catalogue"

    # Define the header row
    headers = ['Dr. RPL ID', 'Dr. Name', 'Item', 'Size', 'Territory ID', 'Territory Name', 'Region', 'Zone', 'Submitted At']
    worksheet.append(headers)

    # Get data using the utils function
    data = utils.filter_doctor_dev_catalogue_data(request)

    # Populate the worksheet with data
    for obj in data:
        row = [
            obj.dr_id,
            obj.dr_name,
            obj.item,
            obj.size or '',
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
    response['Content-Disposition'] = 'attachment; filename="doctor_development_catalogue_data.xlsx"'

    return response
