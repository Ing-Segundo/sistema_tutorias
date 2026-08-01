# Sistema de Tutorías — UTN 🎓

Sistema web integral para la gestión y seguimiento del proceso de tutorías académicas en la **Universidad Tecnológica de Nayarit**. Facilita la interacción entre alumnos, tutores y el departamento de coordinación, optimizando la asignación, la captura de evidencias y la generación de reportes institucionalizados.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, PyJWT, Werkzeug (Security)
- **Base de Datos:** SQLite
- **Generación de Documentos:** FPDF (`fpdf2`)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap / Jinja2 Templates
- **Concurrencia:** Threading nativo para tareas programadas (Respaldos automáticos)

---

## 👥 Roles y Funcionalidades Principales

### 🧑‍🎓 Alumno
- **Solicitar Tutoría:** Agenda citas de tutoría indicando fecha y tema.
- **Historial & Estado:** Consulta el estatus de sus tutorías (*Solicitada, Confirmada, En proceso, Realizada*).
- **Formatos e Informes:** Descarga reportes individuales en PDF de sus tutorías realizadas.

### 👨‍🏫 Tutor
- **Gestión de Citas:** Acepta, edita o rechaza solicitudes de tutorías recibidas.
- **Tutoría Individual (Ficha de Atención):** Inicia sesiones dinámicas registrando horario de inicio/salida, carrera, grupo, motivos, puntos relevantes, compromisos y observaciones.
- **Atención a Alumnos:** Mantiene actualizado su horario de atención y crea tutorías directas para sus alumnos asignados.
- **Reportes:** Exporta resúmenes en PDF y dashboards con estadísticas de atención.

### 👔 Coordinador General
- **Administración de Usuarios:** Crea nuevos usuarios (*Alumnos, Tutores, Coordinadores*) y gestiona el bloqueo/desbloqueo de cuentas.
- **Asignación:** Vincula alumnos a sus respectivos tutores académicos.
- **Seguridad & Auditoría:** Visualiza un *log* en tiempo real con IP, acciones y marcas de tiempo de los accesos al sistema.
- **Respaldos (Backups):** 
  - Ejecución de respaldos manuales de la base de datos `.db`.
  - Configuración de tareas de respaldo automático en segundo plano por intervalo de horas.
  - Restauración rápida de la base de datos desde la interfaz.
- **Estadísticas Globales:** Métricas generales del estado de todas las tutorías y usuarios activos/bloqueados.

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/sistema-tutorias-utn.git](https://github.com/tu-usuario/sistema-tutorias-utn.git)
cd sistema-tutorias-utn
