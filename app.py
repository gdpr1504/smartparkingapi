from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.student import StudentRegister, StudentLogin
from resources.admin import AdminRegister, AdminLogin

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True
app.config['JWT_SECRET_KEY']='coscskillup'
api = Api(app)
jwt = JWTManager(app)

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error':'authorization required',
        "description":"Request does not contain an access token"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error':'invalid token',
        "description":"Signature verification failed"
    }), 401

api.add_resource(StudentRegister, '/studentregister')
api.add_resource(AdminRegister, '/adminregister')
api.add_resource(StudentLogin, '/studentlogin')
api.add_resource(AdminLogin, '/adminlogin')

if __name__ == '__main__':
    app.run()