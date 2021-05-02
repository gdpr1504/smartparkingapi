from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from resources.student import StudentUser

class AdminRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('fullname', type = str, required = True, help = 'username cannot be left blank')
        parser.add_argument('email', type = str, required = True, help = 'year cannot be left blank')
        parser.add_argument('pass', type = str, required = True, help = 'password cannot be left blank')

        data = parser.parse_args()

        try:
            isUsernameAlreadyPresent = query(f"""SELECT * FROM users WHERE email = '{data['email']}'""", return_json = False)
            if len(isUsernameAlreadyPresent) > 0:
                return {"message":"User with given email already exists"},400
        except:
            return {"message":"Error inserting into USERS"},500

        try:
            bcrypt = Bcrypt()
            apassword_hash = bcrypt.generate_password_hash(data['pass']).decode('utf-8')
        except:
            return {"message":"Password hash not generated"},500

        try:
            query(f"""INSERT INTO users(fullname,email,password) VALUES ('{data['fullname']}',
                                               '{data['email']}',
                                               '{data['pass']}'
                                                            )"""
                                                            )
        except:
            return {"message":"Error inserting into User"},500
        
        return {"message":"User successfully registered"},201

class AdminUser():
    def __init__(self, fullname,email,password,uid):
        self.fullname = fullname
        self.password = password
        self.email = email
        self.uid=uid

    @classmethod
    def getAdminUserByAusername(cls, email):
        result = query(f"""SELECT * FROM users WHERE email = '{email}'""",return_json=False)
        if len(result)>0: return AdminUser(result[0]['fullname'], result[0]['email'],result[0]['password'],result[0]['uid'])
        return None


class AdminLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type = str, required = True, help = 'username cannot be left blank')
        parser.add_argument('pass', type = str, required = True, help = 'password cannot be left blank')
        data = parser.parse_args()
        bcrypt = Bcrypt()
            
        try:
            adminuser = AdminUser.getAdminUserByAusername(data['email'])
            if adminuser and (adminuser.password==data['pass']) :
                access_token = create_access_token(identity=adminuser.email, expires_delta = False)
                return {    "email":adminuser.email,
                            "fullname":adminuser.fullname,
                            "access_token":access_token,
                            "uid":adminuser.uid},200
            return {"message":"Invalid credentials!"},401
        except:
            return {"message":"Error while logging in"},500

class EditAdmindetails(Resource):
    @jwt_required
    def post(self):

        try:
            parser = reqparse.RequestParser()

            parser.add_argument('ausername', type = str, required = True, help = 'username cannot be left blank')
            parser.add_argument('aoldpassword', type = str, required = True, help = 'old password cannot be left blank')
            parser.add_argument('anewpassword', type = str)
            parser.add_argument('aname', type = str)
            parser.add_argument('adept', type = str)
            parser.add_argument('aemail', type = str)
            parser.add_argument('aphone', type = str)

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            bcrypt = Bcrypt()
            adminuser = AdminUser.getAdminUserByAusername(data['ausername'])
            if not(adminuser and bcrypt.check_password_hash(adminuser.apassword, data['aoldpassword'])):
                return {"message":"Wrong password"}
        except:
            return {"message":"Error in editing details"},500


        try:
            if data['aname'] == None:
                data['aname'] = adminuser.aname
            if data['adept'] == None:
                data['adept'] = adminuser.adept
            if data['aemail'] == None:
                data['aemail'] = adminuser.aemail
            if data['aphone'] == None:
                data['aphone'] = adminuser.aphone
            if data['anewpassword'] == None:
                x=query(f"""SELECT * FROM ADMINS WHERE ausername = '{data["ausername"]}'""",return_json=False)
                if len(x)>0:
                    query(f"""UPDATE ADMINS SET
                                                    aname='{data['aname']}',
                                                    adept='{data['adept']}',
                                                    aemail='{data['aemail']}',
                                                    aphone='{data['aphone']}'
                            WHERE ausername = '{data['ausername']}'""")
                    return {"message" : "Details are edited successfully!"},200
                return {"message" : "Srollno doesn't exist"},400
            else:
                apassword_hash = bcrypt.generate_password_hash(data['anewpassword']).decode('utf-8')


            x=query(f"""SELECT * FROM ADMINS WHERE ausername = '{data["ausername"]}'""",return_json=False)
            if len(x)>0:
                query(f"""UPDATE ADMINS SET
                                                apassword='{apassword_hash}',
                                                aname='{data['aname']}',
                                                adept='{data['adept']}',
                                                aemail='{data['aemail']}',
                                                aphone='{data['aphone']}'
                        WHERE ausername = '{data['ausername']}'""")
                return {"message" : "Details are edited successfully!"},200
            return {"message" : "Srollno doesn't exist"},400
            
        except:
            return {"message":"Error in editing details"},500


class GetDistricts(Resource):
    def get(self):
        try:
            return query(f"""SELECT * FROM districts""",return_json=False)
        except:
            return {"message":"Error in fetching data"},500

class Getzones(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('did', type = int, required = True, help = 'did cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            return query(f"""SELECT * FROM postal_zones WHERE did = '{data['did']}'""",return_json=False)
        except:
            return {"message":"Error while fetching data"},500


class Studentdetails(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('srollno', type = str, required = True, help = 'srollno cannot be left blank')

        data = parser.parse_args()

        try:
            return query(f"""SELECT sname, sdept, syear, semail, sphone, spgname, spgphone FROM STUDENTS WHERE srollno = '{data['srollno']}'""", return_json=False),200
        except:
            return {"message":"srollno doesn't exist"},500

class SetOutpassesleft(Resource):
    @jwt_required
    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('srollno', type = str, required = True, help = 'srollno cannot be left blank')
            parser.add_argument('value', type = int, required = True, help = 'value cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            query(f"""UPDATE STUDENTS SET passesleft = '{data['value']}' WHERE srollno = '{data['srollno']}'""")
        except:
            return {"message":"Error in setting passesleft"},500
        return {"message":"Passesleft set successfully"},200