# 🚀 Guía de Inicio Automático del Sistema

## 📋 Introducción

Esta guía te explica cómo configurar el sistema para que se inicie automáticamente sin necesidad de ejecutar comandos manualmente cada día.

## 🎯 Opciones Disponibles

### Opción 1: Inicio Manual con Scripts (Recomendado para Pruebas)

**Ventajas:**
- ✅ Control total sobre cuándo iniciar el sistema
- ✅ Fácil de detener y reiniciar
- ✅ No requiere permisos de administrador

**Cómo usar:**
1. **Iniciar todo el sistema:**
   - Haz doble clic en `iniciar_sistema_completo.bat`
   - Se abrirán dos ventanas (Backend y Frontend)
   - El sistema estará disponible en:
     - Backend: http://127.0.0.1:8000/admin/
     - Frontend: http://localhost:5173/

2. **Iniciar solo el Backend:**
   - Haz doble clic en `Backend-Edificio55/iniciar_servidor.bat`

3. **Iniciar solo el Frontend:**
   - Haz doble clic en `Frontend-Edificio55/iniciar_frontend.bat`

4. **Detener el sistema:**
   - Haz doble clic en `detener_sistema_completo.bat`
   - O cierra las ventanas de los servidores

### Opción 2: Inicio Automático al Arrancar Windows (Recomendado para Producción)

**Ventajas:**
- ✅ El sistema se inicia automáticamente al encender la PC
- ✅ No requiere intervención manual
- ✅ Ideal para PC del aula que debe estar siempre disponible

**Cómo configurar:**

1. **Configurar inicio automático:**
   - Haz clic derecho en `configurar_inicio_automatico.bat`
   - Selecciona **"Ejecutar como administrador"**
   - Sigue las instrucciones en pantalla

2. **Verificar la configuración:**
   - Abre "Programador de tareas" (Task Scheduler)
   - Busca la tarea "SistemaLaboratorios_Inicio"
   - Verifica que esté habilitada

3. **Desactivar inicio automático (si es necesario):**
   - Haz clic derecho en `desactivar_inicio_automatico.bat`
   - Selecciona **"Ejecutar como administrador"**
   - O desde el Programador de tareas, deshabilita la tarea

## 📁 Estructura de Scripts

```
Proyecto/
├── iniciar_sistema_completo.bat      # Inicia Backend + Frontend
├── detener_sistema_completo.bat       # Detiene Backend + Frontend
├── configurar_inicio_automatico.bat   # Configura inicio automático
├── desactivar_inicio_automatico.bat   # Desactiva inicio automático
│
├── Backend-Edificio55/
│   ├── iniciar_servidor.bat          # Solo Backend
│   └── detener_servidor.bat          # Detener Backend
│
└── Frontend-Edificio55/
    ├── iniciar_frontend.bat          # Solo Frontend
    └── detener_frontend.bat          # Detener Frontend
```

## 🔧 Requisitos Previos

Antes de usar los scripts, asegúrate de tener:

1. **Python instalado** y en el PATH
   - Verifica: Abre CMD y escribe `python --version`
   - Si no funciona, instala Python desde python.org

2. **Node.js y npm instalados** y en el PATH
   - Verifica: Abre CMD y escribe `node --version` y `npm --version`
   - Si no funciona, instala Node.js desde nodejs.org

3. **Dependencias instaladas:**
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install` (se ejecuta automáticamente si falta)

4. **Base de datos configurada:**
   - PostgreSQL debe estar instalado y corriendo
   - La base de datos debe estar configurada en `settings.py`

## 🎓 Para la PC del Aula

### Configuración Inicial

1. **Instala todo el software necesario:**
   - Python
   - Node.js
   - PostgreSQL
   - Git (opcional, para actualizaciones)

2. **Copia todo el proyecto** a la PC del aula

3. **Configura la base de datos:**
   - Crea la base de datos PostgreSQL
   - Ejecuta las migraciones: `python manage.py migrate`
   - Crea un superusuario: `python manage.py createsuperuser`

4. **Instala las dependencias:**
   ```bash
   # Backend
   cd Backend-Edificio55
   pip install -r requirements.txt
   
   # Frontend
   cd ../Frontend-Edificio55
   npm install
   ```

5. **Configura el inicio automático:**
   - Ejecuta `configurar_inicio_automatico.bat` como administrador
   - Reinicia la PC para probar

### Uso Diario

**Con inicio automático configurado:**
- Simplemente enciende la PC
- El sistema se iniciará automáticamente
- Espera 30-60 segundos para que ambos servidores estén listos

**Sin inicio automático:**
- Haz doble clic en `iniciar_sistema_completo.bat`
- Espera a que se abran las ventanas
- El sistema estará listo

## 🛠️ Solución de Problemas

### El sistema no inicia automáticamente

1. **Verifica la tarea programada:**
   - Abre "Programador de tareas"
   - Busca "SistemaLaboratorios_Inicio"
   - Verifica que esté habilitada
   - Revisa el historial para ver errores

2. **Verifica las rutas:**
   - Asegúrate de que los scripts estén en las rutas correctas
   - No muevas los archivos después de configurar

3. **Verifica permisos:**
   - La tarea debe ejecutarse con permisos de administrador
   - Verifica en las propiedades de la tarea

### Los servidores no inician

1. **Verifica que Python y Node.js estén instalados:**
   ```cmd
   python --version
   node --version
   npm --version
   ```

2. **Verifica que las dependencias estén instaladas:**
   - Backend: Verifica que `venv` tenga las dependencias
   - Frontend: Verifica que `node_modules` exista

3. **Verifica los puertos:**
   - Puerto 8000 (Django) debe estar libre
   - Puerto 5173 (Vite) debe estar libre
   - Si están ocupados, cierra otros programas que los usen

### Error: "Python no está instalado"

- Instala Python desde python.org
- Durante la instalación, marca "Add Python to PATH"
- Reinicia la PC después de instalar

### Error: "Node.js no está instalado"

- Instala Node.js desde nodejs.org
- Reinicia la PC después de instalar

### Los servidores se cierran solos

1. **Revisa los logs en las ventanas de los servidores**
2. **Verifica que la base de datos esté corriendo:**
   - PostgreSQL debe estar activo
   - Verifica la conexión en `settings.py`

3. **Verifica el espacio en disco:**
   - Asegúrate de que haya espacio suficiente

## 🔒 Seguridad

- Los scripts se ejecutan con los permisos del usuario actual
- El inicio automático requiere permisos de administrador
- Considera crear un usuario específico para el sistema
- No compartas los scripts públicamente si contienen información sensible

## 📝 Notas Adicionales

- **Ventanas de los servidores:** Si configuras inicio automático, las ventanas se abrirán al iniciar sesión. Puedes minimizarlas.

- **Reinicio del sistema:** Si reinicias la PC, el sistema se iniciará automáticamente (si está configurado).

- **Cerrar sesión:** Si cierras sesión, los servidores se detendrán. Al iniciar sesión de nuevo, se reiniciarán automáticamente.

- **Actualizaciones:** Si actualizas el código, reinicia los servidores manualmente o reinicia la PC.

## 🆘 Soporte

Si tienes problemas:
1. Revisa los mensajes de error en las ventanas de los servidores
2. Verifica los logs de Windows Event Viewer
3. Consulta la documentación de Django y Vite
4. Verifica que todos los requisitos estén instalados correctamente

---

**¡Con estos scripts, el sistema estará siempre disponible sin intervención manual!** 🎉







