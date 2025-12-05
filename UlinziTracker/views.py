from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth import logout


from .models import Profile, Incident
from .forms import (
    UserRegisterForm,
    ProfileUpdateForm,
    UserProfileForm,
    UserProfileUpdateForm,
    IncidentForm,
    StatusUpdateForm
)

def index(request):
    return render(request, "UlinziTracker/home.html")

def aboutus(request):
    return render(request, "UlinziTracker/aboutus.html")

# --- Incident statistics ---
@login_required
def incidentStats(request):
    # Restrict: only chiefs and admins can view analytics
    role = request.user.profile.role
    if role not in ['chief', 'admin']:
        messages.error(request, "You are not authorized to view incident statistics.")
        return redirect('UlinziTracker:dashboard')

    total = Incident.objects.count()
    pending = Incident.objects.filter(status='pending').count()
    resolved = Incident.objects.filter(status='resolved').count()
    inprogress = Incident.objects.filter(status='in_progress').count()

    dataset = Incident.objects.values('category').annotate(
        total=Count('status'),
        resolved=Count('status', filter=Q(status='resolved')),
        pending=Count('status', filter=Q(status='pending')),
        inprogress=Count('status', filter=Q(status='in_progress'))
    ).order_by('category')

    context = {
        'total': total,
        'unsolved': pending + inprogress,
        'solved': resolved,
        'dataset': dataset
    }
    return render(request, "UlinziTracker/incidentStats.html", context)

# --- Change password ---
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('UlinziTracker:change_password')
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'UlinziTracker/change_password.html', {'form': form})

def change_password_g(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated!')
            return redirect('UlinziTracker:change_password_g')
        else:
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'UlinziTracker/change_password_g.html', {'form': form})

# --- User registration ---
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            new_user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = new_user
            profile.save()
            messages.success(request, 'Registered Successfully')
            return redirect('UlinziTracker:login')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    return render(request, 'UlinziTracker/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_update_form = UserProfileUpdateForm(request.POST, instance=profile)
        if p_form.is_valid() and profile_update_form.is_valid():
            user = p_form.save()
            profile = profile_update_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Updated Successfully')
            return redirect('UlinziTracker:dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_update_form = UserProfileUpdateForm(instance=profile)

    context = {
        'p_form': p_form,
        'profile_update_form': profile_update_form,
        'role': profile.role  # pass role to template for conditional rendering
    }
    return render(request, 'UlinziTracker/dashboard.html', context)

# --- Incident submission ---
@login_required
def incidents(request):
    if request.user.profile.role != 'resident':
        messages.error(request, "Only residents can report incidents.")
        return redirect('UlinziTracker:dashboard')

    if request.method == 'POST':
        incident_form = IncidentForm(request.POST, request.FILES)
        if incident_form.is_valid():
            instance = incident_form.save(commit=False)
            instance.reporter = request.user
            instance.save()
            messages.success(request, 'Your incident has been registered with multimedia evidence!')
            return redirect('UlinziTracker:incident_list')
    else:
        incident_form = IncidentForm()

    return render(request, 'UlinziTracker/incident_form.html', {'incident_form': incident_form})

@login_required
def incident_list(request):
    role = request.user.profile.role
    if role == 'resident':
        incidents = Incident.objects.filter(reporter=request.user)
    else:
        # Officers, chiefs, admins see all incidents
        incidents = Incident.objects.all()
    return render(request, 'UlinziTracker/AllIncidents.html', {'c': incidents})

@login_required
def solved_incidents(request):
    role = request.user.profile.role
    if role in ['officer', 'chief', 'admin']:
        incidents = Incident.objects.filter(status='resolved')
    else:
        incidents = Incident.objects.filter(status='resolved', reporter=request.user)
    return render(request, 'UlinziTracker/resolvedIncidents.html', {'result': incidents})

@login_required
def allincidents(request):
    role = request.user.profile.role
    if role in ['officer', 'chief', 'admin']:
        incidents = Incident.objects.all()
    else:
        messages.error(request, "You are not authorized to view all incidents.")
        return redirect('UlinziTracker:incident_list')
    return render(request, 'UlinziTracker/AllIncidents.html', {'c': incidents})

def pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=incident_id.pdf'
    p = canvas.Canvas(response, pagesize=A4)
    cid = request.POST.get('cid')
    incident = get_object_or_404(Incident, id=cid)

    p.drawString(25, 770, "Incident Report")
    p.drawString(30, 750, f"Reporter: {incident.reporter.username}")
    p.drawString(30, 730, f"Category: {incident.get_category_display()}")
    p.drawString(30, 710, f"Status: {incident.get_status_display()}")
    p.drawString(30, 690, f"Location: {incident.location}")
    p.drawString(30, 670, f"Time Reported: {incident.time_reported.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(30, 650, "Description:")
    p.drawString(30, 630, incident.description)
    p.showPage()
    p.save()
    return response

def choose_login(request):
    return render(request, 'UlinziTracker/login_choice.html')

@login_required
def pending_incidents(request):
    role = request.user.profile.role

    # Officers, chiefs, admins can see ALL pending incidents
    if role in ['officer', 'chief', 'admin']:
        incidents = Incident.objects.filter(status='pending')
    else:
        # Residents only see their own pending incidents
        incidents = Incident.objects.filter(status='pending', reporter=request.user)

    return render(request, 'UlinziTracker/pendingIncidents.html', {'result': incidents})
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('UlinziTracker:index')  # or 'UlinziTracker:choose_login'
