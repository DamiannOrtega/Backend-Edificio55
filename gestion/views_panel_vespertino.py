"""
Vistas para el Panel del Turno Vespertino
Panel simplificado con acceso limitado a:
- Gestión de mantenimientos
- Finalización de sesiones activas
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import Visita, PC, Mantenimiento, Laboratorio
import json


def es_turno_vespertino(user):
    """Verifica si el usuario pertenece al grupo Turno Vespertino"""
    return user.groups.filter(name='Turno Vespertino').exists() or user.is_superuser


@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def panel_vespertino_home(request):
    """Vista principal del panel vespertino"""
    context = {
        'usuario': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'panel_vespertino/home.html', context)


@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def panel_mantenimientos(request):
    """Vista de gestión de mantenimientos"""
    laboratorios = Laboratorio.objects.all().order_by('nombre')
    
    # Obtener mantenimientos recientes (últimos 10)
    mantenimientos_recientes = Mantenimiento.objects.select_related(
        'pc', 'pc__laboratorio'
    ).order_by('-fecha_hora')[:10]
    
    context = {
        'laboratorios': laboratorios,
        'mantenimientos_recientes': mantenimientos_recientes,
    }
    return render(request, 'panel_vespertino/mantenimientos.html', context)


@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def panel_sesiones_activas(request):
    """Vista de sesiones activas"""
    laboratorios = Laboratorio.objects.all().order_by('nombre')
    
    context = {
        'laboratorios': laboratorios,
    }
    return render(request, 'panel_vespertino/sesiones_activas.html', context)


# ============ APIs ============

@csrf_exempt
@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def api_obtener_sesiones_activas(request):
    """API para obtener sesiones activas"""
    try:
        laboratorio_id = request.GET.get('laboratorio', 'all')
        
        # Filtrar sesiones activas (sin hora de salida)
        sesiones = Visita.objects.filter(
            hora_salida__isnull=True
        ).select_related('estudiante', 'pc', 'pc__laboratorio').order_by('-hora_entrada')
        
        # Filtrar por laboratorio si se especifica
        if laboratorio_id != 'all':
            sesiones = sesiones.filter(pc__laboratorio__id=laboratorio_id)
        
        # Preparar datos
        sesiones_data = []
        for sesion in sesiones:
            tiempo_transcurrido = timezone.now() - sesion.hora_entrada
            horas = int(tiempo_transcurrido.total_seconds() // 3600)
            minutos = int((tiempo_transcurrido.total_seconds() % 3600) // 60)
            
            sesiones_data.append({
                'id': sesion.id,
                'estudiante': sesion.estudiante.nombre_completo,
                'id_estudiante': sesion.estudiante.id_estudiante,
                'pc': sesion.pc.numero_pc,
                'laboratorio': sesion.pc.laboratorio.nombre,
                'laboratorio_id': sesion.pc.laboratorio.id,
                'hora_entrada': sesion.hora_entrada.strftime('%H:%M'),
                'tiempo_transcurrido': f'{horas}h {minutos}m',
                'tiempo_minutos': int(tiempo_transcurrido.total_seconds() // 60),
            })
        
        return JsonResponse({
            'success': True,
            'sesiones': sesiones_data,
            'total': len(sesiones_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def api_finalizar_sesion(request):
    """API para finalizar una sesión individual"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        visita_id = data.get('visita_id')
        
        if not visita_id:
            return JsonResponse({'success': False, 'error': 'ID de visita requerido'}, status=400)
        
        # Obtener la visita
        visita = Visita.objects.get(id=visita_id, hora_salida__isnull=True)
        
        # Finalizar la sesión
        visita.hora_salida = timezone.now()
        visita.save()
        
        # Liberar la PC
        if visita.pc:
            visita.pc.en_uso = False
            visita.pc.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Sesión de {visita.estudiante.nombre_completo} finalizada correctamente'
        })
        
    except Visita.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sesión no encontrada o ya finalizada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def api_finalizar_sesiones_laboratorio(request):
    """API para finalizar todas las sesiones de un laboratorio"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        laboratorio_id = data.get('laboratorio_id')
        
        if not laboratorio_id:
            return JsonResponse({'success': False, 'error': 'ID de laboratorio requerido'}, status=400)
        
        # Obtener sesiones activas del laboratorio
        sesiones = Visita.objects.filter(
            pc__laboratorio__id=laboratorio_id,
            hora_salida__isnull=True
        )
        
        count = sesiones.count()
        
        # Finalizar todas las sesiones
        hora_actual = timezone.now()
        for sesion in sesiones:
            sesion.hora_salida = hora_actual
            sesion.save()
            
            # Liberar PC
            if sesion.pc:
                sesion.pc.en_uso = False
                sesion.pc.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'{count} sesiones finalizadas correctamente',
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def api_obtener_pcs_laboratorio(request):
    """API para obtener PCs de un laboratorio"""
    try:
        laboratorio_id = request.GET.get('laboratorio')
        
        if not laboratorio_id:
            return JsonResponse({'success': False, 'error': 'ID de laboratorio requerido'}, status=400)
        
        pcs = PC.objects.filter(
            laboratorio__id=laboratorio_id
        ).order_by('numero_pc')
        
        pcs_data = [{
            'id': pc.id,
            'numero_pc': pc.numero_pc,
            'en_uso': pc.en_uso,
        } for pc in pcs]
        
        return JsonResponse({
            'success': True,
            'pcs': pcs_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@user_passes_test(es_turno_vespertino, login_url='/panel-vespertino/login/')
def api_registrar_mantenimiento(request):
    """API para registrar un mantenimiento"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        pc_id = data.get('pc_id')
        tipo = data.get('tipo')
        descripcion = data.get('descripcion', '')
        
        if not pc_id or not tipo:
            return JsonResponse({
                'success': False,
                'error': 'PC y tipo de mantenimiento son requeridos'
            }, status=400)
        
        # Obtener la PC
        pc = PC.objects.get(id=pc_id)
        
        # Crear el mantenimiento
        mantenimiento = Mantenimiento.objects.create(
            pc=pc,
            tipo_mantenimiento=tipo,
            descripcion=descripcion,
            fecha_hora=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Mantenimiento registrado para {pc.numero_pc}',
            'mantenimiento_id': mantenimiento.id
        })
        
    except PC.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PC no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
