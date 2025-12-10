from src.models.user import db

class DeviceDoc(db.Model):
    __tablename__ = 'device_doc'
    
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(255), nullable=False)
    nombre_catalogo = db.Column(db.String(255), nullable=False)
    modelo_comercial = db.Column(db.String(255), nullable=False)
    modelo_tecnico = db.Column(db.String(255), nullable=False)
    tecnologia_modulacion_doc = db.Column(db.String(255))
    frecuencias_doc = db.Column(db.String(255))
    ganancia_antena_doc = db.Column(db.String(255))
    pire_dbm_doc = db.Column(db.String(255))
    pire_mw_doc = db.Column(db.String(255))

    def __repr__(self):
        return f'<DeviceDoc {self.nombre_catalogo}>'