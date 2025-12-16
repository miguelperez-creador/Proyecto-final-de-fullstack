# 📘 Manual de Usuario – Sistema Help Desk

## 🔐 1. Inicio de Sesión

Para acceder al sistema:

1. Ingresar el correo electrónico y la contraseña registrada.
2. Si no se posee cuenta, hacer clic en **Create New Account** para registrarse.

> Nota: Al registrarse, el rol asignado automáticamente es **USER**.

---

## 🎫 2. Crear Ticket

> Disponible únicamente para usuarios con rol **USER**.

1. Una vez iniciado sesión, en el **Dashboard** aparecerá la opción **New Ticket**.
2. Completar los campos:

   * Título del ticket
   * Descripción
3. Hacer clic en **Enviar** para registrar el ticket.

---

## 📋 3. Ver Tickets

* Acceder a la sección **Tickets** en el **navbar**.
* Ver la lista de tickets según el rol:

  * **USER:** Sus propios tickets
  * **AGENT:** Tickets asignados
  * **ADMIN:** Todos los tickets
* Para ver más detalles de un ticket, hacer clic en el botón **See** correspondiente.

---

## 👥 4. Roles y Permisos

### 🔴 Admin

El **Admin** puede:

* Ver la lista de todos los usuarios registrados
* Asignar y modificar roles de usuarios
* Asignar tickets a agentes
* Cambiar el estado de cualquier ticket

> El Admin **no puede crear tickets**.

### 🟡 Agent

El **Agent** puede:

* Ver y manejar los tickets asignados
* Actualizar el estado de los tickets
* Agregar comentarios a los tickets

> El Agent **no puede crear tickets ni ver la lista de usuarios**.

### 🟢 User

El **User** puede:

* Crear nuevos tickets
* Ver el estado de sus propios tickets
* Agregar comentarios a sus tickets

> El User **no puede modificar tickets de otros usuarios ni gestionar roles**.

---

**Documento elaborado con fines académicos como parte del proyecto final del curso de Full Stack.**
