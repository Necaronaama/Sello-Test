#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import db
from src.models.device import Device
from datetime import datetime, date

def create_test_devices():
    with app.app_context():
        # Verificar si ya existen dispositivos
        existing_devices = Device.query.count()
        if existing_devices > 0:
            print(f"Ya existen {existing_devices} dispositivos en la base de datos.")
            return

        # Crear dispositivos de prueba con diferentes marcas
        test_devices = [
            {
                'marca': 'Samsung',
                'nombre_catalogo': 'Galaxy S24 Ultra',
                'modelo_comercial': 'SM-S928B',
                'modelo_tecnico': 'SM-S928B/DS',
                'ano_lanzamiento': 2024,
                'comentarios': 'Smartphone premium con S Pen integrado',
                'comentario_subtel': 'Cumple con normativas de radiofrecuencia',
                'fecha_vigencia': date(2024, 1, 15),
                'categoria': 'Teléfono celular',
                'subcategoria': 'Smartphone',
                'grupo': '2024'
            },
            {
                'marca': 'Samsung',
                'nombre_catalogo': 'Galaxy Tab S9',
                'modelo_comercial': 'SM-X710',
                'modelo_tecnico': 'SM-X710/NZAAXAR',
                'ano_lanzamiento': 2023,
                'comentarios': 'Tablet premium con pantalla AMOLED',
                'comentario_subtel': 'Certificado para uso en Chile',
                'fecha_vigencia': date(2023, 8, 1),
                'categoria': 'Tablet',
                'subcategoria': 'Tablet A',
                'grupo': '2023'
            },
            {
                'marca': 'Apple',
                'nombre_catalogo': 'iPhone 15 Pro',
                'modelo_comercial': 'A3102',
                'modelo_tecnico': 'iPhone16,1',
                'ano_lanzamiento': 2023,
                'comentarios': 'iPhone con chip A17 Pro y cámara de 48MP',
                'comentario_subtel': 'Homologado por SUBTEL',
                'fecha_vigencia': date(2023, 9, 22),
                'categoria': 'Teléfono celular',
                'subcategoria': 'Smartphone',
                'grupo': '2023'
            },
            {
                'marca': 'Apple',
                'nombre_catalogo': 'iPad Pro 12.9',
                'modelo_comercial': 'A2764',
                'modelo_tecnico': 'iPad14,6',
                'ano_lanzamiento': 2022,
                'comentarios': 'iPad Pro con chip M2 y pantalla Liquid Retina XDR',
                'comentario_subtel': 'Cumple normativas técnicas chilenas',
                'fecha_vigencia': date(2022, 10, 18),
                'categoria': 'Tablet',
                'subcategoria': 'iPad',
                'grupo': '2022'
            },
            {
                'marca': 'Xiaomi',
                'nombre_catalogo': 'Redmi Note 13 Pro',
                'modelo_comercial': '23124RN87G',
                'modelo_tecnico': 'garnet_global',
                'ano_lanzamiento': 2024,
                'comentarios': 'Smartphone con cámara de 200MP y carga rápida',
                'comentario_subtel': 'Autorizado para comercialización',
                'fecha_vigencia': date(2024, 1, 10),
                'categoria': 'Teléfono celular',
                'subcategoria': 'Smartphone',
                'grupo': '2024'
            },
            {
                'marca': 'Xiaomi',
                'nombre_catalogo': 'Mi Pad 6',
                'modelo_comercial': '23073RPBFG',
                'modelo_tecnico': 'pipa_global',
                'ano_lanzamiento': 2023,
                'comentarios': 'Tablet con Snapdragon 870 y pantalla 2.8K',
                'comentario_subtel': 'Certificación SUBTEL vigente',
                'fecha_vigencia': date(2023, 6, 15),
                'categoria': 'Tablet',
                'subcategoria': 'Android Tablet',
                'grupo': '2023'
            },
            {
                'marca': 'Huawei',
                'nombre_catalogo': 'P60 Pro',
                'modelo_comercial': 'ALN-L29',
                'modelo_tecnico': 'ALN-L29',
                'ano_lanzamiento': 2023,
                'comentarios': 'Smartphone con sistema de cámara Leica',
                'comentario_subtel': 'Homologación SUBTEL aprobada',
                'fecha_vigencia': date(2023, 4, 20),
                'categoria': 'Teléfono celular',
                'subcategoria': 'Smartphone',
                'grupo': '2023'
            },
            {
                'marca': 'Sony',
                'nombre_catalogo': 'Xperia 1 V',
                'modelo_comercial': 'XQ-DQ72',
                'modelo_tecnico': 'XQ-DQ72',
                'ano_lanzamiento': 2023,
                'comentarios': 'Smartphone con pantalla 4K OLED y cámaras profesionales',
                'comentario_subtel': 'Cumple estándares de emisión RF',
                'fecha_vigencia': date(2023, 5, 11),
                'categoria': 'Teléfono celular',
                'subcategoria': 'Smartphone',
                'grupo': '2023'
            }
        ]

        # Crear dispositivos
        for device_data in test_devices:
            device = Device(**device_data)
            db.session.add(device)

        db.session.commit()
        print(f"Se crearon {len(test_devices)} dispositivos de prueba.")
        
        # Mostrar resumen por marca
        brands = db.session.query(Device.marca).distinct().all()
        print("\nDispositivos por marca:")
        for brand in brands:
            count = Device.query.filter_by(marca=brand[0]).count()
            print(f"- {brand[0]}: {count} dispositivos")

if __name__ == '__main__':
    create_test_devices()

