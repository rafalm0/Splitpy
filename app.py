from flask import Flask, jsonify
from flask_jwt_extended import JWTManager,create_access_token,get_jwt,get_jwt_identity,jwt_required,set_access_cookies,unset_jwt_cookies
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_migrate import Migrate
from flask_smorest import Api
from dotenv import load_dotenv
import os
if os.path.exists("env_config.py"):
    import env_config
from blocklist import BLOCKLIST
from db import db
from flask_cors import CORS  # Import CORS


from resources.transaction import blp as TransactionBlueprint
from resources.group import blp as GroupBlueprint
from resources.member import blp as MemberBlueprint
from resources.user import blp as UserBlueprint
from resources.balance import blp as BalanceBlueprint


# models need to be already imported before sqlchemy


def create_app(db_url=None):
    app = Flask(__name__)
    cors = CORS(app, supports_credentials=True)  # allow CORS for all domains on all routes.
    app.config['CORS_HEADERS'] = 'Content-Type'

    load_dotenv(".env")
    # --------------------------------- app config ---------------------

    app.config['USING_REDIS_QUEUE'] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "SplitPy"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    if os.path.exists("env_config.py"):
        app.config['SQLALCHEMY_DATABASE_URI'] = env_config.DATABASE_URL
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config['SQLALCHEMY_TACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_KEY", '261696634396203470738536034261566624783')

    print(f"Deployment database on {app.config['SQLALCHEMY_DATABASE_URI']},")
    # ------------------------- populating db with tables ------------------------
    db.init_app(app)
    with app.app_context():  # creating all tables initially
        db.create_all()

    # --------------------------------- flask migrate ---------------------

    migrate = Migrate(app, db)

    # ---------------------------- app initialization -------------------
    api = Api(app)

    # ---------------------------- jwt config and methods-----------------------------------
    jwt = JWTManager(app)

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    @jwt.token_in_blocklist_loader
    def check_if_token_in_clocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        else:
            return {"is_admin": True}  # admin not required for deletion

    @jwt.revoked_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token revoked, user loged out", "error": "token_revoked"}), 401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token expired", "error": "token_expired"}), 401)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token is not fresh", "error": "fresh_token_required"}), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"message": "Signature failed", "error": "invalid_token"}), 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"message": "No signature in request", "error": "authorization_required"}), 401)

    # -------------------------- blueprint registers --------------------------

    api.register_blueprint(TransactionBlueprint)
    api.register_blueprint(GroupBlueprint)
    api.register_blueprint(MemberBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BalanceBlueprint)

    return app
