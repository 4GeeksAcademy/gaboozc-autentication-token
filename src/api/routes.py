"""
This module handles the API routes, authentication, and private access.
"""
from flask import Flask, request, jsonify, Blueprint
from api.models import db, User
from api.utils import APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os

# Initialize Blueprint
api = Blueprint('api', __name__)

# Allow CORS requests
CORS(api)

# Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET", "mysecretkey")

# Token-required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith("Bearer "):
            return jsonify({"msg": "Token is missing"}), 401

        try:
            token = token.split(" ")[1]  # Remove "Bearer" prefix
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])

            if not current_user:
                return jsonify({"msg": "User not found"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# -------------------------
# 💡 ROUTES
# -------------------------

# 🚀 Signup Route
@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 409

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create new user
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


# 🔥 Login Route
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid email or password"}), 401

    # Generate JWT token
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"token": token, "msg": "Login successful"}), 200


# 🔒 Private Route (Protected)
@api.route('/private', methods=['GET'])
@token_required
def private(current_user):
    return jsonify({
        "msg": "Welcome to the private route!",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }), 200


# 🚪 Logout Route (Token is cleared on frontend)
@api.route('/logout', methods=['POST'])
def logout():
    """
    Since JWT is stateless, there's no real server-side logout.
    The frontend should clear the token from sessionStorage.
    """
    return jsonify({"msg": "Logged out successfully"}), 200


# 🌐 Default Route (Hello World Test)
@api.route('/hello', methods=['GET'])
def handle_hello():
    response_body = {
        "message": "Hello! This is the backend."
    }
    return jsonify(response_body), 200
