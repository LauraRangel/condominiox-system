from flask import Blueprint, jsonify, request, send_file
import io

from middleware import get_payload, require_roles, auth_response
from services import reporte_service
from utils.logger import get_logger

bp = Blueprint("reportes", __name__)
log = get_logger(__name__)


@bp.get("/api/reportes/financiero")
def resumen_financiero():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    mes = (request.args.get("mes") or "").strip()
    return jsonify(reporte_service.get_resumen_financiero(mes))


@bp.get("/api/reportes/morosidad/excel")
def exportar_morosidad_excel():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    mes = (request.args.get("mes") or "").strip()
    limit_raw = request.args.get("limit", "100")
    try:
        limit = max(1, min(int(limit_raw), 500))
    except ValueError:
        limit = 100

    try:
        xlsx_bytes = reporte_service.exportar_morosidad_excel(mes, limit)
    except Exception as e:
        log.error("Error generando Excel morosidad", extra={"error": str(e), "tipo": type(e).__name__})
        return jsonify({"error": f"Error al generar el reporte: {type(e).__name__}: {e}"}), 500

    filename = f"morosidad_{mes or 'todos'}.xlsx"
    return send_file(
        io.BytesIO(xlsx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )
