# 🚗 Autos Colombia - Sistema de Gestión de Parqueadero

Sistema de información web Full-Stack desarrollado para la gestión operativa del parqueadero **Autos Colombia**, correspondiente a la **Iteración 1: Control de Entrada y Salida de Vehículos**.

La plataforma permite registrar ingresos y salidas de vehículos, asignar celdas de parqueadero según el tipo de vehículo y monitorear la ocupación del establecimiento mediante un panel de control interactivo.

---

## 📌 Características principales

- **Control de capacidad:** Gestión de 80 celdas de parqueadero, distribuidas en 70 para carros y 10 para motos.
- **Registro de ingresos:** Selección y asignación de celdas disponibles según la categoría del vehículo.
- **Tarifas mensuales:** Tarifa de $250.000 COP para carros y $100.000 COP para motos.
- **Liberación de celdas:** Registro de salidas mediante la placa del vehículo o la celda asignada, actualizando la disponibilidad en tiempo real.
- **Tablero de ocupación (Dashboard):** Visualización de indicadores sobre el total de vehículos ingresados y la disponibilidad de celdas.
- **Edición y reasignación:** Corrección de los datos de propietarios y vehículos, así como cambio de celdas ocupadas.

---

## 🛠️ Arquitectura y tecnologías

El proyecto implementa una arquitectura de tres capas que separa la interfaz de usuario, la lógica de negocio y el almacenamiento de datos.

### Frontend
- **Angular:** Framework para el desarrollo de interfaces web dinámicas.
- **TypeScript:** Lenguaje de programación utilizado para la lógica del frontend.
- **HTML5 y CSS3:** Tecnologías para la estructura y el diseño de la interfaz.

### Backend
- **Python:** Lenguaje de programación para la lógica del servidor.
- **FastAPI:** Framework para la construcción de una API REST.
- **SQLAlchemy:** ORM para la interacción con la base de datos relacional.

### Base de datos
- **PostgreSQL:** Sistema de gestión de bases de datos relacionales.
- **Nombre de la base de datos:** `autos_colombia_db`.
- **Integridad referencial:** Gestión de las relaciones entre las entidades del sistema.

---

## 📋 Requisitos previos

Antes de instalar y ejecutar el proyecto, asegúrate de contar con las siguientes herramientas:

1. **Git:** Para clonar el repositorio y gestionar el control de versiones.
2. **Node.js:** Versión 18 o superior, compatible con las dependencias del proyecto.
3. **Angular CLI:** Herramienta de línea de comandos de Angular.
4. **Python:** Versión 3.10 o superior.
5. **Pip:** Administrador de paquetes de Python.
6. **PostgreSQL:** Versión 14 o superior.
7. **pgAdmin 4:** Herramienta gráfica para administrar PostgreSQL.

### Instalación de Angular CLI

Si todavía no tienes Angular CLI instalado, ejecuta el siguiente comando:

```bash
npm install -g @angular/cli
```

---

## 🚀 Guía de instalación y puesta en funcionamiento

Sigue los pasos en orden para ejecutar la aplicación en un entorno local.

### 1. Clonar el repositorio

Abre una terminal y ejecuta los siguientes comandos:

```bash
git clone https://github.com/Camilo-Alegria/autos-colombia-parking.git
cd autos-colombia-parking
```

### 2. Configurar la base de datos PostgreSQL

1. Abre pgAdmin 4 o accede a PostgreSQL mediante la consola `psql`.
2. Crea la base de datos ejecutando la siguiente instrucción SQL:

```sql
CREATE DATABASE autos_colombia_db;
```

3. Verifica que el servicio de PostgreSQL esté activo y escuchando en el puerto predeterminado `5432`.
4. Configura los parámetros de conexión a la base de datos en el backend, según la configuración definida en el proyecto.

**Nota:** Asegúrate de que el usuario, la contraseña, el host y el nombre de la base de datos coincidan con los parámetros de conexión configurados en la aplicación.

### 3. Configurar y ejecutar el backend (FastAPI)

Abre una terminal y accede a la carpeta del backend:

```bash
cd backend
```

#### Crear el entorno virtual

```bash
python -m venv venv
```

#### Activar el entorno virtual

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux o macOS:**

```bash
source venv/bin/activate
```

#### Instalar las dependencias

```bash
pip install -r requirements.txt
```

#### Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

Una vez iniciado, el backend estará disponible en:

- **API:** http://127.0.0.1:8000
- **Documentación interactiva (Swagger):** http://127.0.0.1:8000/docs
- **Documentación alternativa (ReDoc):** http://127.0.0.1:8000/redoc

La documentación interactiva permite consultar y probar los endpoints disponibles en la API.

### 4. Configurar y ejecutar el frontend (Angular)

Abre una segunda terminal, manteniendo el backend en ejecución, y accede a la carpeta del frontend:

```bash
cd frontend
```

#### Instalar las dependencias

```bash
npm install
```

#### Iniciar el servidor de desarrollo

```bash
ng serve --open
```

La aplicación estará disponible en el navegador en la siguiente dirección:

http://localhost:4200/

**Nota:** Si Angular no abre el navegador automáticamente, puedes ingresar manualmente a la dirección indicada.

---

## 📂 Estructura del repositorio

La estructura general del proyecto está organizada de la siguiente manera:

```text
AutosColombia/
├── backend/
│   ├── app/
│   │   ├── main.py          # Punto de entrada y rutas de la API
│   │   ├── database.py      # Configuración de la conexión a PostgreSQL
│   │   └── models.py        # Modelos ORM de la base de datos
│   └── requirements.txt     # Dependencias de Python
│
├── frontend/
│   ├── src/
│   │   ├── app/             # Componentes, servicios y modelos
│   │   └── assets/          # Recursos estáticos
│   └── package.json         # Dependencias y scripts de Node.js
│
├── .gitignore               # Archivos y carpetas excluidos de Git
└── README.md                # Documentación del proyecto
```

---

## 💰 Tarifas del servicio

| Tipo de vehículo | Capacidad | Tarifa mensual |
|---|---:|---:|
| Carros | 70 celdas | $250.000 COP |
| Motos | 10 celdas | $100.000 COP |
| **Total** | **80 celdas** | — |

Las tarifas corresponden a los valores definidos para el proyecto y pueden utilizarse como referencia para la parametrización del sistema.

---

## 🎯 Objetivo de la iteración 1

Desarrollar un sistema de información web que permita administrar el ingreso y la salida de vehículos del parqueadero Autos Colombia, controlar la disponibilidad de las celdas y facilitar el seguimiento de la ocupación mediante una interfaz intuitiva.

Esta primera iteración se centra en las operaciones esenciales de control de entrada y salida, la asignación de espacios y la consulta de la ocupación del parqueadero.

---

## ✒️ Autor

- **Desarrollador:** Jhojanth Camilo Alegria Escobar
- **Materia:** Ingeniería de Software.
- **Institución:** IU Digital de Antioquia.
- **Proyecto:** Autos Colombia - Sistema de Gestión de Parqueadero.

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos. Si deseas distribuirlo o permitir su reutilización, puedes agregar un archivo `LICENSE` con las condiciones correspondientes.

