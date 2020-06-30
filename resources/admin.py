from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from resources.student import StudentUser

class AdminRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('ausername', type = str, required = True, help = 'username cannot be left blank')
        parser.add_argument('apassword', type = str, required = True, help = 'password cannot be left blank')
        parser.add_argument('aname', type = str, required = True, help = 'name cannot be left blank')
        parser.add_argument('adept', type = str, required = True, help = 'dept cannot be let blank')
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
        
        return {"message":"Admin successfully registered"},201

class AdminUser():
    def __init__(self, ausername, apassword, aname, adept, aemail, aphone):
        self.ausername = ausername
        self.apassword = apassword
        self.aname = aname
        self.adept = adept
        self.aemail = aemail
        self.aphone = aphone

    @classmethod
    def getAdminUserByAusername(cls, ausername):
        result = query(f"""SELECT * FROM ADMINS WHERE ausername = '{ausername}'""",return_json=False)
        if len(result)>0: return AdminUser(result[0]['ausername'], result[0]['apassword'], result[0]['aname'], result[0]['adept'], result[0]['aemail'], result[0]['aphone'])
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


class GetPendingNoOfPasses(Resource):
    @jwt_required
    def get(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            return query(f"""SELECT passesleft FROM STUDENTS WHERE srollno = '{data["srollno"]}'""")
        except:
            return {"message":"Error in fetching data"},500

class GetPassesHistory(Resource):
    @jwt_required
    def get(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            return query(f"""SELECT ostatus, odate FROM PASSES WHERE orollno = '{data["srollno"]}'""")
        except:
            return {"message":"Error while fetching dates"},500


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