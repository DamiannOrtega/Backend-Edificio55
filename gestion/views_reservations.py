"""
API endpoints para estadísticas de reservas
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta, date, datetime
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


@csrf_exempt
@admin_required_api
def api_reservations_occupancy(request):
    """
    API para calcular horas ocupadas y libres de laboratorios por período.
    Considera todas las ReservaClase (individuales y generadas por series).

    Parámetros:
        date_from  : fecha inicio (YYYY-MM-DD)
        date_to    : fecha fin    (YYYY-MM-DD)
        laboratory : id del laboratorio o 'all'
        group_by   : 'week' | 'month'
        hours_per_day : horas laborales por día (default 8)
    """
    try:
        date_from_str = request.GET.get('date_from')
        date_to_str   = request.GET.get('date_to')
        laboratory    = request.GET.get('laboratory', 'all')
        group_by      = request.GET.get('group_by', 'week')   # 'week' | 'month'
        hours_per_day = float(request.GET.get('hours_per_day', 8))

        # ---- Validar fechas ----
        if not date_from_str or not date_to_str:
            # Usar último mes por defecto
            today = date.today()
            date_to_obj   = today
            date_from_obj = today.replace(day=1)
        else:
            date_from_obj = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to_obj   = datetime.strptime(date_to_str,   '%Y-%m-%d').date()

        # ---- Cuántos laboratorios se consideran para las horas disponibles ----
        if laboratory == 'all':
            num_labs = Laboratorio.objects.count() or 1
        else:
            num_labs = 1

        # ---- Filtrar reservas ----
        filters = Q(
            fecha_hora_inicio__date__lte=date_to_obj,
            fecha_hora_fin__date__gte=date_from_obj
        )
        if laboratory != 'all':
            filters &= Q(laboratorio__id=laboratory)

        reservas = ReservaClase.objects.filter(filters).values(
            'fecha_hora_inicio', 'fecha_hora_fin'
        )

        # ---- Construir dict de horas ocupadas por período ----
        # Clave del período: 'YYYY-WNN' para semana, 'YYYY-MM' para mes
        horas_ocupadas_por_periodo = {}

        for r in reservas:
            inicio = r['fecha_hora_inicio']
            fin    = r['fecha_hora_fin']

            # Asegurarnos de que son datetime con timezone aware
            if timezone.is_naive(inicio):
                inicio = timezone.make_aware(inicio)
            if timezone.is_naive(fin):
                fin = timezone.make_aware(fin)

            # Recortar al rango solicitado
            range_start = timezone.make_aware(
                datetime.combine(date_from_obj, datetime.min.time())
            )
            range_end = timezone.make_aware(
                datetime.combine(date_to_obj, datetime.max.time())
            )
            inicio = max(inicio, range_start)
            fin    = min(fin,    range_end)

            if fin <= inicio:
                continue

            # Distribuir la duración entre los períodos que abarca
            cursor = inicio
            while cursor < fin:
                # Determinar la clave de período del cursor
                cursor_date = cursor.date()
                if group_by == 'month':
                    periodo_key   = cursor_date.strftime('%Y-%m')
                    # Fin del período actual
                    if cursor_date.month == 12:
                        next_month_start = date(cursor_date.year + 1, 1, 1)
                    else:
                        next_month_start = date(cursor_date.year, cursor_date.month + 1, 1)
                    periodo_end = timezone.make_aware(
                        datetime.combine(next_month_start, datetime.min.time())
                    )
                else:  # week
                    iso_year, iso_week, _ = cursor_date.isocalendar()
                    periodo_key = f'{iso_year}-W{iso_week:02d}'
                    # Lunes de la semana siguiente
                    days_to_next_monday = 7 - cursor_date.weekday()
                    next_monday = cursor_date + timedelta(days=days_to_next_monday)
                    periodo_end = timezone.make_aware(
                        datetime.combine(next_monday, datetime.min.time())
                    )

                # El segmento de esta reserva que cae en este período
                segment_end = min(fin, periodo_end)
                horas_segmento = (segment_end - cursor).total_seconds() / 3600.0

                horas_ocupadas_por_periodo[periodo_key] = (
                    horas_ocupadas_por_periodo.get(periodo_key, 0.0) + horas_segmento
                )

                cursor = periodo_end

        # ---- Generar lista de períodos en el rango (aunque no tengan reservas) ----
        periodos_resultado = []
        cursor_date = date_from_obj

        seen_periods = set()

        while cursor_date <= date_to_obj:
            if group_by == 'month':
                periodo_key  = cursor_date.strftime('%Y-%m')
                label_str    = cursor_date.strftime('%b %Y')  # ej: Mar 2025
                # Avanzar al primer día del mes siguiente
                if cursor_date.month == 12:
                    cursor_date = date(cursor_date.year + 1, 1, 1)
                else:
                    cursor_date = date(cursor_date.year, cursor_date.month + 1, 1)
            else:  # week
                iso_year, iso_week, iso_dow = cursor_date.isocalendar()
                periodo_key = f'{iso_year}-W{iso_week:02d}'
                # Inicio y fin de la semana para el label
                week_start  = cursor_date - timedelta(days=iso_dow - 1)
                week_end    = week_start + timedelta(days=6)
                label_str   = f'Sem. {iso_week} ({week_start.strftime("%d %b")}–{week_end.strftime("%d %b")})'
                # Avanzar a la semana siguiente
                cursor_date = week_start + timedelta(days=7)

            if periodo_key in seen_periods:
                continue
            seen_periods.add(periodo_key)

            # Calcular horas disponibles para este período
            # Contar días laborables (L-V) dentro del período que caen en el rango
            if group_by == 'month':
                # El período va del primer al último día del mes, intersectado con el rango
                year_m, month_m = map(int, periodo_key.split('-'))
                if month_m == 12:
                    month_end = date(year_m + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = date(year_m, month_m + 1, 1) - timedelta(days=1)
                period_range_start = max(date(year_m, month_m, 1), date_from_obj)
                period_range_end   = min(month_end, date_to_obj)
            else:
                # La semana va del lunes al domingo
                w_year, w_week = int(iso_year), int(iso_week)
                week_mon = date.fromisocalendar(w_year, w_week, 1)
                week_sun = date.fromisocalendar(w_year, w_week, 7)
                period_range_start = max(week_mon, date_from_obj)
                period_range_end   = min(week_sun, date_to_obj)

            dias_laborables = sum(
                1 for i in range((period_range_end - period_range_start).days + 1)
                if (period_range_start + timedelta(days=i)).weekday() < 5  # L-V
            )
            horas_disponibles = dias_laborables * hours_per_day * num_labs

            h_ocupadas = round(horas_ocupadas_por_periodo.get(periodo_key, 0.0), 2)
            h_libres   = round(max(0.0, horas_disponibles - h_ocupadas), 2)

            periodos_resultado.append({
                'periodo': periodo_key,
                'label':   label_str,
                'horas_ocupadas':    h_ocupadas,
                'horas_libres':      h_libres,
                'horas_disponibles': round(horas_disponibles, 2),
            })

        # ---- Totales globales ----
        total_ocupadas    = round(sum(p['horas_ocupadas']    for p in periodos_resultado), 2)
        total_disponibles = round(sum(p['horas_disponibles'] for p in periodos_resultado), 2)
        total_libres      = round(max(0.0, total_disponibles - total_ocupadas), 2)
        pct_ocupacion     = round((total_ocupadas / total_disponibles * 100) if total_disponibles > 0 else 0, 1)

        return JsonResponse({
            'periodos': periodos_resultado,
            'totales': {
                'horas_ocupadas':    total_ocupadas,
                'horas_libres':      total_libres,
                'horas_disponibles': total_disponibles,
                'porcentaje_ocupacion': pct_ocupacion,
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'periodos': [], 'totales': {}}, status=500)
