/**
 * fecha_filter.js
 * Inyecta un date-picker en el filtro "Por Fecha" del sidebar del admin
 * de ReservaClase, permitiendo filtrar por fecha exacta con un clic.
 */
(function () {
    'use strict';

    function injectDatePicker() {
        // Buscar el bloque del filtro "Fecha" en el sidebar
        var filterHeadings = document.querySelectorAll('#changelist-filter h3, #changelist-filter h2');
        var targetSection = null;

        for (var i = 0; i < filterHeadings.length; i++) {
            if (filterHeadings[i].textContent.trim() === 'Por fecha') {
                targetSection = filterHeadings[i].parentElement;
                break;
            }
        }

        if (!targetSection) return; // No estamos en la pagina de reservas

        // Leer el valor actual del filtro desde la URL
        var params = new URLSearchParams(window.location.search);
        var valorActual = params.get('fecha_exacta') || '';

        // Crear el date picker
        var wrapper = document.createElement('div');
        wrapper.style.cssText = 'padding: 8px 10px 12px;';

        var input = document.createElement('input');
        input.type = 'date';
        input.value = valorActual;
        input.style.cssText = (
            'width:100%;padding:6px 8px;border:1px solid #ccc;border-radius:4px;' +
            'font-size:13px;box-sizing:border-box;margin-bottom:6px;'
        );

        var btn = document.createElement('button');
        btn.textContent = 'Filtrar';
        btn.style.cssText = (
            'width:100%;padding:6px;background:#417690;color:#fff;border:none;' +
            'border-radius:4px;cursor:pointer;font-size:13px;'
        );
        btn.addEventListener('click', function () {
            var fecha = input.value;
            if (!fecha) {
                // Quitar el filtro
                params.delete('fecha_exacta');
            } else {
                params.set('fecha_exacta', fecha);
            }
            // Resetear paginacion al filtrar
            params.delete('p');
            window.location.search = params.toString();
        });

        // Boton para limpiar el filtro (solo si hay valor activo)
        if (valorActual) {
            var clearBtn = document.createElement('a');
            clearBtn.textContent = '✕ Quitar filtro de fecha';
            clearBtn.href = '#';
            clearBtn.style.cssText = (
                'display:block;margin-top:6px;font-size:12px;color:#666;text-align:center;'
            );
            clearBtn.addEventListener('click', function (e) {
                e.preventDefault();
                params.delete('fecha_exacta');
                params.delete('p');
                window.location.search = params.toString();
            });
            wrapper.appendChild(clearBtn);
        }

        wrapper.insertBefore(input, wrapper.firstChild);
        wrapper.insertBefore(btn, wrapper.children[1]);

        // Insertar el date-picker DESPUES de la lista de opciones "Todos"
        var ul = targetSection.querySelector('ul');
        if (ul) {
            ul.style.display = 'none'; // Ocultar el "Todos" del choices() si existe
        }
        targetSection.appendChild(wrapper);
    }

    // Ejecutar al cargar la pagina
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectDatePicker);
    } else {
        injectDatePicker();
    }
})();
