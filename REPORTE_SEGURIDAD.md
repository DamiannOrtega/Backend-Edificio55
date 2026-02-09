# 🔒 Reporte de Seguridad - Sistema de Laboratorios Edificio 55

**Fecha**: 2026-02-09  
**Tipo de Despliegue**: Localhost (PC de escritorio en edificio universitario)  
**Base de Datos**: Supabase (Cloud)

---

## ✅ RESUMEN EJECUTIVO

Tu configuración actual de **localhost + Supabase** es **ADECUADA** para uso interno en el edificio universitario, pero se encontraron **vulnerabilidades críticas** que deben corregirse.

### Estado Actual:
- ✅ **Localhost es seguro** para acceso local
- ✅ **Variables de entorno** implementadas correctamente
- ⚠️ **Credenciales expuestas** en múltiples archivos (CORREGIDO)
- ⚠️ **CORS abierto** a todo Internet (CORREGIDO)

---

## 🔒 VULNERABILIDADES ENCONTRADAS Y CORREGIDAS

### 1. ✅ **CORREGIDO: Credenciales Hardcodeadas**

**Problema Original:**
- Contraseña de Supabase visible en 3 archivos `.bat`
- Contraseña comentada en `settings.py`

**Archivos Modificados:**
- ✅ `migrate_with_pgdump.bat` - Ahora lee credenciales de `.env`
- ✅ `restore_from_sql.bat` - Ahora lee credenciales de `.env`
- ✅ `settings.py` - Eliminado código comentado con contraseña

**Acción Requerida:**
```
⚠️ DEBES CAMBIAR TU CONTRASEÑA DE SUPABASE INMEDIATAMENTE
```

**Pasos:**
1. Ve a tu dashboard de Supabase: https://app.supabase.com
2. Navega a: Settings → Database → Database password
3. Haz clic en "Reset database password"
4. Copia la nueva contraseña
5. Actualiza **SOLO** el archivo `.env`:
   ```env
   DB_PASSWORD=TU_NUEVA_CONTRASEÑA_AQUÍ
   ```

### 2. ✅ **CORREGIDO: CORS Abierto**

**Problema Original:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ Permitía acceso desde cualquier sitio web
```

**Solución Aplicada:**
```python
CORS_ALLOW_ALL_ORIGINS = False  # ✅ Solo localhost permitido
```

Ahora solo estas URLs pueden acceder a tu API:
- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:8080`
- `http://127.0.0.1:8080`

---

## 🛡️ RECOMENDACIONES ADICIONALES

### **PRIORIDAD ALTA** 🔴

#### 1. **Protección Física de la PC**
Como el sistema corre en una PC de escritorio accesible:

**Implementar:**
- ✅ Bloquear Windows automáticamente después de 5 minutos de inactividad
- ✅ Usar contraseña fuerte en Windows
- ✅ No dejar la sesión abierta sin supervisión

**Configuración de Windows:**
```
1. Configuración → Cuentas → Opciones de inicio de sesión
2. Activar "Requerir inicio de sesión" → "Cuando el equipo se reactive"
3. Configuración → Sistema → Energía y suspensión
4. "Pantalla" → Establecer en 5 minutos
```

#### 2. **Cambiar DEBUG a False en Producción**

**Archivo:** `.env`

**Cambiar de:**
```env
DEBUG=True
```

**A:**
```env
DEBUG=False
```

**IMPORTANTE:** Solo hazlo cuando el sistema esté completamente probado, ya que DEBUG=True ayuda durante desarrollo.

#### 3. **Restringir ALLOWED_HOSTS**

**Archivo:** `.env`

**Cambiar de:**
```env
ALLOWED_HOSTS=*
```

**A:**
```env
ALLOWED_HOSTS=localhost,127.0.0.1
```

### **PRIORIDAD MEDIA** 🟡

#### 4. **Implementar Auto-Logout en el Frontend**

Agregar timeout de sesión después de inactividad:

```typescript
// Agregar en LabVisitForm.tsx
useEffect(() => {
  let timeout: NodeJS.Timeout;
  
  const resetTimer = () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      // Auto-logout después de 15 minutos de inactividad
      window.location.reload();
      toast.info("Sesión reiniciada por inactividad");
    }, 15 * 60 * 1000); // 15 minutos
  };
  
  window.addEventListener('mousemove', resetTimer);
  window.addEventListener('keypress', resetTimer);
  
  resetTimer();
  
  return () => {
    clearTimeout(timeout);
    window.removeEventListener('mousemove', resetTimer);
    window.removeEventListener('keypress', resetTimer);
  };
}, []);
```

#### 5. **Backups Regulares**

**Configurar backup automático:**
```batch
REM Crear archivo: backup_diario.bat
@echo off
set BACKUP_DIR=C:\Backups\Edificio55
set FECHA=%date:~-4,4%%date:~-10,2%%date:~-7,2%

REM Crear directorio si no existe
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Backup usando pg_dump
pg_dump -h aws-1-us-east-1.pooler.supabase.com -U postgres.zrtbnovaxukwsyomasfx -d postgres -F c -f "%BACKUP_DIR%\backup_%FECHA%.dump"

echo Backup completado: %BACKUP_DIR%\backup_%FECHA%.dump
```

**Programar en Windows:**
1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Ejecutar `backup_diario.bat` todos los días a las 11:00 PM

### **PRIORIDAD BAJA** 🟢

#### 6. **Logging de Accesos**

Agregar registro de quién usa el sistema:

```python
# En views.py
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def registrar_visita(request):
    logger.info(f"Registro de visita - ID: {request.data.get('id_estudiante')} - IP: {request.META.get('REMOTE_ADDR')}")
    # ... resto del código
```

---

## 📊 ANÁLISIS DE RIESGOS

### **Riesgos Residuales (Después de las correcciones)**

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Acceso físico no autorizado | Media | Alto | Bloqueo automático de Windows |
| Fallo de Supabase | Baja | Alto | Backups regulares |
| Pérdida de datos | Baja | Alto | Supabase tiene backups automáticos |
| Uso indebido por estudiantes | Baja | Bajo | Logs de acceso |

### **¿Es Seguro Usar Localhost?**

**SÍ**, para tu caso de uso es la opción más segura porque:

✅ **Ventajas:**
- No expuesto a Internet
- Solo accesible desde la PC física
- Protegido por firewall de Windows
- Sin necesidad de certificados SSL
- Configuración simple

❌ **Desventajas:**
- Requiere acceso físico a la PC
- No accesible remotamente (pero esto es lo que quieres)
- Dependiente de que la PC esté encendida

---

## 🎯 PLAN DE ACCIÓN INMEDIATO

### **Hoy (URGENTE):**
1. ✅ Cambiar contraseña de Supabase
2. ✅ Actualizar `.env` con nueva contraseña
3. ✅ Verificar que los archivos `.bat` funcionan con las nuevas variables

### **Esta Semana:**
4. ⬜ Configurar bloqueo automático de Windows
5. ⬜ Cambiar `DEBUG=False` después de pruebas
6. ⬜ Configurar backup automático diario

### **Este Mes:**
7. ⬜ Implementar auto-logout en frontend
8. ⬜ Agregar logging de accesos
9. ⬜ Documentar procedimientos de emergencia

---

## 📝 CHECKLIST DE SEGURIDAD

### Configuración Actual:
- [x] Variables de entorno en `.env`
- [x] `.env` en `.gitignore`
- [x] Credenciales removidas de archivos `.bat`
- [x] CORS restringido a localhost
- [ ] Contraseña de Supabase rotada
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS restringido
- [ ] Bloqueo automático de Windows
- [ ] Backups configurados

---

## 🆘 EN CASO DE EMERGENCIA

### Si sospechas que las credenciales fueron comprometidas:

1. **Inmediatamente:**
   - Cambiar contraseña de Supabase
   - Revisar logs de Supabase para accesos sospechosos

2. **Verificar:**
   - Dashboard de Supabase → Logs → Buscar IPs desconocidas
   - Revisar cambios recientes en la base de datos

3. **Contacto:**
   - Soporte de Supabase: support@supabase.io
   - Documentación: https://supabase.com/docs/guides/platform/going-into-prod

---

## 📚 RECURSOS ADICIONALES

- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/going-into-prod)
- [Django Security Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## ✅ CONCLUSIÓN

Tu configuración de **localhost + Supabase** es **SEGURA Y APROPIADA** para uso interno en el edificio universitario, siempre y cuando:

1. ✅ Cambies la contraseña de Supabase (expuesta en archivos)
2. ✅ Mantengas la PC físicamente segura
3. ✅ Implementes las recomendaciones de prioridad alta

**No hay problema en usar localhost** para este caso de uso. De hecho, es más seguro que exponerlo a Internet.

---

**Última actualización:** 2026-02-09  
**Próxima revisión recomendada:** 2026-03-09
