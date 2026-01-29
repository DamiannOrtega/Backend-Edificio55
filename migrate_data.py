#!/usr/bin/env python
"""
Script para migrar datos desde base de datos local a Supabase
"""
import os
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_labs.settings')
django.setup()

from gestion.models import (
    Laboratorio, PC, Estudiante, Software, ReservaClase, 
    SerieReserva, Visita, Mantenimiento, DiaSemana
)

def export_data():
    """Exporta todos los datos a un archivo JSON"""
    print("📦 Exportando datos...")
    
    data = {
        'laboratorios': [],
        'pcs': [],
        'estudiantes': [],
        'software': [],
        'reservas': [],
        'series_reservas': [],
        'visitas': [],
        'mantenimientos': [],
    }
    
    # Exportar Laboratorios
    for lab in Laboratorio.objects.all():
        data['laboratorios'].append({
            'nombre': lab.nombre,
            'capacidad': lab.capacidad,
            'descripcion': lab.descripcion,
        })
    
    # Exportar Software
    for soft in Software.objects.all():
        data['software'].append({
            'nombre': soft.nombre,
            'version': soft.version,
            'descripcion': soft.descripcion,
        })
    
    # Exportar Estudiantes
    for est in Estudiante.objects.all():
        data['estudiantes'].append({
            'matricula': est.matricula,
            'nombre': est.nombre,
            'apellido': est.apellido,
            'email': est.email,
        })
    
    # Exportar PCs (necesitamos el ID del laboratorio)
    for pc in PC.objects.all():
        data['pcs'].append({
            'numero': pc.numero,
            'laboratorio_nombre': pc.laboratorio.nombre if pc.laboratorio else None,
            'estado': pc.estado,
            'software_ids': [s.nombre for s in pc.software.all()],
        })
    
    # Exportar Series de Reservas
    for serie in SerieReserva.objects.all():
        data['series_reservas'].append({
            'nombre': serie.nombre,
            'laboratorio_nombre': serie.laboratorio.nombre if serie.laboratorio else None,
            'hora_inicio': serie.hora_inicio.strftime('%H:%M:%S') if serie.hora_inicio else None,
            'hora_fin': serie.hora_fin.strftime('%H:%M:%S') if serie.hora_fin else None,
            'activa': serie.activa,
            'dias_semana': [dia.nombre for dia in serie.dias_semana.all()],
        })
    
    # Exportar Reservas
    for res in ReservaClase.objects.all():
        data['reservas'].append({
            'fecha': res.fecha.isoformat() if res.fecha else None,
            'laboratorio_nombre': res.laboratorio.nombre if res.laboratorio else None,
            'hora_inicio': res.hora_inicio.strftime('%H:%M:%S') if res.hora_inicio else None,
            'hora_fin': res.hora_fin.strftime('%H:%M:%S') if res.hora_fin else None,
            'serie_nombre': res.serie.nombre if res.serie else None,
        })
    
    # Exportar Visitas
    for vis in Visita.objects.all():
        data['visitas'].append({
            'matricula_estudiante': vis.estudiante.matricula if vis.estudiante else None,
            'pc_numero': vis.pc.numero if vis.pc else None,
            'laboratorio_nombre': vis.pc.laboratorio.nombre if vis.pc and vis.pc.laboratorio else None,
            'fecha_entrada': vis.fecha_entrada.isoformat() if vis.fecha_entrada else None,
            'fecha_salida': vis.fecha_salida.isoformat() if vis.fecha_salida else None,
            'software_usado': [s.nombre for s in vis.software_usado.all()],
        })
    
    # Exportar Mantenimientos
    for mant in Mantenimiento.objects.all():
        data['mantenimientos'].append({
            'pc_numero': mant.pc.numero if mant.pc else None,
            'laboratorio_nombre': mant.pc.laboratorio.nombre if mant.pc and mant.pc.laboratorio else None,
            'fecha_inicio': mant.fecha_inicio.isoformat() if mant.fecha_inicio else None,
            'fecha_fin': mant.fecha_fin.isoformat() if mant.fecha_fin else None,
            'descripcion': mant.descripcion,
            'tipo': mant.tipo,
        })
    
    # Guardar en archivo
    filename = f'backup_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Datos exportados a: {filename}")
    print(f"  - Laboratorios: {len(data['laboratorios'])}")
    print(f"  - PCs: {len(data['pcs'])}")
    print(f"  - Estudiantes: {len(data['estudiantes'])}")
    print(f"  - Software: {len(data['software'])}")
    print(f"  - Reservas: {len(data['reservas'])}")
    print(f"  - Series: {len(data['series_reservas'])}")
    print(f"  - Visitas: {len(data['visitas'])}")
    print(f"  - Mantenimientos: {len(data['mantenimientos'])}")
    
    return filename, data

def import_data(filename=None, data=None):
    """Importa datos desde un archivo JSON"""
    if data is None:
        if filename is None:
            # Buscar el archivo más reciente
            import glob
            files = glob.glob('backup_data_*.json')
            if not files:
                print("✗ No se encontró archivo de backup")
                return
            filename = max(files, key=os.path.getctime)
        
        print(f"📥 Importando datos desde: {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("📥 Importando datos...")
    
    # Importar en orden correcto (respetando dependencias)
    
    # 1. Laboratorios
    lab_map = {}
    for lab_data in data['laboratorios']:
        lab, created = Laboratorio.objects.get_or_create(
            nombre=lab_data['nombre'],
            defaults={
                'capacidad': lab_data.get('capacidad', 0),
                'descripcion': lab_data.get('descripcion', ''),
            }
        )
        lab_map[lab_data['nombre']] = lab
        if created:
            print(f"  ✓ Laboratorio creado: {lab.nombre}")
    
    # 2. Software
    soft_map = {}
    for soft_data in data['software']:
        soft, created = Software.objects.get_or_create(
            nombre=soft_data['nombre'],
            defaults={
                'version': soft_data.get('version', ''),
                'descripcion': soft_data.get('descripcion', ''),
            }
        )
        soft_map[soft_data['nombre']] = soft
        if created:
            print(f"  ✓ Software creado: {soft.nombre}")
    
    # 3. Estudiantes
    est_map = {}
    for est_data in data['estudiantes']:
        est, created = Estudiante.objects.get_or_create(
            matricula=est_data['matricula'],
            defaults={
                'nombre': est_data.get('nombre', ''),
                'apellido': est_data.get('apellido', ''),
                'email': est_data.get('email', ''),
            }
        )
        est_map[est_data['matricula']] = est
        if created:
            print(f"  ✓ Estudiante creado: {est.matricula}")
    
    # 4. PCs
    pc_map = {}
    for pc_data in data['pcs']:
        lab = lab_map.get(pc_data['laboratorio_nombre'])
        if not lab:
            print(f"  ⚠ PC {pc_data['numero']} omitida: laboratorio no encontrado")
            continue
        
        pc, created = PC.objects.get_or_create(
            numero=pc_data['numero'],
            laboratorio=lab,
            defaults={
                'estado': pc_data.get('estado', 'disponible'),
            }
        )
        
        # Asignar software
        for soft_name in pc_data.get('software_ids', []):
            if soft_name in soft_map:
                pc.software.add(soft_map[soft_name])
        
        pc_map[f"{pc_data['laboratorio_nombre']}_{pc_data['numero']}"] = pc
        if created:
            print(f"  ✓ PC creada: {pc.numero} en {lab.nombre}")
    
    # 5. Días de semana (crear si no existen)
    dia_map = {}
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for dia_nombre in dias_nombres:
        dia, created = DiaSemana.objects.get_or_create(nombre=dia_nombre)
        dia_map[dia_nombre] = dia
    
    # 6. Series de Reservas
    serie_map = {}
    for serie_data in data['series_reservas']:
        lab = lab_map.get(serie_data['laboratorio_nombre'])
        if not lab:
            continue
        
        from datetime import time as dt_time
        hora_inicio = None
        hora_fin = None
        if serie_data.get('hora_inicio'):
            h, m, s = map(int, serie_data['hora_inicio'].split(':'))
            hora_inicio = dt_time(h, m, s)
        if serie_data.get('hora_fin'):
            h, m, s = map(int, serie_data['hora_fin'].split(':'))
            hora_fin = dt_time(h, m, s)
        
        serie, created = SerieReserva.objects.get_or_create(
            nombre=serie_data['nombre'],
            laboratorio=lab,
            defaults={
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'activa': serie_data.get('activa', True),
            }
        )
        
        # Asignar días
        for dia_nombre in serie_data.get('dias_semana', []):
            if dia_nombre in dia_map:
                serie.dias_semana.add(dia_map[dia_nombre])
        
        serie_map[serie_data['nombre']] = serie
        if created:
            print(f"  ✓ Serie creada: {serie.nombre}")
    
    # 7. Reservas
    from datetime import datetime as dt
    for res_data in data['reservas']:
        lab = lab_map.get(res_data['laboratorio_nombre'])
        if not lab:
            continue
        
        fecha = dt.fromisoformat(res_data['fecha']).date() if res_data.get('fecha') else None
        hora_inicio = None
        hora_fin = None
        if res_data.get('hora_inicio'):
            h, m, s = map(int, res_data['hora_inicio'].split(':'))
            hora_inicio = dt_time(h, m, s)
        if res_data.get('hora_fin'):
            h, m, s = map(int, res_data['hora_fin'].split(':'))
            hora_fin = dt_time(h, m, s)
        
        serie = serie_map.get(res_data['serie_nombre']) if res_data.get('serie_nombre') else None
        
        ReservaClase.objects.get_or_create(
            fecha=fecha,
            laboratorio=lab,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            defaults={'serie': serie}
        )
    
    # 8. Visitas
    for vis_data in data['visitas']:
        est = est_map.get(vis_data['matricula_estudiante'])
        if not est:
            continue
        
        pc_key = f"{vis_data['laboratorio_nombre']}_{vis_data['pc_numero']}"
        pc = pc_map.get(pc_key)
        if not pc:
            continue
        
        fecha_entrada = dt.fromisoformat(vis_data['fecha_entrada']) if vis_data.get('fecha_entrada') else None
        fecha_salida = dt.fromisoformat(vis_data['fecha_salida']) if vis_data.get('fecha_salida') else None
        
        visita = Visita.objects.create(
            estudiante=est,
            pc=pc,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
        )
        
        # Asignar software usado
        for soft_name in vis_data.get('software_usado', []):
            if soft_name in soft_map:
                visita.software_usado.add(soft_map[soft_name])
    
    # 9. Mantenimientos
    for mant_data in data['mantenimientos']:
        pc_key = f"{mant_data['laboratorio_nombre']}_{mant_data['pc_numero']}"
        pc = pc_map.get(pc_key)
        if not pc:
            continue
        
        fecha_inicio = dt.fromisoformat(mant_data['fecha_inicio']) if mant_data.get('fecha_inicio') else None
        fecha_fin = dt.fromisoformat(mant_data['fecha_fin']) if mant_data.get('fecha_fin') else None
        
        Mantenimiento.objects.create(
            pc=pc,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            descripcion=mant_data.get('descripcion', ''),
            tipo=mant_data.get('tipo', 'preventivo'),
        )
    
    print("\n✓ Importación completada!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_data()
    elif len(sys.argv) > 1 and sys.argv[1] == 'import':
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        import_data(filename)
    else:
        print("Uso:")
        print("  python migrate_data.py export  - Exportar datos a JSON")
        print("  python migrate_data.py import [archivo.json]  - Importar datos desde JSON")





