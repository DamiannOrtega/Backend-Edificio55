(function($) {
    $(document).ready(function() {
        // Obtener los campos
        var $laboratorioField = $('#id_laboratorio');
        var $pcField = $('#id_pc');
        
        // Verificar que los campos existan
        if (!$laboratorioField.length || !$pcField.length) {
            return;
        }
        
        // Construir la URL base del admin de mantenimientos
        // La URL será algo como: /admin/gestion/mantenimiento/get-pcs/
        var pathParts = window.location.pathname.split('/').filter(function(part) {
            return part !== '';
        });
        
        // Buscar el índice de 'mantenimiento' o construir la URL base
        var urlBase = '/admin/gestion/mantenimiento';
        
        // Función para cargar las PCs según el laboratorio seleccionado
        function loadPCs() {
            var laboratorioId = $laboratorioField.val();
            
            if (!laboratorioId) {
                $pcField.empty();
                $pcField.append($('<option></option>').attr('value', '').text('---------'));
                return;
            }
            
            // Deshabilitar el campo PC mientras se carga
            $pcField.prop('disabled', true);
            $pcField.html('<option>Cargando...</option>');
            
            // Hacer una petición AJAX para obtener las PCs del laboratorio
            $.ajax({
                url: urlBase + '/get-pcs/',
                data: {
                    'laboratorio_id': laboratorioId
                },
                dataType: 'json',
                success: function(data) {
                    var currentPcValue = $pcField.data('current-value') || $pcField.val();
                    $pcField.empty();
                    $pcField.append($('<option></option>').attr('value', '').text('---------'));
                    
                    if (data.pcs && data.pcs.length > 0) {
                        $.each(data.pcs, function(index, pc) {
                            var $option = $('<option></option>').attr('value', pc.id).text(pc.nombre);
                            if (pc.id == currentPcValue) {
                                $option.attr('selected', 'selected');
                            }
                            $pcField.append($option);
                        });
                    } else {
                        $pcField.append($('<option></option>').attr('value', '').text('No hay PCs disponibles'));
                    }
                    
                    $pcField.prop('disabled', false);
                },
                error: function(xhr, status, error) {
                    console.error('Error al cargar las PCs:', error);
                    console.error('URL intentada:', urlBase + '/get-pcs/');
                    console.error('Response:', xhr.responseText);
                    $pcField.empty();
                    $pcField.append($('<option></option>').attr('value', '').text('Error al cargar PCs'));
                    $pcField.prop('disabled', false);
                }
            });
        }
        
        // Guardar el valor actual de PC antes de limpiar
        if ($pcField.val()) {
            $pcField.data('current-value', $pcField.val());
        }
        
        // Cargar PCs cuando se cambie el laboratorio
        $laboratorioField.on('change', function() {
            loadPCs();
        });
        
        // Cargar PCs al cargar la página si ya hay un laboratorio seleccionado
        if ($laboratorioField.val()) {
            loadPCs();
        }
    });
})(django.jQuery);

