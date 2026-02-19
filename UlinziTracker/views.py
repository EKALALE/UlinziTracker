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
        # Pass the user into the forms so they know who is editing
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_update_form = UserProfileUpdateForm(request.POST, instance=profile, user=request.user)

        if p_form.is_valid() and profile_update_form.is_valid():
            user = p_form.save()
            profile = profile_update_form.save(commit=False)

            # Enforce role immutability unless superuser
            if not request.user.is_superuser:
                # Reset role back to original if someone tried to change it
                original_role = Profile.objects.get(pk=profile.pk).role
                profile.role = original_role

            profile.user = user
            profile.save()

            messages.success(request, 'Updated Successfully')
            return redirect('UlinziTracker:dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_update_form = UserProfileUpdateForm(instance=profile, user=request.user)

    # ✅ NEW: add incidents for residents
    if request.user.profile.role == 'resident':
        incidents = Incident.objects.filter(reporter=request.user)
    else:
        incidents = Incident.objects.none()

    context = {
        'p_form': p_form,
        'profile_update_form': profile_update_form,
        'role': profile.role,   # existing
        'incidents': incidents  # new
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

@login_required
def pdf_view(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=incident_{incident.id}.pdf'
    p = canvas.Canvas(response, pagesize=A4)

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
    return redirect('UlinziTracker:login')  # or 'UlinziTracker:choose_login'

@login_required
def edit_incident(request, id):
    incident = get_object_or_404(Incident, id=id)

    # Residents: only edit if pending
    if request.user == incident.reporter and incident.status != 'pending':
        messages.error(request, "You can only edit pending incidents.")
        return redirect('UlinziTracker:incident_list')

    # Non-reporters: only superuser/admin can edit
    if request.user != incident.reporter and not request.user.is_superuser and request.user.profile.role != 'admin':
        messages.error(request, "You are not authorized to edit this incident.")
        return redirect('UlinziTracker:incident_list')

    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "Incident updated successfully.")
            return redirect('UlinziTracker:incident_list')
    else:
        form = IncidentForm(instance=incident)

    return render(request, 'UlinziTracker/edit_incident.html', {'form': form})


@login_required
def update_status(request, id):
    incident = get_object_or_404(Incident, id=id)

    # Allow superuser, admin, or officer
    if not (request.user.is_superuser or request.user.profile.role in ['admin', 'officer']):
        messages.error(request, "You are not authorized to update this incident.")
        return redirect('UlinziTracker:incident_list')

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "Status updated successfully.")
            return redirect('UlinziTracker:incident_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StatusUpdateForm(instance=incident)

    return render(request, 'UlinziTracker/update_status.html', {'form': form, 'incident': incident})


@login_required
def delete_incident(request, id):
    incident = get_object_or_404(Incident, id=id)

    # Residents: only delete if pending
    if request.user == incident.reporter and incident.status != 'pending':
        messages.error(request, "You can only delete pending incidents.")
        return redirect('UlinziTracker:incident_list')

    # Non-reporters: only superuser/admin can delete
    if request.user != incident.reporter and not request.user.is_superuser and request.user.profile.role != 'admin':
        messages.error(request, "You are not authorized to delete this incident.")
        return redirect('UlinziTracker:incident_list')

    if request.method == 'POST':
        incident.delete()
        messages.success(request, "Incident deleted successfully.")
        return redirect('UlinziTracker:incident_list')

    return render(request, 'UlinziTracker/delete_incident.html', {'incident': incident})

def redirect_after_login(user):
    if user.is_superuser or user.profile.role == 'admin':
        return 'UlinziTracker:dashboard'   # Admin dashboard
    elif user.profile.role == 'officer':
        return 'UlinziTracker:incident_list'   # Officers see all incidents
    elif user.profile.role == 'chief':
        return 'UlinziTracker:incidentStats'   # Chiefs see analytics
    elif user.profile.role == 'authority':
        return 'UlinziTracker:incidentStats'   # Authorities also see analytics
    else:  # resident
        return 'UlinziTracker:incident_list'   # Residents see only their own incidents



from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Use the helper function to send them to the right dashboard
            return redirect(redirect_after_login(user))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'UlinziTracker/login.html', {'form': form})

@login_required
def confirm_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)

    if request.user.profile.role == 'officer':
        if request.method == 'POST':
            note = request.POST.get('response_notes')
            incident.status = 'confirmed'
            incident.confirmed_by = request.user
            incident.response_notes = note
            incident.save()
            messages.success(request, f"Incident {incident.id} confirmed with response.")
            return redirect('UlinziTracker:pending_incidents')
    else:
        messages.error(request, "Only officers can confirm incidents.")
        return redirect('UlinziTracker:pending_incidents')

    return render(request, 'UlinziTracker/confirm_incident.html', {'incident': incident})

@login_required
def resolve_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)

    # Only officers can resolve
    if request.user.profile.role != 'officer':
        messages.error(request, "Only officers can resolve incidents.")
        return redirect('UlinziTracker:pending_incidents')

    # Mark as resolved
    incident.status = 'resolved'
    incident.save()

    messages.success(request, f"Incident {incident.id} has been marked as resolved.")
    return redirect('UlinziTracker:solved_incidents')
