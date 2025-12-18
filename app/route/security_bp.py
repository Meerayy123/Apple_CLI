from flask import Blueprint
from app.db import db
from app.domain.security import Security

security_bp = Blueprint("security", __name__, url_prefix="/security")


def _security_to_dict(s):
    return {
        "id": s.id,
        "symbol": s.symbol,
        "name": s.name,
        "type": s.type,
        "price": s.price,
    }


@security_bp.route("/all", methods=["GET"])
def get_all_securities():
    try:
        securities = db.session.query(Security).order_by(Security.id).all()
        return {"securities": [_security_to_dict(s) for s in securities]}, 200
    except Exception as e:
        return {"error": str(e)}, 400
