import sqlite3

def migrate_db():
    conn = sqlite3.connect('src/database/app.db')
    cursor = conn.cursor()

    # Agregar las nuevas columnas de información técnica a la tabla device
    try:
        cursor.execute("ALTER TABLE device ADD COLUMN tecnologia_modulacion VARCHAR(255);")
        print("Columna 'tecnologia_modulacion' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columna 'tecnologia_modulacion' ya existe.")
        else:
            print(f"Error al agregar 'tecnologia_modulacion': {e}")

    try:
        cursor.execute("ALTER TABLE device ADD COLUMN frecuencias VARCHAR(255);")
        print("Columna 'frecuencias' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columna 'frecuencias' ya existe.")
        else:
            print(f"Error al agregar 'frecuencias': {e}")

    try:
        cursor.execute("ALTER TABLE device ADD COLUMN ganancia_antena VARCHAR(255);")
        print("Columna 'ganancia_antena' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columna 'ganancia_antena' ya existe.")
        else:
            print(f"Error al agregar 'ganancia_antena': {e}")

    try:
        cursor.execute("ALTER TABLE device ADD COLUMN pire_dbm DECIMAL(10,2);")
        print("Columna 'pire_dbm' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columna 'pire_dbm' ya existe.")
        else:
            print(f"Error al agregar 'pire_dbm': {e}")

    try:
        cursor.execute("ALTER TABLE device ADD COLUMN pire_mw DECIMAL(10,2);")
        print("Columna 'pire_mw' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columna 'pire_mw' ya existe.")
        else:
            print(f"Error al agregar 'pire_mw': {e}")

    conn.commit()
    conn.close()
    print("Migración de base de datos completada: nuevos campos de información técnica agregados.")

if __name__ == '__main__':
    migrate_db()

