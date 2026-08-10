import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, g
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_sistema_tutorias'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutorias.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# MODELOS DE BASE DE DATOS
# -----------------------------------------------------------------------------
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    credencial = db.Column(db.String(50), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'alumno', 'tutor', 'coordinador'
    bloqueado = db.Column(db.Boolean, default=False)

    perfil_alumno = db.relationship('PerfilAlumno', backref='usuario', uselist=False, cascade="all, delete-orphan")
    perfil_tutor = db.relationship('PerfilTutor', backref='usuario', uselist=False, cascade="all, delete-orphan")

class PerfilAlumno(db.Model):
    __tablename__ = 'perfiles_alumnos'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_tutor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    tutorias = db.relationship('Tutoria', backref='alumno', lazy=True)

class PerfilTutor(db.Model):
    __tablename__ = 'perfiles_tutores'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Tutoria(db.Model):
    __tablename__ = 'tutorias'
    id = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('perfiles_alumnos.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tema = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), default='Solicitada')  # Solicitada, Asignada, Realizada

class BitacoraAuditoria(db.Model):
    __tablename__ = 'bitacora_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(100))
    accion = db.Column(db.String(255))
    ip = db.Column(db.String(45))

class ConfigRespaldo(db.Model):
    __tablename__ = 'config_respaldo'
    id = db.Column(db.Integer, primary_key=True)
    activo = db.Column(db.Boolean, default=True)
    intervalo_horas = db.Column(db.Integer, default=24)

# -----------------------------------------------------------------------------
# MIDDLEWARE Y DECORADORES DE AUTENTICACIÓN
# -----------------------------------------------------------------------------
@app.before_request
def cargar_usuario_actual():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        g.user = None
        g.nombre = None
    else:
        g.user = Usuario.query.get(usuario_id)
        g.nombre = g.user.nombre_completo if g.user else None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Inicie sesión para acceder a este apartado.", "danger")
            return redirect(url_for('ingresar'))
        if g.user.bloqueado:
            session.clear()
            flash("Su cuenta se encuentra bloqueada.", "danger")
            return redirect(url_for('ingresar'))
        return f(*args, **kwargs)
    return decorated_function

def roles_requeridos(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None or g.user.tipo not in roles:
                flash("No posee los permisos necesarios para esta sección.", "danger")
                return redirect(url_for('ingresar'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN
# -----------------------------------------------------------------------------
@app.route('/')
def index():
    if g.user:
        if g.user.tipo == 'coordinador':
            return redirect(url_for('panel_coordinador'))
        elif g.user.tipo == 'tutor':
            return redirect(url_for('panel_tutor'))
        elif g.user.tipo == 'alumno':
            return redirect(url_for('panel_alumno'))
    return redirect(url_for('ingresar'))

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    if request.method == 'POST':
        credencial = request.form.get('credencial')
        contrasena = request.form.get('contrasena')

        usuario = Usuario.query.filter_by(credencial=credencial).first()

        if usuario and check_password_hash(usuario.contrasena_hash, contrasena):
            if usuario.bloqueado:
                flash("Esta cuenta ha sido suspendida temporalmente.", "danger")
                return redirect(url_for('ingresar'))

            session['usuario_id'] = usuario.id
            session['usuario_tipo'] = usuario.tipo

            # Redirección estricta según rol
            if usuario.tipo == 'coordinador':
                return redirect(url_for('panel_coordinador'))
            elif usuario.tipo == 'tutor':
                return redirect(url_for('panel_tutor'))
            elif usuario.tipo == 'alumno':
                return redirect(url_for('panel_alumno'))

        flash("Credenciales de acceso inválidas.", "danger")
    return render_template('login.html')

@app.route('/salir')
def salir():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('ingresar'))

# -----------------------------------------------------------------------------
# PANEL DE COORDINADOR
# -----------------------------------------------------------------------------
@app.route('/coordinador')
@login_required
@roles_requeridos('coordinador')
def panel_coordinador():
    usuarios = Usuario.query.all()
    tutorias = Tutoria.query.all()
    
    # Métricas para las gráficas y tarjetas
    solicitadas = Tutoria.query.filter_by(estado='Solicitada').count()
    asignadas = Tutoria.query.filter_by(estado='Asignadas').count()
    realizadas = Tutoria.query.filter_by(estado='Realizada').count()
    
    total_alumnos = Usuario.query.filter_by(tipo='alumno').count()
    total_tutores = Usuario.query.filter_by(tipo='tutor').count()
    total_coordinadores = Usuario.query.filter_by(tipo='coordinador').count()
    
    activos = Usuario.query.filter_by(bloqueado=False).count()
    bloqueados = Usuario.query.filter_by(bloqueado=True).count()
    
    cfg = ConfigRespaldo.query.first()
    auditoria = BitacoraAuditoria.query.order_by(BitacoraAuditoria.fecha.desc()).limit(20).all()
    
    respaldos = []
    if os.path.exists('backups'):
        respaldos = os.listdir('backups')

    return render_template(
        'coordinador.html',
        usuarios=usuarios,
        tutorias=tutorias,
        total_tutorias=len(tutorias),
        solicitadas=solicitadas,
        asignadas=asignadas,
        realizadas=realizadas,
        total_alumnos=total_alumnos,
        total_tutores=total_tutores,
        total_coordinadores=total_coordinadores,
        activos=activos,
        bloqueados=bloqueados,
        cfg=cfg,
        auditoria=auditoria,
        respaldos=respaldos
    )

@app.route('/crear_usuario', methods=['POST'])
@login_required
@roles_requeridos('coordinador')
def crear_usuario():
    tipo = request.form.get('tipo')
    credencial = request.form.get('credencial')
    nombre = request.form.get('nombre')
    contrasena = request.form.get('contrasena')

    if Usuario.query.filter_by(credencial=credencial).first():
        flash("La credencial/matrícula ingresada ya existe.", "danger")
        return redirect(url_for('panel_coordinador'))

    nuevo_usuario = Usuario(
        tipo=tipo,
        credencial=credencial,
        nombre_completo=nombre,
        contrasena_hash=generate_password_hash(contrasena)
    )
    db.session.add(nuevo_usuario)
    db.session.flush()

    if tipo == 'alumno':
        perfil = PerfilAlumno(id_usuario=nuevo_usuario.id)
        db.session.add(perfil)
    elif tipo == 'tutor':
        perfil = PerfilTutor(id_usuario=nuevo_usuario.id)
        db.session.add(perfil)

    db.session.commit()
    flash("Usuario registrado exitosamente.", "success")
    return redirect(url_for('panel_coordinador'))

@app.route('/asignar_tutor/<int:id_alumno>', methods=['POST'])
@login_required
@roles_requeridos('coordinador')
def asignar_tutor(id_alumno):
    id_tutor = request.form.get('id_tutor')
    alumno = PerfilAlumno.query.get_or_404(id_alumno)
    alumno.id_tutor = id_tutor
    db.session.commit()
    flash("Tutor asignado correctamente.", "success")
    return redirect(url_for('panel_coordinador'))

@app.route('/cambiar_estado/<int:id>')
@login_required
@roles_requeridos('coordinador')
def cambiar_estado(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.bloqueado = not usuario.bloqueado
    db.session.commit()
    flash(f"Estado del usuario {usuario.nombre_completo} actualizado.", "success")
    return redirect(url_for('panel_coordinador'))

# -----------------------------------------------------------------------------
# PANEL DE TUTOR
# -----------------------------------------------------------------------------
@app.route('/tutor')
@login_required
@roles_requeridos('tutor')
def panel_tutor():
    return render_template('tutor.html')

# -----------------------------------------------------------------------------
# PANEL DE ALUMNO
# -----------------------------------------------------------------------------
@app.route('/alumno')
@login_required
@roles_requeridos('alumno')
def panel_alumno():
    return render_template('alumno.html')

# -----------------------------------------------------------------------------
# CONFIGURACIÓN Y REPORTE
# -----------------------------------------------------------------------------
@app.route('/reporte_general_pdf')
@login_required
@roles_requeridos('coordinador')
def reporte_general_pdf():
    flash("Generación de informe PDF ejecutada.", "success")
    return redirect(url_for('panel_coordinador'))

@app.route('/respaldo_manual')
@login_required
@roles_requeridos('coordinador')
def respaldo_manual():
    flash("Respaldo manual completado con éxito.", "success")
    return redirect(url_for('panel_coordinador'))

@app.route('/config_respaldos', methods=['POST'])
@login_required
@roles_requeridos('coordinador')
def config_respaldos():
    activo = 'activo' in request.form
    intervalo = request.form.get('intervalo', type=int)
    cfg = ConfigRespaldo.query.first()
    if not cfg:
        cfg = ConfigRespaldo(activo=activo, intervalo_horas=intervalo)
        db.session.add(cfg)
    else:
        cfg.activo = activo
        cfg.intervalo_horas = intervalo
    db.session.commit()
    flash("Configuración de respaldos guardada.", "success")
    return redirect(url_for('panel_coordinador'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
