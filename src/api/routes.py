"""
API Routes for Authentication and Protected Resources
"""
import re
import os
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from api.models import db, User
from api.utils import APIException

# Initialize Blueprint
api = Blueprint('api', __name__)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-strong-secret-key-here")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 24))
TOKEN_HEADER = "Authorization"

# -------------------------
# 🛡️ Utility Functions
# -------------------------

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password complexity"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""

def generate_token(user_id):
    """Generate JWT token"""
    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

def token_required(f):
    """JWT authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if TOKEN_HEADER in request.headers:
            token = request.headers[TOKEN_HEADER].split(" ")[1] if "Bearer" in request.headers[TOKEN_HEADER] else None

        if not token:
            return jsonify({"success": False, "msg": "Token is missing"}), 401

        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            
            if not current_user:
                raise APIException("User not found", status_code=404)
                
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "msg": "Token has expired"}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            return jsonify({"success": False, "msg": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# -------------------------
# 🔐 Authentication Routes
# -------------------------

@api.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            raise APIException("No input data provided", status_code=400)

        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        # Validate input
        if not email or not password:
            raise APIException("Email and password are required", status_code=400)
        
        if not validate_email(email):
            raise APIException("Invalid email format", status_code=400)
            
        is_valid_pw, pw_msg = validate_password(password)
        if not is_valid_pw:
            raise APIException(pw_msg, status_code=400)

        # Check if user exists
        if User.query.filter_by(email=email).first():
            raise APIException("User already exists", status_code=409)

        # Create user
        new_user = User(
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate token
        token = generate_token(new_user.id)

        return jsonify({
            "success": True,
            "token": token,
            "user": {"id": new_user.id, "email": new_user.email},
            "msg": "User created successfully"
        }), 201

    except APIException as e:
        return jsonify({"success": False, "msg": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "msg": "Registration failed"}), 500


@api.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            raise APIException("No input data provided", status_code=400)

        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            raise APIException("Email and password are required", status_code=400)

        # Get user
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            raise APIException("Invalid email or password", status_code=401)

        # Generate token
        token = generate_token(user.id)

        return jsonify({
            "success": True,
            "token": token,
            "user": {"id": user.id, "email": user.email},
            "msg": "Login successful"
        }), 200

    except APIException as e:
        return jsonify({"success": False, "msg": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "msg": "Login failed"}), 500


@api.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Token invalidation endpoint (frontend should remove token)"""
    return jsonify({
        "success": True,
        "msg": "Logout successful (please remove token on client side)"
    }), 200


# -------------------------
# 🔒 Protected Routes
# -------------------------

@api.route('/private', methods=['GET'])
@token_required
def private_route(current_user):
    """Example protected route"""
    return jsonify({
        "success": True,
        "msg": f"Welcome {current_user.email}!",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }), 200


@api.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    return jsonify({
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            # Add other user fields as needed
        }
    }), 200


# -------------------------
# 🌐 Public Routes
# -------------------------

@api.route('/status', methods=['GET'])
def status():
    """API status check"""
    return jsonify({
        "success": True,
        "status": "API is running",
        "time": datetime.datetime.utcnow().isoformat()
    }), 200