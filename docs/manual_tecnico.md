<!-- MANUAL TÉCNICO -->

# Manual Técnico

## 1. Descripción del proyecto
- Proyecto Full Stack: Web App de Help Desk / Gestión de Biblioteca / etc.
- Tecnologías: Flask, MariaDB/MySQL, Bootstrap, jQuery, Python.

## 2. Arquitectura del proyecto
- Estructura de carpetas y archivos:
  - app.py / main.py → archivo principal de la aplicación
  - routes.py → rutas y vistas de Flask
  - templates/ → HTML templates
  - static/ → CSS, JS, imágenes
  - models.py → definición de modelos de base de datos
  - config.py → configuración del proyecto
  - venv/ → entorno virtual (no subir a GitHub)
- Descripción de cómo Flask se conecta con la base de datos y renderiza templates.

## 3. Base de datos
- Tablas, relaciones y llaves primarias / foráneas.
- Scripts SQL de creación de tablas si aplica.
- Ejemplos de registros.

## 4. Funcionalidades principales
- Login / logout
- CRUD de usuarios, libros, tickets, etc.
- Roles y permisos

## 5. Seguridad
- Hash de contraseñas
- Validaciones de formularios
- Protección de rutas por roles

## 6. Dependencias
- Listado de librerías de Python (`requirements.txt`)
- Versiones de librerías importantes

## 7. Configuración
- Variables de entorno
- Configuración de base de datos
