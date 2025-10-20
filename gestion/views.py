from django.shortcuts import render
from django.http import JsonResponse
# ASÍ DEBE QUEDAR
from .models import Laboratorio, Software, PC, Estudiante, Visita, ReservaClase, SerieReserva
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json
from django.views.decorators.csrf import csrf_exempt


def pagina_registro(request):
    # El bloque POST para registrar la visita no cambia
    if request.method == 'POST':
        # ... (todo el código para registrar una visita que ya tenías) ...

        # (El código completo del bloque POST para claridad)
        estudiante_id = request.POST.get('id_estudiante')
        nombre_nuevo = request.POST.get('nombre_completo')
        correo_nuevo = request.POST.get('correo')
        pc_id = request.POST.get('pc')
        software_id = request.POST.get('software')

        estudiante, creado = Estudiante.objects.get_or_create(
            id=estudiante_id, 
            defaults={'nombre_completo': nombre_nuevo, 'correo': correo_nuevo}
        )

        pc_seleccionada = PC.objects.get(id=pc_id)
        software_seleccionado = Software.objects.get(id=software_id)

        Visita.objects.create(
            estudiante=estudiante,
            pc=pc_seleccionada,
            software_utilizado=software_seleccionado
        )

        pc_seleccionada.estado = 'En Uso'
        pc_seleccionada.save()

        todos_los_labs = Laboratorio.objects.all() # Aquí podrías aplicar el filtro también
        todo_el_software = Software.objects.all()
        contexto = {
            'laboratorios': todos_los_labs,
            'software': todo_el_software,
            'success_message': f"¡Visita registrada con éxito para {estudiante.nombre_completo} en la PC {pc_seleccionada}!"
        }
        return render(request, 'gestion/registro.html', contexto)

    # --- INICIO DEL CAMBIO ---
    # El bloque GET (cuando se carga la página) ahora es más inteligente
    else:
        # Obtenemos la fecha y hora actual
        ahora = timezone.now()

        # Buscamos los IDs de los laboratorios que tienen una reserva ACTIVA
        labs_ocupados = ReservaClase.objects.filter(
            fecha_hora_inicio__lte=ahora, 
            fecha_hora_fin__gte=ahora
        ).values_list('laboratorio__id', flat=True)

        # Pedimos a la base de datos todos los laboratorios, EXCEPTO los que están en la lista de ocupados
        labs_disponibles = Laboratorio.objects.exclude(id__in=list(labs_ocupados))

        todo_el_software = Software.objects.all()
        contexto = {
            'laboratorios': labs_disponibles,
            'software': todo_el_software,
        }
        return render(request, 'gestion/registro.html', contexto)


# gestion/views.py

def opciones_dinamicas(request):
    software_id = request.GET.get('software_id')
    laboratorio_id = request.GET.get('laboratorio_id')

    labs_disponibles = []
    software_disponible = []
    pcs_disponibles = []

    # Usamos la hora local para la comparación
    ahora = timezone.localtime(timezone.now())

    # Buscamos los IDs de los laboratorios que tienen una reserva ACTIVA en nuestro modelo simple
    labs_ocupados_ids = ReservaClase.objects.filter(
        fecha_hora_inicio__lte=ahora,
        fecha_hora_fin__gte=ahora
    ).values_list('laboratorio_id', flat=True)

    ids_labs_ocupados = list(set(labs_ocupados_ids))

    if software_id:
        try:
            software = Software.objects.get(id=software_id)
            labs_con_software = software.laboratorios.all()
            labs_disponibles = list(
                labs_con_software.exclude(id__in=ids_labs_ocupados)
                                 .order_by('nombre')
                                 .values('id', 'nombre')
            )
        except Software.DoesNotExist:
            pass 
    elif laboratorio_id:
        try:
            laboratorio = Laboratorio.objects.get(id=laboratorio_id)
            software_disponible = list(laboratorio.software_instalado.all().order_by('nombre').values('id', 'nombre'))
            pcs_disponibles = list(PC.objects.filter(laboratorio=laboratorio, estado='Disponible').order_by('numero_pc').values('id', 'numero_pc'))
        except Laboratorio.DoesNotExist:
            pass
    else: # Carga inicial de la página
        labs_disponibles = list(
            Laboratorio.objects.exclude(id__in=ids_labs_ocupados)
                             .order_by('nombre')
                             .values('id', 'nombre')
        )
        software_disponible = list(Software.objects.all().order_by('nombre').values('id', 'nombre'))

    return JsonResponse({
        'laboratorios': labs_disponibles,
        'software': software_disponible,
        'pcs': pcs_disponibles,
    })

def finalizar_visita(request):
    contexto = {}
    if request.method == 'POST':
        estudiante_id = request.POST.get('id_estudiante')

        # --- INICIO DE LA CORRECCIÓN ---
        # En lugar de .get(), usamos .filter() para obtener todas las sesiones activas,
        # las ordenamos por la más nueva primero (-fecha_hora_inicio), y tomamos la primera (.first()).
        visita_activa = Visita.objects.filter(
            estudiante__id=estudiante_id, 
            fecha_hora_fin__isnull=True
        ).order_by('-fecha_hora_inicio').first()
        # --- FIN DE LA CORRECCIÓN ---

        # Ahora, en lugar de un try/except, simplemente comprobamos si se encontró algo
        if visita_activa:
            # Si encontramos la visita, la finalizamos
            visita_activa.fecha_hora_fin = timezone.now()
            visita_activa.save()

            # Y liberamos la PC
            pc = visita_activa.pc
            pc.estado = 'Disponible'
            pc.save()

            contexto['success_message'] = f"¡Sesión finalizada con éxito! La PC {pc} ha sido liberada."
        else:
            # Si .first() no devuelve nada, significa que no hay sesión activa
            contexto['error_message'] = "No se encontró una sesión activa para este ID. Verifica que sea correcto."

    return render(request, 'gestion/finalizar.html', contexto)

def buscar_estudiante(request):
    # Obtenemos el ID que nos manda el JavaScript
    estudiante_id = request.GET.get('id_estudiante', None)
    datos = {'encontrado': False} # Preparamos una respuesta por defecto

    if estudiante_id:
        try:
            estudiante = Estudiante.objects.get(id=estudiante_id)
            # Si lo encontramos, preparamos los datos para devolverlos
            datos = {
                'encontrado': True,
                'nombre': estudiante.nombre_completo,
                'correo': estudiante.correo,
                'celular': estudiante.celular,
            }
        except Estudiante.DoesNotExist:
            # Si no lo encontramos, la respuesta por defecto ('encontrado': False) es suficiente
            pass

    return JsonResponse(datos)

def dashboard(request):
    # 1. Cálculos de estadísticas simples
    total_visitas = Visita.objects.count()
    pcs_en_uso = PC.objects.filter(estado='En Uso').count()
    total_estudiantes = Estudiante.objects.count()

    # 2. Cálculos con agregación (más complejos)
    #    .annotate() crea una nueva "columna" temporal con el cálculo
    #    .order_by() ordena los resultados
    lab_mas_usado = Laboratorio.objects.annotate(num_visitas=Count('pc__visita')).order_by('-num_visitas').first()
    software_mas_usado = Software.objects.annotate(num_usos=Count('visita')).order_by('-num_usos').first()

    # 3. Datos para el gráfico de barras (Uso por Laboratorio)
    uso_por_lab = Laboratorio.objects.annotate(
        visitas=Count('pc__visita')
    ).order_by('-visitas')

    # Preparamos las etiquetas y los datos para el gráfico
    labels_lab = [lab.nombre for lab in uso_por_lab]
    data_lab = [lab.visitas for lab in uso_por_lab]

    contexto = {
        'total_visitas': total_visitas,
        'pcs_en_uso': pcs_en_uso,
        'total_estudiantes': total_estudiantes,
        'lab_mas_usado': lab_mas_usado,
        'software_mas_usado': software_mas_usado,
        'labels_lab': labels_lab, # Datos para el gráfico
        'data_lab': data_lab,       # Datos para el gráfico
    }
    return render(request, 'gestion/dashboard.html', contexto)

@csrf_exempt # Desactiva la protección CSRF para esta API (para simplificar)
def registrar_visita_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Obtenemos los datos del JSON
            estudiante_id = data.get('id_estudiante')
            nombre = data.get('nombre_completo')
            correo = data.get('correo')
            celular = data.get('celular')
            pc_id = data.get('pc')
            software_id = data.get('software')

            # Buscamos o creamos al estudiante
            estudiante, creado = Estudiante.objects.get_or_create(
                id=estudiante_id,
                defaults={'nombre_completo': nombre, 'correo': correo, 'celular': celular}
            )

            # Buscamos los objetos
            pc_seleccionada = PC.objects.get(id=pc_id)
            software_seleccionado = Software.objects.get(id=software_id)

            # Creamos la visita
            Visita.objects.create(
                estudiante=estudiante,
                pc=pc_seleccionada,
                software_utilizado=software_seleccionado
            )

            # Actualizamos el estado de la PC
            pc_seleccionada.estado = 'En Uso'
            pc_seleccionada.save()

            return JsonResponse({'message': f'Visita registrada para {estudiante.nombre_completo}.'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def finalizar_visita_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            estudiante_id = data.get('id_estudiante')

            if not estudiante_id:
                return JsonResponse({'error': 'El ID del estudiante es requerido.'}, status=400)

            visita_activa = Visita.objects.filter(
                estudiante__id=estudiante_id, 
                fecha_hora_fin__isnull=True
            ).order_by('-fecha_hora_inicio').first()

            if visita_activa:
                visita_activa.fecha_hora_fin = timezone.now()
                visita_activa.save()

                pc = visita_activa.pc
                pc.estado = 'Disponible'
                pc.save()

                return JsonResponse({'message': f'Sesión finalizada. La PC {pc} ha sido liberada.'}, status=200)
            else:
                return JsonResponse({'error': 'No se encontró una sesión activa para este ID.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# APIs para dashboard React
@csrf_exempt
def api_dashboard_stats(request):
    """API para obtener estadísticas generales del dashboard"""
    
    try:
        # Estadísticas generales
        total_visitas = Visita.objects.count()
        total_estudiantes = Estudiante.objects.count()
        total_laboratorios = Laboratorio.objects.count()
        total_pcs = PC.objects.count()
        pcs_en_uso = PC.objects.filter(estado='En Uso').count()
        
        # Visitas del último mes
        hace_un_mes = timezone.now() - timedelta(days=30)
        visitas_ultimo_mes = Visita.objects.filter(fecha_hora_inicio__gte=hace_un_mes).count()
        
        # Tiempo promedio de uso (solo visitas completadas)
        visitas_completadas = Visita.objects.filter(fecha_hora_fin__isnull=False)
        tiempo_promedio_str = "0h 0m"
        
        if visitas_completadas.exists():
            # Calcular tiempo promedio manualmente
            total_seconds = 0
            count = 0
            for visita in visitas_completadas:
                if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                    diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                    total_seconds += diff.total_seconds()
                    count += 1
            
            if count > 0:
                avg_seconds = total_seconds / count
                horas = int(avg_seconds // 3600)
                minutos = int((avg_seconds % 3600) // 60)
                tiempo_promedio_str = f"{horas}h {minutos}m"
        
        # Porcentaje de ocupación
        porcentaje_ocupacion = (pcs_en_uso / total_pcs * 100) if total_pcs > 0 else 0
        
        return JsonResponse({
            'total_visitas': total_visitas,
            'total_estudiantes': total_estudiantes,
            'total_laboratorios': total_laboratorios,
            'total_pcs': total_pcs,
            'pcs_en_uso': pcs_en_uso,
            'visitas_ultimo_mes': visitas_ultimo_mes,
            'tiempo_promedio': tiempo_promedio_str,
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 1)
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'total_visitas': 0,
            'total_estudiantes': 0,
            'total_laboratorios': 0,
            'total_pcs': 0,
            'pcs_en_uso': 0,
            'visitas_ultimo_mes': 0,
            'tiempo_promedio': "0h 0m",
            'porcentaje_ocupacion': 0
        })


@csrf_exempt
def api_lab_usage(request):
    """API para obtener datos de uso por laboratorio"""
    
    try:
        # Uso por laboratorio (últimos 30 días)
        hace_30_dias = timezone.now() - timedelta(days=30)
        
        lab_usage = Laboratorio.objects.annotate(
            visitas=Count('pc__visita', filter=Q(pc__visita__fecha_hora_inicio__gte=hace_30_dias))
        ).order_by('-visitas')
        
        data = []
        for lab in lab_usage:
            data.append({
                'laboratorio': lab.nombre,
                'visitas': lab.visitas,
                'capacidad': lab.pc_set.count()
            })
        
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_software_usage(request):
    """API para obtener datos de uso de software"""
    
    try:
        # Software más usado (últimos 30 días)
        hace_30_dias = timezone.now() - timedelta(days=30)
        
        software_usage = Software.objects.annotate(
            usos=Count('visita', filter=Q(visita__fecha_hora_inicio__gte=hace_30_dias))
        ).filter(usos__gt=0).order_by('-usos')[:10]
        
        data = []
        for software in software_usage:
            data.append({
                'software': software.nombre,
                'usos': software.usos,
                'categoria': getattr(software, 'categoria', 'Sin categoría')
            })
        
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_visits_timeline(request):
    """API para obtener datos de visitas por día (últimos 30 días)"""
    
    try:
        # Visitas por día (últimos 30 días)
        hace_30_dias = timezone.now() - timedelta(days=30)
        
        visits_by_day = Visita.objects.filter(
            fecha_hora_inicio__gte=hace_30_dias
        ).extra(
            select={'day': 'date(fecha_hora_inicio)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        data = []
        for item in visits_by_day:
            # Convertir la fecha a zona horaria local
            fecha_local = timezone.localtime(item['day'])
            data.append({
                'fecha': fecha_local.strftime('%Y-%m-%d'),
                'visitas': item['count']
            })
        
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_recent_visits(request):
    """API para obtener visitas recientes"""
    
    try:
        # Visitas recientes (últimas 10)
        recent_visits = Visita.objects.select_related(
            'estudiante', 'pc__laboratorio', 'software_utilizado'
        ).order_by('-fecha_hora_inicio')[:10]
        
        data = []
        for visita in recent_visits:
            # Convertir a zona horaria local de México
            fecha_inicio_local = timezone.localtime(visita.fecha_hora_inicio)
            fecha_fin_local = timezone.localtime(visita.fecha_hora_fin) if visita.fecha_hora_fin else None
            
            data.append({
                'id': visita.id,
                'estudiante': visita.estudiante.nombre_completo,
                'laboratorio': visita.pc.laboratorio.nombre,
                'pc': str(visita.pc),
                'software': visita.software_utilizado.nombre if visita.software_utilizado else 'N/A',
                'fecha_inicio': fecha_inicio_local.strftime('%Y-%m-%d %H:%M'),
                'fecha_fin': fecha_fin_local.strftime('%Y-%m-%d %H:%M') if fecha_fin_local else 'En curso',
                'estado': 'En uso' if visita.fecha_hora_fin is None else 'Terminado'
            })
        
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


# APIs para reportes filtrados
@csrf_exempt
def api_reports_filtered_stats(request):
    """API para obtener estadísticas filtradas para reportes"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        laboratory = request.GET.get('laboratory', 'all')
        software = request.GET.get('software', 'all')
        user_type = request.GET.get('user_type', 'all')
        
        # Construir filtros base
        filters = Q()
        
        # Filtro por fechas
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        
        # Filtro por laboratorio
        if laboratory != 'all':
            filters &= Q(pc__laboratorio__id=laboratory)
        
        # Filtro por software
        if software != 'all':
            filters &= Q(software_utilizado__id=software)
        
        # Aplicar filtros a las consultas
        visitas_filtradas = Visita.objects.filter(filters)
        
        # Calcular estadísticas
        total_visitas = visitas_filtradas.count()
        
        # Promedio diario
        if date_from and date_to:
            from datetime import datetime
            fecha_inicio = datetime.strptime(date_from, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(date_to, '%Y-%m-%d').date()
            dias = (fecha_fin - fecha_inicio).days + 1
            promedio_diario = round(total_visitas / dias, 1) if dias > 0 else 0
        else:
            promedio_diario = 0
        
        # Tiempo total (solo visitas completadas)
        visitas_completadas = visitas_filtradas.filter(fecha_hora_fin__isnull=False)
        tiempo_total_horas = 0
        
        for visita in visitas_completadas:
            if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                tiempo_total_horas += diff.total_seconds() / 3600
        
        # Sesiones únicas (usuarios distintos)
        sesiones_unicas = visitas_filtradas.values('estudiante').distinct().count()
        
        return JsonResponse({
            'total_visitas': total_visitas,
            'promedio_diario': promedio_diario,
            'tiempo_total_horas': round(tiempo_total_horas, 1),
            'sesiones_unicas': sesiones_unicas
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
def api_reports_lab_usage(request):
    """API para obtener uso por laboratorio filtrado"""
    
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
        
        # Obtener laboratorios con sus estadísticas
        if laboratory != 'all':
            labs = Laboratorio.objects.filter(id=laboratory)
        else:
            labs = Laboratorio.objects.all()
        
        data = []
        for lab in labs:
            # Contar visitas para este laboratorio
            visitas = Visita.objects.filter(filters, pc__laboratorio=lab)
            total_visitas = visitas.count()
            
            # Calcular horas totales
            horas_totales = 0
            for visita in visitas.filter(fecha_hora_fin__isnull=False):
                if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                    diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                    horas_totales += diff.total_seconds() / 3600
            
            data.append({
                'name': lab.nombre,
                'visitas': total_visitas,
                'horas': round(horas_totales, 1)
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_reports_software_usage(request):
    """API para obtener uso de software filtrado"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        software = request.GET.get('software', 'all')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        
        # Obtener software con sus estadísticas
        if software != 'all':
            software_list = Software.objects.filter(id=software)
        else:
            software_list = Software.objects.all()
        
        data = []
        for soft in software_list:
            # Contar usos para este software
            usos = Visita.objects.filter(filters, software_utilizado=soft).count()
            
            if usos > 0:  # Solo incluir software que se haya usado
                data.append({
                    'name': soft.nombre,
                    'value': usos
                })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_reports_daily_trend(request):
    """API para obtener tendencia diaria filtrada"""
    
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
            filters &= Q(pc__laboratorio__id=laboratory)
        
        # Obtener visitas por día de la semana
        visitas_por_dia = Visita.objects.filter(filters).extra(
            select={'day_of_week': 'extract(dow from fecha_hora_inicio)'}
        ).values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')
        
        # Mapear días de la semana
        dias_semana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
        
        data = []
        for item in visitas_por_dia:
            dia_num = int(item['day_of_week'])
            data.append({
                'dia': dias_semana[dia_num],
                'visitas': item['count']
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_reports_top_users(request):
    """API para obtener usuarios más activos filtrados"""
    
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        laboratory = request.GET.get('laboratory', 'all')
        software = request.GET.get('software', 'all')
        
        # Construir filtros base
        filters = Q()
        
        if date_from:
            filters &= Q(fecha_hora_inicio__date__gte=date_from)
        if date_to:
            filters &= Q(fecha_hora_inicio__date__lte=date_to)
        if laboratory != 'all':
            filters &= Q(pc__laboratorio__id=laboratory)
        if software != 'all':
            filters &= Q(software_utilizado__id=software)
        
        # Obtener usuarios con sus estadísticas
        usuarios_stats = Visita.objects.filter(filters).values(
            'estudiante__nombre_completo'
        ).annotate(
            total_visitas=Count('id')
        ).order_by('-total_visitas')[:5]
        
        data = []
        for usuario in usuarios_stats:
            # Calcular horas totales para este usuario
            visitas_usuario = Visita.objects.filter(
                filters, 
                estudiante__nombre_completo=usuario['estudiante__nombre_completo']
            ).filter(fecha_hora_fin__isnull=False)
            
            horas_totales = 0
            for visita in visitas_usuario:
                if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                    diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                    horas_totales += diff.total_seconds() / 3600
            
            data.append({
                'nombre': usuario['estudiante__nombre_completo'],
                'visitas': usuario['total_visitas'],
                'horas': round(horas_totales, 1)
            })
        
        return JsonResponse({'data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_reports_laboratories_list(request):
    """API para obtener lista de laboratorios para filtros"""
    
    try:
        labs = Laboratorio.objects.all().order_by('nombre')
        data = [{'id': lab.id, 'name': lab.nombre} for lab in labs]
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


@csrf_exempt
def api_reports_software_list(request):
    """API para obtener lista de software para filtros"""
    
    try:
        software = Software.objects.all().order_by('nombre')
        data = [{'id': soft.id, 'name': soft.nombre} for soft in software]
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'data': []})


# APIs para exportación de reportes
@csrf_exempt
def api_export_pdf(request):
    """API para exportar reporte a PDF"""
    
    try:
        from .report_generator import ReportGenerator
        from django.http import HttpResponse
        import json
        
        # Obtener filtros del request
        filters = {}
        if request.method == 'GET':
            filters = dict(request.GET)
        elif request.method == 'POST':
            data = json.loads(request.body)
            filters = data.get('filters', {})
        
        # Generar PDF
        generator = ReportGenerator()
        pdf_content = generator.generate_pdf_report(filters)
        
        # Crear respuesta HTTP
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_laboratorios_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_export_excel(request):
    """API para exportar reporte a Excel"""
    
    try:
        from .report_generator import ReportGenerator
        from django.http import HttpResponse
        import json
        
        # Obtener filtros del request
        filters = {}
        if request.method == 'GET':
            filters = dict(request.GET)
        elif request.method == 'POST':
            data = json.loads(request.body)
            filters = data.get('filters', {})
        
        # Generar Excel
        generator = ReportGenerator()
        excel_content = generator.generate_excel_report(filters)
        
        # Crear respuesta HTTP
        response = HttpResponse(
            excel_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_laboratorios_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)