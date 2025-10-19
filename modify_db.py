
import sqlite3

def migrate_db():
    conn = sqlite3.connect('src/database/app.db')
    cursor = conn.cursor()

    # 1. Rename the old device table
    cursor.execute("ALTER TABLE device RENAME TO old_device;")

    # 2. Create the new device table with new columns
    cursor.execute("""
        CREATE TABLE device (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            marca VARCHAR(100) NOT NULL,
            nombre_catalogo VARCHAR(200) NOT NULL,
            modelo_comercial VARCHAR(100) NOT NULL,
            modelo_tecnico VARCHAR(100) NOT NULL,
            ano_lanzamiento INTEGER NOT NULL,
            comentarios TEXT,
            comentario_subtel TEXT,
            fecha_vigencia DATE NOT NULL,
            categoria VARCHAR(50) NOT NULL,
            subcategoria VARCHAR(50) NOT NULL,
            grupo VARCHAR(50) NOT NULL,
            importador_representante VARCHAR(255),
            domicilio VARCHAR(255),
            correo_contacto VARCHAR(255),
            created_at DATETIME,
            updated_at DATETIME,
            fabricante VARCHAR(100)
        );
    """)

    # 3. Copy data from old_device to device
    cursor.execute("""
        INSERT INTO device (
            id, marca, nombre_catalogo, modelo_comercial, modelo_tecnico,
            ano_lanzamiento, comentarios, comentario_subtel, fecha_vigencia,
            categoria, subcategoria, grupo, created_at, updated_at, fabricante
        )
        SELECT
            id, marca, nombre_catalogo, modelo_comercial, modelo_tecnico,
            ano_lanzamiento, comentarios, comentario_subtel, fecha_vigencia,
            categoria, subcategoria, grupo, created_at, updated_at, fabricante
        FROM old_device;
    """)

    # 4. Drop the old device table
    cursor.execute("DROP TABLE old_device;")

    conn.commit()
    conn.close()
    print("Database migration complete: 'device' table updated with new columns.")

if __name__ == '__main__':
    migrate_db()


