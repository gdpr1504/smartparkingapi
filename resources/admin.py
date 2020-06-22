from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from flask_bcrypt import Bcrypt

class AdminRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('ausername', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('apassword', type = str, required = True, help = 'password cannot be left blank')
        parser.add_argument('aname', type = str, required = True, help = 'name cannot be left blank')
        parser.add_argument('adept', type = str, required = False)
        parser.add_argument('aemail', type = str, required = True, help = 'year cannot be left blank')
        parser.add_argument('aphone', type = str, required = True, help = 'email cannot be left blank')

        data = parser.parse_args()

        try:
            isUsernameAlreadyPresent = query(f"""SELECT * FROM ADMINS WHERE ausername = '{data['ausername']}'""", return_json = False)
            if len(isUsernameAlreadyPresent) > 0:
                return {"message":"Admin with given username already exists"},400
        except:
            return {"message":"Error inserting into ADMINS"},500

        try:
            isDeptAlreadyPresent = query(f"""SELECT * FROM ADMINS WHERE adept = '{data['adept']}'""", return_json = False)
            if len(isDeptAlreadyPresent) > 0:
                return {"message":"Admin of given dept already exists"},400
        except:
            return {"message":"Error inserting into ADMINS"},500

        try:
            bcrypt = Bcrypt()
            apassword_hash = bcrypt.generate_password_hash(data['apassword']).decode('utf-8')
        except:
            return {"message":"Password hash not generated"},500

        if data['adept']!=None:
            try:
                query(f"""INSERT INTO ADMINS VALUES (
                                                                '{data['ausername']}',
                                                                '{apassword_hash}',
                                                                '{data['aname']}',
                                                                '{data['adept']}',
                                                                '{data['aemail']}',
                                                                '{data['aphone']}'
                                                                )"""
                                                                )
            except:
                return {"message":"Error inserting into ADMINS"},500
        else:
            try:
                query(f"""INSERT INTO ADMINS (ausername, apassword, aname, aemail, aphone) VALUES (
                                                                '{data['ausername']}',
                                                                '{data['apassword']}',
                                                                '{data['aname']}',
                                                                '{data['aemail']}',
                                                                '{data['aphone']}'
                                                                )"""
                                                                )
            except:
                return {"message":"Error inserting into ADMINS"},500
        
        return {"message":"Admin successfully registered"},201

class AdminUser():
    def __init__(self, ausername, apassword, aname, adept):
        self.ausername = ausername
        self.apassword = apassword
        self.aname = aname
        self.adept = adept

    @classmethod
    def getAdminUserByAusername(cls, ausername):
        result = query(f"""SELECT ausername, apassword, aname, adept FROM ADMINS WHERE ausername = '{ausername}'""",return_json=False)
        if len(result)>0: return AdminUser(result[0]['ausername'], result[0]['apassword'], result[0]['aname'], result[0]['adept'])
        return None


class AdminLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ausername', type = str, required = True, help = 'username cannot be left blank')
        parser.add_argument('apassword', type = str, required = True, help = 'password cannot be left blank')
        data = parser.parse_args()
        bcrypt = Bcrypt()
            
        try:
            adminuser = AdminUser.getAdminUserByAusername(data['ausername'])
            if adminuser and bcrypt.check_password_hash(adminuser.apassword, data['apassword']) :
                access_token = create_access_token(identity=adminuser.ausername, expires_delta = False)
                return {    "ausername":adminuser.ausername,
                            "aname":adminuser.aname,
                            "adept":adminuser.adept,
                            "access_token":access_token},200
            return {"message":"Invalid credentials!"},401
        except:
            return {"message":"Error while logging in"},500