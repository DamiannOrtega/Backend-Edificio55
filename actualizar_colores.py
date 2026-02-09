"""
Script para actualizar los colores de las reservas existentes
Copia el color de la serie a todas las reservas que pertenecen a esa serie
"""

from gestion.models import ReservaClase, SerieReserva

def actualizar_colores_reservas():
    """Actualiza el color de todas las reservas basándose en su serie"""
    
    # Obtener todas las reservas que tienen una serie asociada
    reservas_con_serie = ReservaClase.objects.filter(serie__isnull=False)
    
    actualizadas = 0
    
    for reserva in reservas_con_serie:
        if reserva.serie and reserva.serie.color:
            # Actualizar el color de la reserva con el color de la serie
            reserva.color = reserva.serie.color
            reserva.save()
            actualizadas += 1
    
    print(f"✅ Se actualizaron {actualizadas} reservas con los colores de sus series")
    
    # También actualizar reservas sin serie que no tienen color
    reservas_sin_color = ReservaClase.objects.filter(color__isnull=True)
    sin_serie_actualizadas = 0
    
    for reserva in reservas_sin_color:
        reserva.color = '#667eea'  # Color por defecto
        reserva.save()
        sin_serie_actualizadas += 1
    
    print(f"✅ Se asignó color por defecto a {sin_serie_actualizadas} reservas sin color")
    
    return actualizadas + sin_serie_actualizadas

if __name__ == '__main__':
    total = actualizar_colores_reservas()
    print(f"\n🎉 Total de reservas actualizadas: {total}")
