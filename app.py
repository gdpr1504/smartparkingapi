from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.student import StudentRegister, StudentLogin, EditStudentdetails, Outpassstatus, GetStudentHistory
from resources.admin import AdminRegister, AdminLogin, EditAdmindetails, GetPendingNoOfPasses, GetPassesHistory, Studentdetails, SetOutpassesleft
from resources.outpass import OutpassApplication, PendingOutpasses, SetOutpassStatus, Outpasssdetails

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True
app.config['JWT_SECRET_KEY']='password'
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
api.add_resource(AdminRegister, '/userregister')
api.add_resource(StudentLogin, '/studentlogin')
api.add_resource(AdminLogin, '/userlogin')
api.add_resource(OutpassApplication, '/outpassapplication')
api.add_resource(PendingOutpasses, '/outpassrequests')
api.add_resource(EditStudentdetails, '/editstudentdetails')
api.add_resource(EditAdmindetails, '/editadmindetails')
api.add_resource(GetDistricts, '/getdistricts')
api.add_resource(GetPassesHistory, '/getpasseshistory')
api.add_resource(SetOutpassStatus, '/setoutpassstatus')
api.add_resource(Studentdetails, '/studentdetails')
api.add_resource(Outpassstatus, '/outpassstatus')
api.add_resource(Outpasssdetails, '/outpassdetails')
api.add_resource(GetStudentHistory, '/getstudenthistory')
api.add_resource(SetOutpassesleft, '/setoutpassesleft')

if __name__ == '__main__':
    app.run()