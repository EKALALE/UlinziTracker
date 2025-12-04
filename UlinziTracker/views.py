from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Profile, Incident
from .forms import (
    UserRegisterForm,
    ProfileUpdateForm,
    UserProfileForm,
    UserProfileUpdateForm,
    IncidentForm,
    StatusUpdateForm
)

# --- Page loading ---
def index(request):
    return render(request, "UlinziTracker/home.html")

def aboutus(request):
    return render(request, "UlinziTracker/aboutus.html")

def login(request):
    return render(request, "UlinziTracker/login.html")

def signin(request):
    return render(request, "UlinziTracker/signin.html")

# --- reportincident for incidents ---
def reportincident(request):
    total = Incident.objects.report()
    pending = Incident.objects.filter(status='pending').report()
    resolved = Incident.objects.filter(status='resolved').report()
    inprogress = Incident.objects.filter(status='in_progress').report()

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
    return render(request, "UlinziTracker/counter.html", context)

# --- Change password ---
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
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
            return redirect('change_password_g')
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
            return redirect('/login/')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    return render(request, 'UlinziTracker/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def dashboard(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_update_form = UserProfileUpdateForm(request.POST, instance=request.user.profile)
        if p_form.is_valid() and profile_update_form.is_valid():
            user = p_form.save()
            profile = profile_update_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Updated Successfully')
            return redirect('dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_update_form = UserProfileUpdateForm(instance=request.user.profile)
    context = {'p_form': p_form, 'profile_update_form': profile_update_form}
    return render(request, 'UlinziTracker/dashboard.html', context)

# --- Incident submission ---
@login_required
def incidents(request):
    if request.method == 'POST':
        incident_form = IncidentForm(request.POST)
        if incident_form.is_valid():
            instance = incident_form.save(commit=False)
            instance.reporter = request.user
            instance.save()
            messages.success(request, 'Your incident has been registered!')
            return redirect('incident_list')
    else:
        incident_form = IncidentForm()
    return render(request, 'UlinziTracker/incident_form.html', {'incident_form': incident_form})


# --- User incident list ---
@login_required
def incident_list(request):
    incidents = Incident.objects.filter(reporter=request.user)
    return render(request, 'UlinziTracker/AllIncidents.html', {'c': incidents})

# --- Solved incidents ---
@login_required
def solved_incidents(request):
    incidents = Incident.objects.filter(status='resolved')
    return render(request, 'UlinziTracker/solvedIncidents.html', {'result': incidents})

@login_required # --- added....
def allincidents(request):
    incidents = Incident.objects.all()
    return render(request, 'UlinziTracker/AllIncidents.html', {'c': incidents})

# --- PDF generation ---
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
