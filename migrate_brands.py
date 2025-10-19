#!/usr/bin/env python3
"""
Script para migrar marcas existentes del sistema antiguo al nuevo modelo Brand
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db
from src.models.device import Device
from src.models.brand import Brand

def migrate_brands():
    """Migrar marcas existentes al nuevo modelo Brand"""
    with app.app_context():
        print("Iniciando migración de marcas...")
        
        # Obtener todas las marcas únicas de la tabla Device
        existing_brands = db.session.query(Device.marca).distinct().all()
        
        migrated_count = 0
        
        for brand_tuple in existing_brands:
            brand_name = brand_tuple[0]
            
            if not brand_name or brand_name.strip() == "":
                continue
                
            # Verificar si la marca ya existe en la tabla Brand
            existing_brand = Brand.query.filter(Brand.name == brand_name).first()
            
            if not existing_brand:
                # Crear nueva entrada en Brand
                new_brand = Brand(
                    name=brand_name,
                    url=None,  # Las marcas migradas no tienen URL inicialmente
                    image_path=None  # Se puede configurar manualmente después
                )
                
                db.session.add(new_brand)
                migrated_count += 1
                print(f"Migrando marca: {brand_name}")
            else:
                print(f"Marca ya existe: {brand_name}")
        
        try:
            db.session.commit()
            print(f"Migración completada. {migrated_count} marcas migradas.")
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate_brands()

