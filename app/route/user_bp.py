from flask import Blueprint, request
from app.services.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/user")


def _user_to_dict(u):
    return {"id": u.id, "name": u.name, "email": u.email}


@user_bp.route("/all", methods=["GET"])
def get_all_users():
    try:
        users = UserService.list_users()
        return {"users": [_user_to_dict(u) for u in users]}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id: int):
    try:
        user = UserService.get_user(user_id)
        if user is None:
            return {"error": "User not found."}, 404
        return {"user": _user_to_dict(user)}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route("/create", methods=["POST"])
def create_user():
    try:
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")

        user = UserService.create_user(name=name, email=email)
        return {"message": "User created.", "user": _user_to_dict(user)}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    try:
        UserService.delete_user(user_id)
        return {"message": "User deleted."}, 200
    except Exception as e:
        return {"error": str(e)}, 400
