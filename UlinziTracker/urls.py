from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = "UlinziTracker"

urlpatterns = [
    # Core pages
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.dashboard, name='profile'),


    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),   # use custom login view
    path('logout/', views.logout_view, name='logout'),
    path('password/', views.change_password, name='change_password'),
    path('passwords/', views.change_password_g, name='change_password_g'),

    # Incidents
    path('incidents/', views.incidents, name='incidents'),
    path('incident-list/', views.incident_list, name='incident_list'),
    path('allincidents/', views.allincidents, name='allincidents'),
    path('incidents/resolved/', views.solved_incidents, name='resolved_incidents'),
    path('incidentStats/', views.incidentStats, name='incidentStats'),
    path('incidents/pending/', views.pending_incidents, name='pending_incidents'),
    path('incidents/<int:incident_id>/confirm/', views.confirm_incident, name='confirm_incident'),


    # Incident actions
    path('incidents/edit/<int:id>/', views.edit_incident, name='edit_incident'),
    path('incidents/update/<int:id>/', views.update_status, name='update_status'),
    path('incidents/delete/<int:id>/', views.delete_incident, name='delete_incident'),

    # PDF export
    path('pdf/', views.pdf_view, name='pdf_view'),

    # Password reset flow
    path('password-reset/',
        auth_views.PasswordResetView.as_view(template_name='UlinziTracker/password_reset.html'),
        name='password_reset'
    ),
    path('password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(template_name='UlinziTracker/password_reset_done.html'),
        name='password_reset_done'
    ),
    re_path(
        r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='UlinziTracker/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='UlinziTracker/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
