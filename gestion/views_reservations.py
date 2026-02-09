"""
API endpoints para estadísticas de reservas
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import ReservaClase, SerieReserva, Laboratorio
from .views import admin_required_api


@csrf_exempt
@admin_required_api
def api_reservations_stats(request):
    """API para obtener estadísticas generales de reservas"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        laboratory = request.GET.get('laboratory', 'all')
        carrera = request.GET.get('carrera', 'all')
        semestre = request.GET.get('semestre', 'all')
        
        # Construir filtros base
        filters = Q()
        
        # Filtro por fechas
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        
        # Filtro por laboratorio
        if laboratory != 'all':
            filters &= Q(laboratorio__id=laboratory)
        
        # Filtro por carrera
        if carrera != 'all':
            filters &= Q(carrera=carrera)
        
        # Filtro por semestre
        if semestre != 'all':
            filters &= Q(semestre=int(semestre))
        
        # Aplicar filtros
        reservas_filtradas = ReservaClase.objects.filter(filters)
        
        # Calcular estadísticas
        total_reservas = reservas_filtradas.count()
        total_alumnos = reservas_filtradas.aggregate(
            total=Sum('numero_alumnos')
        )['total'] or 0
        
        promedio_alumnos = reservas_filtradas.aggregate(
            promedio=Avg('numero_alumnos')
        )['promedio'] or 0
        
        # Carreras únicas
        carreras_unicas = reservas_filtradas.exclude(
            carrera__isnull=True
        ).exclude(
            carrera=''
        ).values('carrera').distinct().count()
        
        # Laboratorios más usados
        labs_mas_usados = reservas_filtradas.values(
            'laboratorio__nombre'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return JsonResponse({
            'total_reservas': total_reservas,
            'total_alumnos': int(total_alumnos),
            'promedio_alumnos': round(promedio_alumnos, 1),
            'carreras_unicas': carreras_unicas,
            'labs_mas_usados': list(labs_mas_usados)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_by_carrera(request):
    """API para obtener reservas agrupadas por carrera"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        laboratory = request.GET.get('laboratory', 'all')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        if laboratory != 'all':
            filters &= Q(laboratorio__id=laboratory)
        
        # Obtener datos agrupados por carrera
        carreras_stats = ReservaClase.objects.filter(filters).exclude(
            carrera__isnull=True
        ).exclude(
            carrera=''
        ).values('carrera').annotate(
            total_reservas=Count('id'),
            total_alumnos=Sum('numero_alumnos')
        ).order_by('-total_reservas')
        
        data = []
        for carrera in carreras_stats:
            data.append({
                'carrera': carrera['carrera'],
                'reservas': carrera['total_reservas'],
                'alumnos': carrera['total_alumnos'] or 0
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_by_semester(request):
    """API para obtener reservas agrupadas por semestre"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        carrera = request.GET.get('carrera', 'all')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        if carrera != 'all':
            filters &= Q(carrera=carrera)
        
        # Obtener datos agrupados por semestre
        semestres_stats = ReservaClase.objects.filter(filters).exclude(
            semestre__isnull=True
        ).values('semestre').annotate(
            total_reservas=Count('id'),
            total_alumnos=Sum('numero_alumnos')
        ).order_by('semestre')
        
        data = []
        for semestre in semestres_stats:
            data.append({
                'semestre': semestre['semestre'],
                'reservas': semestre['total_reservas'],
                'alumnos': semestre['total_alumnos'] or 0
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_lab_usage(request):
    """API para obtener uso de laboratorios por carrera"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        
        # Obtener datos agrupados por laboratorio y carrera
        lab_carrera_stats = ReservaClase.objects.filter(filters).exclude(
            carrera__isnull=True
        ).exclude(
            carrera=''
        ).values('laboratorio__nombre', 'carrera').annotate(
            total_reservas=Count('id'),
            total_alumnos=Sum('numero_alumnos')
        ).order_by('laboratorio__nombre', '-total_reservas')
        
        # Organizar datos por laboratorio
        labs_data = {}
        for item in lab_carrera_stats:
            lab_nombre = item['laboratorio__nombre']
            if lab_nombre not in labs_data:
                labs_data[lab_nombre] = []
            
            labs_data[lab_nombre].append({
                'carrera': item['carrera'],
                'reservas': item['total_reservas'],
                'alumnos': item['total_alumnos'] or 0
            })
        
        return JsonResponse({'data': labs_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': {}}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_timeline(request):
    """API para obtener línea de tiempo de reservas"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        laboratory = request.GET.get('laboratory', 'all')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        if laboratory != 'all':
            filters &= Q(laboratorio__id=laboratory)
        
        # Obtener reservas por día
        reservas_por_dia = ReservaClase.objects.filter(filters).extra(
            select={'day': 'date(fecha_hora_inicio)'}
        ).values('day').annotate(
            count=Count('id'),
            total_alumnos=Sum('numero_alumnos')
        ).order_by('day')
        
        data = []
        for item in reservas_por_dia:
            data.append({
                'fecha': str(item['day']),
                'reservas': item['count'],
                'alumnos': item['total_alumnos'] or 0
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_list_carreras(request):
    """API para obtener lista de carreras únicas"""
    
    try:
        carreras = ReservaClase.objects.exclude(
            carrera__isnull=True
        ).exclude(
            carrera=''
        ).values_list('carrera', flat=True).distinct().order_by('carrera')
        
        return JsonResponse({'carreras': list(carreras)})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'carreras': []}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_list_semestres(request):
    """API para obtener lista de semestres únicos"""
    
    try:
        semestres = ReservaClase.objects.exclude(
            semestre__isnull=True
        ).values_list('semestre', flat=True).distinct().order_by('semestre')
        
        return JsonResponse({'semestres': list(semestres)})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'semestres': []}, status=500)


@csrf_exempt
@admin_required_api
def api_reservations_list_laboratorios(request):
    """API para obtener lista de todos los laboratorios"""
    
    try:
        laboratorios = Laboratorio.objects.all().order_by('nombre').values('id', 'nombre')
        
        return JsonResponse({'laboratories': list(laboratorios)})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'laboratories': []}, status=500)
