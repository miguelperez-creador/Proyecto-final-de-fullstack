# 📖 Manual Técnico – Sistema Help Desk

## 1. Descripción General

Este documento describe la arquitectura, configuración y funcionamiento técnico del **Sistema de Help Desk**, desarrollado como **proyecto final Full Stack**. La aplicación permite la gestión de tickets de soporte, usuarios y roles, integrando frontend, backend y base de datos.

---

## 🏗️ 2. Arquitectura del Sistema

El sistema está dividido en tres capas principales:

### 🎨 Front-End

El **front-end** contiene toda la interfaz visual que el usuario ve al acceder a la aplicación. Está construido con **HTML, CSS, Bootstrap y jQuery**.
La información que se muestra depende del **rol del usuario autenticado**, controlando el acceso a botones, formularios y vistas.

---

### ⚙️ Back-End

El **back-end** contiene la lógica principal del sistema y está desarrollado con **Python y Flask**.
Desde aquí se manejan:

* Autenticación y sesiones de usuario
* Autorización por roles
* Rutas (endpoints)
* Lógica de negocio de tickets y usuarios
* Comunicación con la base de datos

Los datos se envían a las vistas HTML mediante plantillas Jinja2.

---

### 🗄️ Base de Datos

La base de datos es **MariaDB**, y contiene **tres tablas principales**:

* **users**
* **tickets**
* **ticket_comments**

Estas tablas permiten manejar usuarios, tickets y el historial de comentarios.

---

## 🔄 3. Modificaciones y Funcionalidades Implementadas

Durante el desarrollo del proyecto se implementaron las siguientes mejoras:

* Se creó el endpoint **register** para el registro de nuevos usuarios.

  * Por defecto, los usuarios creados reciben el rol **USER**.

* Se modificó la forma de acceder al detalle de un ticket:

  * En lugar de usar el ID directamente, se agregó un **botón de acceso**, mejorando la experiencia del usuario.

* Los usuarios con rol **ADMIN** y **AGENT** no pueden crear tickets.

  * Solo los usuarios **USER** tienen permiso para crear nuevos tickets.

* Se añadieron **filtros en la lista de tickets**:

  * Filtro por **status**
  * Filtro por **priority**
  * Orden por fecha de creación

---

## 🗄️ 4. Configuración de la Base de Datos

La base de datos utilizada es **MariaDB**.

### 4.1 Creación de la Base de Datos

```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE helpdesk_db;
```

### 4.2 Creación de Tablas

#### Tabla: users

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'AGENT', 'USER') NOT NULL DEFAULT 'USER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

#### Tabla: tickets

```sql
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED') NOT NULL DEFAULT 'OPEN',
    priority ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    assigned_to INT NULL,
    CONSTRAINT fk_tickets_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id)
);
```

---

#### Tabla: ticket_comments

```sql
CREATE TABLE ticket_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## ⚙️ 5. Configuración del Entorno

### Archivo `.env`

El proyecto utiliza variables de entorno para la configuración:

```env
SECRET_KEY="final_proyect"
DB_HOST="localhost"
DB_USER="your_user"
DB_PASSWORD="your_password"
DB_NAME="helpdesk_db"
```

---

## 📦 6. Instalación y Ejecución

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Ejecución del Proyecto

```bash
# Windows
python app.py

# macOS / Linux
python3 app.py
```

---

## 🛣️ 7. Rutas Principales del Sistema

* **dashboard**
  Panel principal con resumen de tickets y accesos principales.

* **register**
  Creación de nuevos usuarios.

* **login**
  Inicio de sesión del usuario.

* **logout**
  Cierre de sesión.

* **tickets_list**
  Lista de tickets con filtros.

* **ticket_new**
  Creación de un nuevo ticket (solo USER).

* **ticket_detail**
  Visualización del detalle de un ticket.



* **comment_add**
  Agregar comentarios a un ticket.

* **users_list**
  Lista de usuarios registrados.

* **user_change_role**
  Cambio de rol (exclusivo para ADMIN).

---

## 🔐 8. Roles del Sistema

* **ADMIN:** Control total del sistema y gestión de usuarios.
* **AGENT:** Seguimiento y manejo de tickets asignados.
* **USER:** Creación y seguimiento de tickets propios.

---

**Documento elaborado con fines académicos como parte del proyecto final del curso de Full Stack.**
