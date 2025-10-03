from django.shortcuts import render
from django.http import JsonResponse
# ASÍ DEBE QUEDAR
from .models import Laboratorio, Software, PC, Estudiante, Visita, ReservaClase
from django.utils import timezone
from django.db.models import Count
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


def opciones_dinamicas(request):
    software_id = request.GET.get('software_id')
    laboratorio_id = request.GET.get('laboratorio_id')

    labs_disponibles = []
    software_disponible = []
    pcs_disponibles = []

    if software_id:
        try:
            software = Software.objects.get(id=software_id)
            # Ordenamos los laboratorios alfabéticamente también
            labs_disponibles = list(software.laboratorios.all().order_by('nombre').values('id', 'nombre'))
        except Software.DoesNotExist:
            pass 

    elif laboratorio_id:
        try:
            laboratorio = Laboratorio.objects.get(id=laboratorio_id)

            # --- CAMBIO AQUÍ ---
            # Ordenamos el software de este laboratorio por nombre
            software_disponible = list(laboratorio.software_instalado.all().order_by('nombre').values('id', 'nombre'))

            pcs_disponibles = list(PC.objects.filter(
                laboratorio=laboratorio, 
                estado='Disponible'
            ).order_by('numero_pc').values('id', 'numero_pc'))

        except Laboratorio.DoesNotExist:
            pass

    else:
        ahora = timezone.now()
        labs_ocupados = ReservaClase.objects.filter(
            fecha_hora_inicio__lte=ahora, 
            fecha_hora_fin__gte=ahora
        ).values_list('laboratorio__id', flat=True)

        labs_disponibles = list(Laboratorio.objects.exclude(id__in=list(labs_ocupados)).order_by('nombre').values('id', 'nombre'))

        # Ordenamos la lista completa de software por nombre
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