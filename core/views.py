from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dep_admin.models import AccessControl

# Create your views here.
def home(request):
    return redirect('login')

def login_view(request):
    """
    Handle user login with territory code or admin credentials.
    """
    if request.user.is_authenticated:
        if not request.user.is_superuser and request.user.userprofile.user_type == 'territory':
            return redirect('territory_home')
        return redirect('knowledge_series')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not user.is_superuser and user.userprofile.user_type == 'territory':
                messages.success(request, "Login successful.")
                return redirect('territory_home')
            messages.success(request, "Login successful.")
            return redirect('knowledge_series')
        
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'login/login.html')


@login_required
def user_logout(request):
    """
    Log out the current user and redirect to login page.
    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required
def territory_home(request):
    access_control = AccessControl.objects.all()
    access_control_states = {item.key:item.is_active for item in access_control}
    events = {
        'knowledge_series': {'label': 'Knowledge Series', 'url_name': 'book_choice', 'is_active': access_control_states['knowledge_series']},
        'gift_catalogs': {'label': 'Gift Catalogs', 'url_name': 'gift_choice', 'is_active': access_control_states['gift_catalogs']},
        'anniversary': {'label': 'Enlighten Together', 'url_name': 'anniversary_form', 'is_active': access_control_states['anniversary']},
        'green_corner': {'label': 'Radiant Green Corner', 'url_name': 'rgc_upload', 'is_active': access_control_states['green_corner']},
        'doctors_opinion': {'label': "Doctor Opinion", 'url_name': 'do_form', 'is_active': access_control_states['doctors_opinion']},
        'doctors_data': {'label': "Doctor Chamber Info", 'url_name': 'dd_form', 'is_active': access_control_states['doctors_data']},
        'doctors_ai_course': {'label': "AI for Doctors Old", 'url_name': 'dac_form', 'is_active': access_control_states['doctors_ai_course']},
        'doctors_ai_course2': {'label': "AI for Doctors", 'url_name': 'dac2_form', 'is_active': access_control_states['doctors_ai_course2']},
        'plant_module': {'label': "HerStory Plant Catalogue", 'url_name': 'p_form', 'is_active': access_control_states['plant_module']},
        'doctor_development': {'label': "Doctor Development 1Q 26", 'url_name': 'dd_gift_choice', 'is_active': access_control_states['doctor_development']},
        'dr_boishakh_catalog': {'label': "Pohela Boishakh Calatog", 'url_name': 'view_boishakh_catalogs', 'is_active': access_control_states['dr_boishakh_catalog']},
        'gift_catalogs_2': {'label': "Gift Catalogs 2026", 'url_name': 'gift_catalogs_2026_form', 'is_active': access_control_states['gift_catalogs_2']},
        'gift_voucher_catalog': {'label': "Gift Voucher Catalogue", 'url_name': 'gvc_form', 'is_active': access_control_states['gvc_26']},
        'nfc_card_info': {'label': "NFC Card Info", 'url_name': 'nfc_form', 'is_active': access_control_states['nfc_card_info']},
        'orthopedic_dr_development': {'label': "Orthopedic Dr. Development", 'url_name': 'odd_form', 'is_active': access_control_states['orthopedic_dr_development']},
    }
    return render(request, 'home.html', {'events': events})