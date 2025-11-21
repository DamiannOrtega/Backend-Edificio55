# gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_registro, name='registro'),
    path('finalizar/', views.finalizar_visita, name='finalizar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/buscar-estudiante/', views.buscar_estudiante, name='api_buscar_estudiante'),
    path('api/opciones-dinamicas/', views.opciones_dinamicas, name='api_opciones'),
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
]