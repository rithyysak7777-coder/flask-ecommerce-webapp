from api import api_bp
from flask import jsonify, request
from extensions import db
from sqlalchemy import text
from models import User

@api_bp.get('/user')
def user():
    sql = text("SELECT username, email, role, profile FROM user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]
    return jsonify(rows)

# @api_bp.get('/user/<int:user_id>')
# def get_user_by_id(user_id):
#     sql = text("SELECT id, username, email, role, profile, status FROM user WHERE id = :user_id")
#     result = db.session.execute(sql, {"user_id": user_id}).fetchone()
#     if result:
#         return jsonify(dict(result._mapping))
#     return jsonify({"error": "User not found"}), 404