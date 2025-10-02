# gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_registro, name='registro'),
    path('finalizar/', views.finalizar_visita, name='finalizar'),
    path('dashboard/', views.dashboard, name='dashboard'), # <-- AÑADE ESTA LÍNEA
    path('api/buscar-estudiante/', views.buscar_estudiante, name='api_buscar_estudiante'),
    path('api/opciones-dinamicas/', views.opciones_dinamicas, name='api_opciones'),
    path('api/registrar-visita/', views.registrar_visita_api, name='api_registrar_visita'),
    path('api/finalizar-visita/', views.finalizar_visita_api, name='api_finalizar_visita'),
]