from flask import Flask, request, jsonify, session
from db import Ad, Session as DB_Session, User
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

@app.route('/ads', methods=['POST'])
def create_ad():

    if 'user_id' not in session:
        return jsonify({"error": "unauthorized"}), 401

    if not request.json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.json
    title = data.get('title')
    if title is None:
        return jsonify({"error": "title is required"}), 400

    description = data.get('description')
    
    ad = Ad(title=title, description=description, user_id=session['user_id'])
    
    try:
        with DB_Session() as db_session:
            db_session.add(ad)
            db_session.commit()
            db_session.refresh(ad)
            return jsonify(ad.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ads', methods=['GET'])
def get_ads():
    with DB_Session() as db_session:
        ads = db_session.query(Ad).all()
        return jsonify([ad.to_dict() for ad in ads]), 200


@app.route('/ads/<int:id>', methods=['GET'])
def get_ad(id):
    with DB_Session() as db_session:
        ad = db_session.get(Ad, id)
        if ad is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(ad.to_dict()), 200


@app.route('/ads/<int:id>', methods=['DELETE'])
def delete_ad(id):

    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    with DB_Session() as db_session:
        ad = db_session.get(Ad, id)
        if ad is None:
            return jsonify({"error": "not found"}), 404
            
        if ad.user_id != session['user_id']:
            return jsonify({"error": "Forbidden"}), 403

        db_session.delete(ad)
        db_session.commit()
        return jsonify({"message": "ad deleted"}), 200


@app.route('/register', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.json
    
    if 'name' not in data:
        return jsonify({"error": "name is required"}), 400
    if 'email' not in data:
        return jsonify({"error": "email is required"}), 400
    if 'password' not in data:
        return jsonify({"error": "password is required"}), 400
    
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])
    
    user = User(name=name, email=email, password_hash=password)
    
    try:
        with DB_Session() as db_session:
            existing_user = db_session.query(User).filter(User.email == email).first()
            if existing_user:
                return jsonify({"error": "user already exists"}), 400
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            return jsonify(user.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.json
    if 'email' not in data:
        return jsonify({"error": "email is required"}), 400
    if 'password' not in data:
        return jsonify({"error": "password is required"}), 400
    
    email = data['email']
    password = data['password']

    try:
        with DB_Session() as db_session:
            user = db_session.query(User).filter(User.email == email).first()
            if user is None:
                return jsonify({"error": "user not found"}), 400
            if not check_password_hash(user.password_hash, password):
                return jsonify({"error": "invalid password"}), 401
            session['user_id'] = user.id
            return jsonify({"message": "login successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def main():
    return "Server is running"

if __name__ == '__main__':
    app.run(debug=True)
