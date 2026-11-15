# 🚗 Autos Colombia - Sistema de Gestión de Parqueadero

Sistema de información web Full-Stack desarrollado para la gestión operativa y administrativa del parqueadero **Autos Colombia**, integrando los alcances de la **Iteración 1 (Control de Entrada y Salida de Vehículos)** y la **Iteración 2 (Gestión de Usuarios, Control de Acceso RBAC, Gestión de Celdas y Auditoría)**.

La plataforma permite controlar el acceso mediante roles diferenciados, administrar el catálogo de celdas, registrar ingresos y salidas en tiempo real con validación de mensualidad y monitorear la ocupación del establecimiento mediante un panel interactivo sincronizado.

---

## 📌 Características principales

### Operación de Portería (Iteración 1)

- **Control de capacidad base:** Gestión inicial de 80 celdas parametrizadas (70 para carros y 10 para motos), ampliable desde el módulo administrativo.
- **Registro de ingresos con validación:** Asignación de celdas disponibles según el tipo de vehículo, bloqueando el ingreso si la mensualidad está en estado `PENDIENTE` y aplicando control de concurrencia pesimista (`SELECT FOR UPDATE`) para evitar asignaciones simultáneas.
- **Tarifas mensuales:** Parametrización de $250.000 COP/mes para carros y $100.000 COP/mes para motos.
- **Liberación de celdas:** Registro de salidas por placa o celda asignada, liberando el espacio de inmediato.
- **Tablero de ocupación en tiempo real (Dashboard):** Indicadores dinámicos y mapa visual de celdas actualizado automáticamente mediante WebSockets sin recargar la página.
- **Edición y reasignación:** Corrección de datos de propietarios y vehículos (restringida a administradores) y reasignación de celdas ocupadas.

### Seguridad y Administración (Iteración 2)

- **Autenticación y control de acceso por roles (RBAC):** Inicio de sesión seguro con contraseñas cifradas mediante `bcrypt` y tokens `JWT`, diferenciando permisos entre **Administrador** y **Operador**.
- **Gestión de usuarios (Empleados):** Creación, consulta y desactivación (borrado lógico) de cuentas de operadores y administradores, preservando su trazabilidad histórica.
- **Gestión de celdas:** Creación, consulta con filtros, edición y eliminación controlada de celdas, validando códigos únicos e integridad referencial (impidiendo borrar celdas ocupadas o con historial activo).
- **Historial de auditoría:** Registro automático de cada movimiento crítico (ingresos, salidas, reasignaciones, creación o modificación de usuarios y celdas), incluyendo usuario responsable, fecha y hora, detalle e IP de origen.

---

## 🛠️ Arquitectura y tecnologías

El proyecto implementa una arquitectura modular por capas que desacopla la presentación, la lógica de negocio, el acceso a datos y la persistencia.

### Frontend

- **Angular:** Framework para el desarrollo de la interfaz web reactiva.
- **TypeScript:** Lenguaje principal para componentes, guardias de rutas, interceptores JWT y servicios.
- **HTML5, CSS3 y Tailwind CSS:** Diseño de interfaz adaptable con tema oscuro (*Dark Slate*).
- **WebSockets:** Cliente en tiempo real para sincronizar el estado de ocupación entre sesiones.

### Backend

- **Python y FastAPI:** API RESTful estructurada por capas (`api`, `services`, `repositories`, `models`, `schemas`, `core`).
- **SQLAlchemy:** ORM para el mapeo objeto-relacional y control transaccional.
- **Seguridad (JWT y Passlib/Bcrypt):** Autenticación basada en tokens Bearer y hash seguro de contraseñas.

### Base de datos

- **PostgreSQL:** Motor de base de datos relacional (`autos_colombia_db`).
- **Integridad referencial:** Relaciones normalizadas entre usuarios, clientes, vehículos, tipos de vehículo, celdas, registros de entrada y salida e historial de auditoría.

---

## 📋 Requisitos previos

Antes de instalar y ejecutar el proyecto, asegúrate de contar con las siguientes herramientas:

1. **Git:** Para clonar el repositorio y gestionar el control de versiones.
2. **Node.js:** Versión 18 o superior.
3. **Angular CLI:** Herramienta de línea de comandos de Angular.
4. **Python:** Versión 3.10 o superior.
5. **Pip:** Administrador de paquetes de Python.
6. **PostgreSQL:** Versión 14 o superior.
7. **pgAdmin 4:** Herramienta gráfica para administrar PostgreSQL.

Para instalar Angular CLI:

```bash
npm install -g @angular/cli
```

---

## 🚀 Guía de instalación y puesta en funcionamiento

Sigue los siguientes pasos para ejecutar la aplicación en un entorno local.

### 1. Clonar el repositorio

```bash
git clone https://github.com/Camilo-Alegria/autos-colombia-parking.git
cd autos-colombia-parking
```

### 2. Configurar la base de datos PostgreSQL

Abre pgAdmin 4 o accede a PostgreSQL mediante la consola `psql`.

Crea la base de datos ejecutando la siguiente instrucción SQL:

```sql
CREATE DATABASE autos_colombia_db;
```

Verifica que el servicio de PostgreSQL esté activo en el puerto predeterminado `5432`.

### 3. Configurar y ejecutar el Backend (FastAPI)

Abre una terminal y accede a la carpeta del backend:

```bash
cd backend
```

**Crear el entorno virtual:**

```bash
python -m venv venv
```

**Activar el entorno virtual:**

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Linux o macOS:

```bash
source venv/bin/activate
```

**Instalar las dependencias:**

```bash
pip install -r requirements.txt
```

**Configurar las variables de entorno:**

Crea un archivo `.env` tomando como referencia el archivo `.env.example` y configura tus credenciales de PostgreSQL (`DATABASE_URL`) y la clave secreta para JWT (`SECRET_KEY`).

**Iniciar el servidor:**

```bash
uvicorn app.main:app --reload
```

Al iniciar por primera vez, el sistema crea automáticamente las tablas, las 80 celdas base y los usuarios iniciales mediante `seed.py`.

Una vez iniciado, el backend estará disponible en:

- **API:** http://127.0.0.1:8000
- **Documentación interactiva (Swagger):** http://127.0.0.1:8000/docs
- **Documentación alternativa (ReDoc):** http://127.0.0.1:8000/redoc

### 4. Configurar y ejecutar el Frontend (Angular)

Abre una segunda terminal, manteniendo el backend en ejecución, y accede a la carpeta del frontend:

```bash
cd frontend
```

**Instalar las dependencias:**

```bash
npm install
```

**Iniciar la aplicación:**

```bash
ng serve --open
```

La aplicación estará disponible en el navegador en:

- **Frontend Web:** http://localhost:4200/

---

## 🔐 Acceso y roles de prueba

Al inicializar la base de datos, el sistema habilita cuentas base para validar los permisos RBAC.

| Rol | Usuario | Contraseña | Permisos principales |
|---|---|---|---|
| Administrador | `admin` | `admin123` | Acceso total: Dashboard, entradas y salidas, gestión de usuarios, gestión de celdas (CRUD), edición de vehículos e historial de auditoría. |
| Operador | Creado desde Admin | Asignada al crear | Operación de portería: Dashboard en tiempo real, registro de entradas y salidas, registro de nuevos vehículos y consulta de celdas disponibles. |

---

## 📂 Estructura del repositorio

```text
AutosColombia/
│
├── backend/
│   ├── app/
│   │   ├── api/                 # Endpoints REST (auth, usuarios, celdas, registros, auditoría, websockets)
│   │   ├── core/                # Configuración, conexión BD, seguridad JWT, seed inicial y WebSocket manager
│   │   ├── models/              # Modelos ORM SQLAlchemy
│   │   ├── repositories/        # Capa de acceso a datos y consultas transaccionales
│   │   ├── schemas/             # Esquemas Pydantic para validación de entrada y salida (DTO)
│   │   ├── services/            # Lógica de negocio y reglas de validación
│   │   └── main.py              # Punto de entrada de FastAPI y registro de routers
│   │
│   └── requirements.txt         # Dependencias de Python
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout/          # Estructura principal y navegación dinámica por rol
│   │   │   ├── models/          # Interfaces y modelos TypeScript
│   │   │   ├── pages/           # Vistas (login, dashboard, entrada, salida, editar, admin)
│   │   │   ├── services/        # Servicios HTTP, interceptor JWT y cliente WebSocket
│   │   │   ├── app.config.ts    # Configuración de proveedores e interceptores
│   │   │   └── app.routes.ts    # Rutas y protección por roles
│   │   └── assets/              # Recursos estáticos
│   │
│   └── package.json             # Dependencias y scripts de Node.js
│
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Archivos y carpetas excluidos de Git
└── README.md                    # Documentación del proyecto
```

---

## 💰 Tarifas y capacidad base

| Tipo de vehículo | Capacidad inicial | Tarifa mensual |
|---|---:|---:|
| Carros | 70 celdas | $250.000 COP |
| Motos | 10 celdas | $100.000 COP |
| **Total** | **80 celdas** | — |

**Nota:** Desde el módulo de Gestión de Celdas del panel administrativo es posible incorporar nuevas celdas o modificar las existentes, manteniendo las restricciones de integridad.

---

## 🎯 Alcance de las iteraciones

### Iteración 1 — Control de Entrada y Salida de Vehículos

Implementación del flujo operativo de ingreso y salida de vehículos, validación del estado de pago mensual, asignación de celdas por tipo de vehículo, reasignación de espacios y tablero de ocupación en tiempo real.

### Iteración 2 — Gestión de Usuarios y Gestión de Celdas

Incorporación de autenticación JWT con control de acceso basado en roles (RBAC), administración del ciclo de vida de empleados (creación y baja lógica), administración completa del catálogo de celdas y módulo de auditoría transaccional.

---

## ✒️ Autor

- **Desarrollador:** Jhojanth Camilo Alegria Escobar
- **Materia:** Ingeniería de Software
- **Institución:** IU Digital de Antioquia
- **Proyecto:** Autos Colombia - Sistema de Gestión de Parqueadero

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos. Si deseas distribuirlo o permitir su reutilización, puedes agregar un archivo `LICENSE` con las condiciones correspondientes.
