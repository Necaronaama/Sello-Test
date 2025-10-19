from flask import Blueprint, request, send_from_directory, jsonify, abort
import os
from src.models.device import DeviceFile
from src.models.user import db

password_protected_downloads_bp = Blueprint("password_protected_downloads", __name__)

# Contraseña de ejemplo (¡En un entorno de producción, esto debería ser gestionado de forma segura!)
DOWNLOAD_PASSWORD = "Carmona2025"

# Directorio donde se almacenan los archivos adjuntos
# Corregido para apuntar a la ubicación real de los archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")

@password_protected_downloads_bp.route("/download-protected-file/<int:file_id>", methods=["GET"])
def download_protected_file(file_id):
    """
    Descarga un archivo protegido por contraseña usando el ID del archivo.
    """
    password = request.args.get("password")

    if not password or password != DOWNLOAD_PASSWORD:
        abort(401, description="Contraseña incorrecta o no proporcionada.")

    try:
        # Buscar el archivo en la base de datos por ID
        device_file = DeviceFile.query.get(file_id)
        
        if not device_file:
            abort(404, description="Archivo no encontrado en la base de datos.")
        
        # Obtener la ruta del archivo desde la base de datos
        file_path = device_file.file_path
        
        if not file_path:
            abort(404, description="Ruta del archivo no disponible.")
        
        # CORRECCIÓN CRÍTICA: Normalizar las barras de la ruta
        # La base de datos puede tener rutas con barras invertidas de Windows
        file_path = file_path.replace('\\', '/')
        
        # Construir la ruta completa al archivo
        if os.path.isabs(file_path):
            # Si la ruta es absoluta, usarla directamente
            full_file_path = file_path
        else:
            # Si es relativa, hay dos casos posibles:
            if file_path.startswith('src/'):
                # La ruta ya incluye 'src/', usar desde el directorio raíz del proyecto
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                full_file_path = os.path.join(project_root, file_path)
            else:
                # La ruta es relativa al UPLOAD_FOLDER
                full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
        
        # Normalizar la ruta completa para el sistema operativo actual
        full_file_path = os.path.normpath(full_file_path)
        
        # Verificar si el archivo existe
        if not os.path.exists(full_file_path):
            # Intentar rutas alternativas si no se encuentra
            alternative_paths = []
            
            # Alternativa 1: Desde el directorio raíz del proyecto
            if not file_path.startswith('src/'):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                alt_path1 = os.path.join(project_root, 'src', 'static', 'uploads', file_path)
                alternative_paths.append(alt_path1)
            
            # Alternativa 2: Solo el nombre del archivo en UPLOAD_FOLDER
            filename_only = os.path.basename(file_path)
            alt_path2 = os.path.join(UPLOAD_FOLDER, filename_only)
            alternative_paths.append(alt_path2)
            
            # Probar rutas alternativas
            for alt_path in alternative_paths:
                alt_path = os.path.normpath(alt_path)
                if os.path.exists(alt_path):
                    full_file_path = alt_path
                    break
            else:
                # Si ninguna ruta alternativa funciona, mostrar información de debug
                debug_info = {
                    "file_id": file_id,
                    "db_file_path": device_file.file_path,
                    "normalized_path": file_path,
                    "full_file_path": full_file_path,
                    "upload_folder": UPLOAD_FOLDER,
                    "alternatives_tried": alternative_paths,
                    "file_exists": os.path.exists(full_file_path)
                }
                abort(404, description=f"Archivo físico no encontrado. Debug: {debug_info}")
        
        # Obtener el directorio y nombre del archivo
        file_directory = os.path.dirname(full_file_path)
        filename = os.path.basename(full_file_path)
        
        # Usar el nombre original del archivo si está disponible
        download_name = device_file.file_name if device_file.file_name else filename
        
        return send_from_directory(
            file_directory, 
            filename, 
            as_attachment=True,
            download_name=download_name
        )
        
    except FileNotFoundError:
        abort(404, description="Archivo no encontrado.")
    except Exception as e:
        abort(500, description=f"Error interno del servidor: {str(e)}")

@password_protected_downloads_bp.route("/download-protected-file-by-path/<path:filename>", methods=["GET"])
def download_protected_file_by_path(filename):
    """
    Descarga un archivo protegido por contraseña usando la ruta del archivo.
    Esta función mantiene compatibilidad con el método anterior.
    """
    password = request.args.get("password")

    if not password or password != DOWNLOAD_PASSWORD:
        abort(401, description="Contraseña incorrecta o no proporcionada.")

    try:
        # Normalizar las barras de la ruta
        filename = filename.replace('\\', '/')
        
        # Limpiar el filename para evitar ataques de path traversal
        # Pero permitir subdirectorios legítimos como brands/APPLE/
        safe_filename = filename.replace('..', '').replace('//', '/')
        
        # Construir la ruta completa al archivo
        full_file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        full_file_path = os.path.normpath(full_file_path)
        
        # Verificar que la ruta esté dentro del directorio de uploads (seguridad)
        if not full_file_path.startswith(os.path.abspath(UPLOAD_FOLDER)):
            abort(403, description="Acceso denegado: ruta no permitida.")
        
        # Verificar si el archivo existe
        if not os.path.exists(full_file_path):
            abort(404, description="Archivo no encontrado.")
        
        # Obtener el directorio y nombre del archivo
        file_directory = os.path.dirname(full_file_path)
        basename = os.path.basename(full_file_path)
        
        return send_from_directory(file_directory, basename, as_attachment=True)
        
    except FileNotFoundError:
        abort(404, description="Archivo no encontrado.")
    except Exception as e:
        abort(500, description=f"Error interno del servidor: {str(e)}")
