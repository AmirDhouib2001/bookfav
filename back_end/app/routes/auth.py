from flask import Blueprint, jsonify, request, current_app
from app.models import AuthUser, UserSession, db
from datetime import datetime
import re
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        # Validation des données
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({"error": "Tous les champs obligatoires doivent être remplis (username, email, password)"}), 400
        
        # Validation de l'email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return jsonify({"error": "Format d'email invalide"}), 400
        
        # Validation du mot de passe (au moins 8 caractères, avec lettres et chiffres)
        if len(data['password']) < 8 or not (any(c.isalpha() for c in data['password']) and any(c.isdigit() for c in data['password'])):
            return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères, dont des lettres et des chiffres"}), 400
        
        # Création de l'utilisateur
        user = AuthUser(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', ''),
            profile_image_url=data.get('profile_image_url', '')
        )
        user.set_password(data['password'])
        
        # Enregistrement des genres préférés si fournis
        if 'favorite_genres' in data and isinstance(data['favorite_genres'], list):
            user.favorite_genres = data['favorite_genres']
        
        db.session.add(user)
        db.session.commit()
        
        # Création de la session utilisateur
        session_id = user.create_session(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_in_hours=24  # Session de 24h par défaut à l'inscription
        )
        
        return jsonify({
            "message": "Compte créé avec succès",
            "user": user.to_dict(),
            "session_id": session_id
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e)
        if "username" in error_message:
            return jsonify({"error": "Ce nom d'utilisateur est déjà utilisé"}), 409
        elif "email" in error_message:
            return jsonify({"error": "Cette adresse email est déjà utilisée"}), 409
        return jsonify({"error": "Erreur lors de la création du compte"}), 409
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'inscription: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la création du compte"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        # Validation des données
        if not all(k in data for k in ['username', 'password']):
            return jsonify({"error": "Veuillez fournir un nom d'utilisateur et un mot de passe"}), 400
        
        # Recherche de l'utilisateur
        user = AuthUser.query.filter_by(username=data['username']).first()
        
        # Vérification du mot de passe
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401
        
        # Vérification du compte actif
        if not user.is_active:
            return jsonify({"error": "Ce compte a été désactivé"}), 403
        
        # Mise à jour de la date de dernière connexion
        user.last_login = datetime.utcnow()
        
        # Création de la session utilisateur
        session_id = user.create_session(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_in_hours=24  # Session de 24h par défaut
        )
        
        db.session.commit()
        
        return jsonify({
            "message": "Connexion réussie",
            "user": user.to_dict(),
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"Erreur lors de la connexion: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la connexion"}), 500


@auth_bp.route("/validate-session", methods=["POST"])
def validate_session():
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({"error": "ID de session non fourni"}), 400
        
        # Récupération et validation de la session
        session = UserSession.get_by_session_id(data['session_id'])
        
        if not session:
            return jsonify({"valid": False, "error": "Session invalide ou expirée"}), 401
        
        # Récupération de l'utilisateur
        user = AuthUser.query.get(session.user_id)
        
        if not user or not user.is_active:
            return jsonify({"valid": False, "error": "Utilisateur introuvable ou désactivé"}), 401
        
        # Prolonger la session à chaque validation réussie
        session.extend_session(hours=1)
        
        return jsonify({
            "valid": True,
            "user": user.to_dict()
        })
        
    except Exception as e:
        print(f"Erreur lors de la validation de session: {str(e)}")
        return jsonify({"valid": False, "error": "Une erreur est survenue"}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({"error": "ID de session non fourni"}), 400
        
        # Suppression de la session
        session = UserSession.query.filter_by(session_id=data['session_id']).first()
        
        if session:
            db.session.delete(session)
            db.session.commit()
        
        return jsonify({"message": "Déconnexion réussie"})
        
    except Exception as e:
        print(f"Erreur lors de la déconnexion: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la déconnexion"}), 500


@auth_bp.route("/user-profile", methods=["GET"])
def user_profile():
    try:
        # Récupération de l'ID de session depuis les headers
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({"error": "Non authentifié"}), 401
        
        # Validation de la session
        session = UserSession.get_by_session_id(session_id)
        
        if not session:
            return jsonify({"error": "Session invalide ou expirée"}), 401
        
        # Récupération de l'utilisateur
        user = AuthUser.query.get(session.user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
            
        # Prolonger la session à chaque requête authentifiée
        session.extend_session(hours=1)
        
        return jsonify({"user": user.to_dict()})
        
    except Exception as e:
        print(f"Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({"error": "Une erreur est survenue"}), 500


@auth_bp.route("/update-profile", methods=["PUT"])
def update_profile():
    try:
        # Récupération de l'ID de session depuis les headers
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({"error": "Non authentifié"}), 401
        
        # Validation de la session
        session = UserSession.get_by_session_id(session_id)
        
        if not session:
            return jsonify({"error": "Session invalide ou expirée"}), 401
        
        # Récupération de l'utilisateur
        user = AuthUser.query.get(session.user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        # Mise à jour des informations
        data = request.get_json()
        
        if 'full_name' in data:
            user.full_name = data['full_name']
            
        if 'profile_image_url' in data:
            user.profile_image_url = data['profile_image_url']
            
        if 'favorite_genres' in data and isinstance(data['favorite_genres'], list):
            user.favorite_genres = data['favorite_genres']
            
        # Mise à jour du mot de passe si fourni
        if 'current_password' in data and 'new_password' in data:
            if not user.check_password(data['current_password']):
                return jsonify({"error": "Mot de passe actuel incorrect"}), 401
                
            if len(data['new_password']) < 8 or not (any(c.isalpha() for c in data['new_password']) and any(c.isdigit() for c in data['new_password'])):
                return jsonify({"error": "Le nouveau mot de passe doit contenir au moins 8 caractères, dont des lettres et des chiffres"}), 400
                
            user.set_password(data['new_password'])
        
        # Enregistrement des modifications
        db.session.commit()
        
        # Prolonger la session
        session.extend_session(hours=1)
        
        return jsonify({
            "message": "Profil mis à jour avec succès",
            "user": user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour du profil: {str(e)}")
        return jsonify({"error": "Une erreur est survenue lors de la mise à jour du profil"}), 500 