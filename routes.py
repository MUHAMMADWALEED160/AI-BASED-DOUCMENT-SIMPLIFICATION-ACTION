import io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
from models import db, User, Document
from utils import allowed_file, process_document

routes_bp = Blueprint('routes', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@routes_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))
    return render_template('index.html')

@routes_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user_docs = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).all()
    return render_template('dashboard.html', documents=user_docs)

@routes_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('routes.dashboard'))
        
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('routes.dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        file_data = file.read()
        
        if len(file_data) == 0:
            flash('The file is empty.', 'error')
            return redirect(url_for('routes.dashboard'))
            
        summary = process_document(filename, file_data)
        
        new_doc = Document(
            user_id=session['user_id'],
            filename=filename,
            file_data=file_data,
            mimetype=mimetype,
            summary_text=summary
        )
        
        db.session.add(new_doc)
        db.session.commit()
        
        flash('File successfully uploaded and processed!', 'success')
    else:
        flash('File type not allowed. Please upload valid documents.', 'error')
        
    return redirect(url_for('routes.dashboard'))

@routes_bp.route('/download/<string:doc_id>')
@login_required
def download(doc_id):
    user_id = session.get('user_id')
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    
    if not doc:
        flash('Document not found or you do not have permission to access it.', 'error')
        return redirect(url_for('routes.dashboard'))
        
    return send_file(
        io.BytesIO(doc.file_data),
        mimetype=doc.mimetype,
        as_attachment=True,
        download_name=doc.filename
    )

@routes_bp.route('/delete/<string:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    user_id = session.get('user_id')
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    
    if not doc:
        flash('Document not found or you do not have permission to delete it.', 'error')
        return redirect(url_for('routes.dashboard'))
        
    db.session.delete(doc)
    db.session.commit()
    
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('routes.dashboard'))

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
