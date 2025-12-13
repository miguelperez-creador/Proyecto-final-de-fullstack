from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)


def get_db_connection():
    return pymysql.connect(
        host=app.config["DB_HOST"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

# ---- Helpers ----


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_role" not in session or session["user_role"] not in roles:
                flash("No tienes permiso para acceder a esta página.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---- Rutas básicas ----


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Simple dashboard: counts (puedes extenderlo)
    user_id = session["user_id"]
    user_role = session["user_role"]

    conn = get_db_connection()
    with conn.cursor() as cursor:
        if user_role in ['ADMIN', 'AGENT']: # Total de tickets creado por todos los usuarios del programa
            cursor.execute("SELECT COUNT(*) AS total FROM tickets")
            total = cursor.fetchone()["total"]
            
            cursor.execute("SELECT status, COUNT(*) as cnt FROM tickets GROUP BY status") # Agrupa los tickets por status
            by_status = cursor.fetchall()
            
            stats = {
                "total": total,
                "by_status": by_status
            }
        else: # USER: Total de tickets creadas por el usuario
            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE created_by=%s", (user_id,))
            total_user_tickets = cursor.fetchone()["total"]
            
            stats = { "total_user_tickets": total_user_tickets}
        
    conn.close()
    return render_template("dashboard.html", stats=stats, user_role=user_role)

# ---- Auth ----


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Hash password
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si usuario existe
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for('login'))

        # Insertar usuario nuevo
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
        """, (name, email, password_hash))

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash(f"Bienvenido, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Email o contraseña inválidos.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login"))

# ---- Tickets ----


@app.route("/tickets")
@login_required
def tickets_list():
    user_id = session["user_id"]
    user_role = session["user_role"]
    conn = get_db_connection()
    with conn.cursor() as cursor:
        if user_role == "ADMIN":
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                ORDER BY t.created_at DESC
            """)
            tickets = cursor.fetchall()
        elif user_role == "AGENT":
            # agent sees tickets assigned to them or unassigned
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE t.assigned_to = %s OR t.assigned_to IS NULL
                ORDER BY t.created_at DESC
            """, (user_id,))
            tickets = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE t.created_by = %s
                ORDER BY t.created_at DESC
            """, (user_id,))
            tickets = cursor.fetchall()
    conn.close()
    return render_template("tickets_list.html", tickets=tickets)


@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
def ticket_new():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority") or "MEDIUM"
        created_by = session["user_id"]
        if not title or not description:
            flash("Título y descripción son obligatorios.", "warning")
            return redirect(url_for("ticket_new"))
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, created_by)
                VALUES (%s, %s, %s, %s)
            """, (title, description, priority, created_by))
            conn.commit()
        conn.close()
        flash("Ticket creado con éxito.", "success")
        return redirect(url_for("tickets_list"))
    return render_template("ticket_new.html")


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
@login_required
def ticket_detail(ticket_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            LEFT JOIN users a ON t.assigned_to = a.id
            WHERE t.id = %s
        """, (ticket_id,))
        ticket = cursor.fetchone()
        if not ticket:
            conn.close()
            flash("Ticket no encontrado.", "danger")
            return redirect(url_for("tickets_list"))

        cursor.execute("""
            SELECT c.*, u.name as user_name
            FROM ticket_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_at ASC
        """, (ticket_id,))
        comments = cursor.fetchall()

        cursor.execute(
            "SELECT id, name FROM users WHERE role IN ('ADMIN','AGENT')")
        agents = cursor.fetchall()
    conn.close()
    return render_template("ticket_detail.html", ticket=ticket, comments=comments, agents=agents)


@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
@login_required
def ticket_update(ticket_id):
    user_role = session["user_role"]
    if user_role not in ["ADMIN", "AGENT"]:
        flash("No tienes permiso para actualizar tickets.", "danger")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    status = request.form.get("status") or "OPEN"
    assigned_to = request.form.get("assigned_to") or None
    if assigned_to == "":
        assigned_to = None

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE tickets SET status = %s, assigned_to = %s WHERE id = %s",
                       (status, assigned_to, ticket_id))
        conn.commit()
    conn.close()
    flash("Ticket actualizado.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route("/tickets/<int:ticket_id>/comments", methods=["POST"])
@login_required
def comment_add(ticket_id):
    comment_text = request.form.get("comment")
    user_id = session["user_id"]
    if not comment_text or comment_text.strip() == "":
        flash("El comentario no puede estar vacío.", "warning")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO ticket_comments (ticket_id, user_id, comment) VALUES (%s, %s, %s)",
                       (ticket_id, user_id, comment_text))
        conn.commit()
    conn.close()
    flash("Comentario agregado.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

# Optional: AJAX endpoint to add comment and return it (puede usarse desde jQuery)


@app.route("/tickets/<int:ticket_id>/comments_ajax", methods=["POST"])
@login_required
def comment_add_ajax(ticket_id):
    comment_text = request.form.get("comment")
    user_id = session["user_id"]
    if not comment_text or comment_text.strip() == "":
        return jsonify({"error": "empty"}), 400
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO ticket_comments (ticket_id, user_id, comment) VALUES (%s, %s, %s)",
                       (ticket_id, user_id, comment_text))
        conn.commit()
        cursor.execute(
            "SELECT c.*, u.name as user_name FROM ticket_comments c JOIN users u ON c.user_id = u.id WHERE c.id = LAST_INSERT_ID()")
        comment = cursor.fetchone()
    conn.close()
    return jsonify(comment), 201

# ---- Users management (ADMIN) ----


@app.route("/users")
@login_required
@role_required("ADMIN")
def users_list():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
    conn.close()
    return render_template("users_list.html", users=users)


@app.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@role_required("ADMIN")
def user_change_role(user_id):
    new_role = request.form.get("role")
    if new_role not in ["ADMIN", "AGENT", "USER"]:
        flash("Rol inválido.", "danger")
        return redirect(url_for("users_list"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE users SET role = %s WHERE id = %s",
                       (new_role, user_id))
        conn.commit()
    conn.close()
    flash("Rol actualizado.", "success")
    return redirect(url_for("users_list"))

# ---- Utility route para crear hash de contraseña (solo local, no en producción) ----


@app.route("/generate_hash/<password>")
def gen_hash(password):
    # Uso local: visita /generate_hash/tuContraseña para obtener hash (solo en entorno dev)
    h = generate_password_hash(password)
    return {"hash": h}


if __name__ == "__main__":
    app.run(debug=False)
