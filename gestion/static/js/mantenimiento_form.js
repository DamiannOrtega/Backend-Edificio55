// Esperar a que jQuery esté disponible
(function() {
    'use strict';
    
    // Función para inicializar cuando jQuery esté disponible
    function initMantenimientoForm() {
        // Intentar obtener jQuery de diferentes fuentes
        var $ = window.jQuery || window.django && window.django.jQuery || null;
        
        if (!$) {
            // Si jQuery no está disponible, intentar de nuevo después de un breve delay
            setTimeout(initMantenimientoForm, 100);
            return;
        }
        
        // Usar jQuery cuando esté disponible
        $(document).ready(function() {
            // Obtener los campos
            var $laboratorioField = $('#id_laboratorio');
            var $pcField = $('#id_pc');
            
            // Verificar que los campos existan
            if (!$laboratorioField.length || !$pcField.length) {
                console.log('Campos no encontrados, reintentando...');
                setTimeout(arguments.callee, 200);
                return;
            }
            
            // Construir la URL base del admin de mantenimientos
            var urlBase = '/admin/gestion/mantenimiento';
            
            console.log('Mantenimiento form JS cargado');
            console.log('Laboratorio field:', $laboratorioField.length);
            console.log('PC field:', $pcField.length);
            
            // Función para obtener el token CSRF
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            
            // Función para cargar las PCs según el laboratorio seleccionado
            function loadPCs() {
                var laboratorioId = $laboratorioField.val();
                
                console.log('loadPCs llamado con laboratorio_id:', laboratorioId);
                
                if (!laboratorioId) {
                    $pcField.empty();
                    $pcField.append($('<option></option>').attr('value', '').text('---------'));
                    return;
                }
                
                // Deshabilitar el campo PC mientras se carga
                $pcField.prop('disabled', true);
                $pcField.html('<option>Cargando...</option>');
                
                var ajaxUrl = urlBase + '/get-pcs/';
                console.log('Haciendo petición AJAX a:', ajaxUrl);
                console.log('Con datos:', {laboratorio_id: laboratorioId});
                
                var csrftoken = getCookie('csrftoken');
                
                // Hacer una petición AJAX para obtener las PCs del laboratorio
                $.ajax({
                    url: ajaxUrl,
                    type: 'GET',
                    data: {
                        'laboratorio_id': laboratorioId
                    },
                    dataType: 'json',
                    beforeSend: function(xhr) {
                        if (csrftoken) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    },
                    success: function(data) {
                        console.log('Respuesta recibida:', data);
                        var currentPcValue = $pcField.data('current-value') || $pcField.val();
                        $pcField.empty();
                        $pcField.append($('<option></option>').attr('value', '').text('---------'));
                        
                        if (data.pcs && data.pcs.length > 0) {
                            console.log('Agregando', data.pcs.length, 'PCs');
                            $.each(data.pcs, function(index, pc) {
                                var $option = $('<option></option>').attr('value', pc.id).text(pc.nombre);
                                if (pc.id == currentPcValue) {
                                    $option.attr('selected', 'selected');
                                }
                                $pcField.append($option);
                            });
                        } else {
                            console.log('No hay PCs disponibles');
                            $pcField.append($('<option></option>').attr('value', '').text('No hay PCs disponibles'));
                        }
                        
                        $pcField.prop('disabled', false);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error al cargar las PCs:', error);
                        console.error('URL intentada:', ajaxUrl);
                        console.error('Response:', xhr.responseText);
                        console.error('Status:', xhr.status);
                        console.error('Status Text:', xhr.statusText);
                        $pcField.empty();
                        $pcField.append($('<option></option>').attr('value', '').text('Error al cargar PCs (ver consola)'));
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
                console.log('Cambio detectado en laboratorio');
                loadPCs();
            });
            
            // También usar el evento input por si acaso
            $laboratorioField.on('input', function() {
                console.log('Input detectado en laboratorio');
                loadPCs();
            });
            
            // Cargar PCs al cargar la página si ya hay un laboratorio seleccionado
            if ($laboratorioField.val()) {
                console.log('Laboratorio ya seleccionado al cargar:', $laboratorioField.val());
                loadPCs();
            }
            
            // Forzar el evento change si el campo tiene valor
            setTimeout(function() {
                if ($laboratorioField.val() && $pcField.find('option').length <= 1) {
                    console.log('Forzando carga de PCs después de timeout');
                    loadPCs();
                }
            }, 500);
        });
    }
    
    // Iniciar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMantenimientoForm);
    } else {
        initMantenimientoForm();
    }
})();
