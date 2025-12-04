from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('signin/', auth_views.LoginView.as_view(template_name='UlinziTracker/signin.html'), name='signin'),
    path('logout/', auth_views.LogoutView.as_view(template_name='UlinziTracker/logout.html'), name='logout'),

    path('password/', views.change_password, name='change_password'),
    path('passwords/', views.change_password_g, name='change_password_g'),

    path('reportincident/', views.reportincident, name='reportincident'),
    path('solved/', views.solved_incidents, name='solved_incidents'),  # updated

    path('login/', views.login, name='login'),
    path('incidents/', views.incidents, name='incidents'),  # incident submission
    path('allincidents/', views.allincidents, name='allincidents'),  # all incidents list
    path('incident-list/', views.incident_list, name='incident_list'),  # user’s incidents
    path('pdf/', views.pdf_view, name='pdf_view'),
    #path('pdf_g/', views.pdf_viewer, name='pdf_viewer'),
    path('aboutus/', views.aboutus, name='aboutus'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Password reset flow ---
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='UlinziTracker/password_reset.html'
        ),
        name='password_reset'
    ),
    path('password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='UlinziTracker/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='UlinziTracker/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='UlinziTracker/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
