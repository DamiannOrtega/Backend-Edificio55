# gestion/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_reservations
from . import views_panel_vespertino

urlpatterns = [
    path('', views.pagina_registro, name='registro'),
    path('finalizar/', views.finalizar_visita, name='finalizar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/buscar-estudiante/', views.buscar_estudiante, name='api_buscar_estudiante'),
    path('api/opciones-dinamicas/', views.opciones_dinamicas, name='api_opciones'),
    path('api/carreras/', views.api_carreras, name='api_carreras'),
    path('api/registrar-visita/', views.registrar_visita_api, name='api_registrar_visita'),
    path('api/finalizar-visita/', views.finalizar_visita_api, name='api_finalizar_visita'),
    
    # APIs de autenticación para reportes
    path('api/admin/login/', views.api_admin_login, name='api_admin_login'),
    path('api/admin/verify/', views.api_admin_verify, name='api_admin_verify'),
    
    # APIs para dashboard React
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/lab-usage/', views.api_lab_usage, name='api_lab_usage'),
    path('api/dashboard/software-usage/', views.api_software_usage, name='api_software_usage'),
    path('api/dashboard/visits-timeline/', views.api_visits_timeline, name='api_visits_timeline'),
    path('api/dashboard/recent-visits/', views.api_recent_visits, name='api_recent_visits'),
    
    # APIs para reportes filtrados
    path('api/reports/filtered-stats/', views.api_reports_filtered_stats, name='api_reports_filtered_stats'),
    path('api/reports/lab-usage/', views.api_reports_lab_usage, name='api_reports_lab_usage'),
    path('api/reports/software-usage/', views.api_reports_software_usage, name='api_reports_software_usage'),
    path('api/reports/daily-trend/', views.api_reports_daily_trend, name='api_reports_daily_trend'),
    path('api/reports/top-users/', views.api_reports_top_users, name='api_reports_top_users'),
    path('api/reports/laboratories-list/', views.api_reports_laboratories_list, name='api_reports_laboratories_list'),
    path('api/reports/software-list/', views.api_reports_software_list, name='api_reports_software_list'),
    
    # APIs para exportación
    path('api/export/pdf/', views.api_export_pdf, name='api_export_pdf'),
    path('api/export/excel/', views.api_export_excel, name='api_export_excel'),
    
    # APIs para estadísticas de reservas
    path('api/reservations/stats/', views_reservations.api_reservations_stats, name='api_reservations_stats'),
    path('api/reservations/by-carrera/', views_reservations.api_reservations_by_carrera, name='api_reservations_by_carrera'),
    path('api/reservations/by-semester/', views_reservations.api_reservations_by_semester, name='api_reservations_by_semester'),
    path('api/reservations/lab-usage/', views_reservations.api_reservations_lab_usage, name='api_reservations_lab_usage'),
    path('api/reservations/timeline/', views_reservations.api_reservations_timeline, name='api_reservations_timeline'),
    path('api/reservations/list-carreras/', views_reservations.api_reservations_list_carreras, name='api_reservations_list_carreras'),
    path('api/reservations/list-semestres/', views_reservations.api_reservations_list_semestres, name='api_reservations_list_semestres'),
    path('api/reservations/list-laboratorios/', views_reservations.api_reservations_list_laboratorios, name='api_reservations_list_laboratorios'),
    path('api/reservations/occupancy/', views_reservations.api_reservations_occupancy, name='api_reservations_occupancy'),
    
    # Panel Vespertino
    path('panel-vespertino/', views_panel_vespertino.panel_vespertino_home, name='panel_vespertino_home'),
    path('panel-vespertino/login/', auth_views.LoginView.as_view(template_name='panel_vespertino/login.html'), name='panel_vespertino_login'),
    path('panel-vespertino/logout/', auth_views.LogoutView.as_view(next_page='/panel-vespertino/login/'), name='panel_vespertino_logout'),
    path('panel-vespertino/mantenimientos/', views_panel_vespertino.panel_mantenimientos, name='panel_mantenimientos'),
    path('panel-vespertino/sesiones/', views_panel_vespertino.panel_sesiones_activas, name='panel_sesiones_activas'),
    
    # APIs Panel Vespertino
    path('panel-vespertino/api/sesiones-activas/', views_panel_vespertino.api_obtener_sesiones_activas, name='api_sesiones_activas'),
    path('panel-vespertino/api/finalizar-sesion/', views_panel_vespertino.api_finalizar_sesion, name='api_finalizar_sesion'),
    path('panel-vespertino/api/finalizar-sesiones-lab/', views_panel_vespertino.api_finalizar_sesiones_laboratorio, name='api_finalizar_sesiones_lab'),
    path('panel-vespertino/api/pcs-laboratorio/', views_panel_vespertino.api_obtener_pcs_laboratorio, name='api_pcs_laboratorio'),
    path('panel-vespertino/api/registrar-mantenimiento/', views_panel_vespertino.api_registrar_mantenimiento, name='api_registrar_mantenimiento'),
]