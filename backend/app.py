from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from db import execute
from routes import (
    health_routes,
    auth_routes,
    configuracion_routes,
    propietario_routes,
    gasto_routes,
    recibo_routes,
    anuncio_routes,
    reporte_routes,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Registrar blueprints (Controllers en MVC)
app.register_blueprint(health_routes.bp)
app.register_blueprint(auth_routes.bp)
app.register_blueprint(configuracion_routes.bp)
app.register_blueprint(propietario_routes.bp)
app.register_blueprint(gasto_routes.bp)
app.register_blueprint(recibo_routes.bp)
app.register_blueprint(anuncio_routes.bp)
app.register_blueprint(reporte_routes.bp)


def _ensure_extra_tables():
    execute(
        """
        CREATE TABLE IF NOT EXISTS pagos_gastos (
            id SERIAL PRIMARY KEY,
            gasto_id INTEGER NOT NULL REFERENCES gastos(id) ON DELETE CASCADE,
            monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
            fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS anuncios (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            contenido TEXT NOT NULL,
            tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('mantenimiento','pago','informativo')),
            fecha_publicacion DATE NOT NULL DEFAULT CURRENT_DATE,
            activo BOOLEAN DEFAULT TRUE
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS lecturas_anuncios (
            id SERIAL PRIMARY KEY,
            anuncio_id INTEGER NOT NULL REFERENCES anuncios(id) ON DELETE CASCADE,
            propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
            fecha_lectura TIMESTAMP DEFAULT NOW(),
            UNIQUE(anuncio_id, propietario_id)
        )
        """
    )


_ensure_extra_tables()

if __name__ == "__main__":
    app.run(debug=True)
