from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import safe_str_cmp
from flask_bcrypt import Bcrypt

class StudentRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('spassword', type = str, required = True, help = 'password cannot be left blank')
        parser.add_argument('sname', type = str, required = True, help = 'name cannot be left blank')
        parser.add_argument('sdept', type = str, required = True, help = 'dept cannot be left blank')
        parser.add_argument('syear', type = int, required = True, help = 'year cannot be left blank')
        parser.add_argument('semail', type = str, required = True, help = 'email cannot be left blank')
        parser.add_argument('sphone', type = str, required = True, help = 'phone no cannot be left blank')
        parser.add_argument('spgname', type = str, required = True, help = 'Parent/Guardian name cannot be left blank')
        parser.add_argument('spgphone', type = str, required = True, help = 'Parent/Guardian email cannot be left blank')

        data = parser.parse_args()

        try:
            isAlreadyPresent = query(f"""SELECT * FROM STUDENTS WHERE srollno = '{data['srollno']}'""", return_json = False)
            if len(isAlreadyPresent) > 0:
                return {"message":"Student with given roll no already exists"},400
        except:
            return {"message":"Error inserting into STUDENTS"},500

        try:
            bcrypt = Bcrypt()
            spassword_hash = bcrypt.generate_password_hash(data['spassword']).decode('utf-8')
        except:
            return {"message":"Password hash not generated"},500

        try:
            query(f"""INSERT INTO STUDENTS VALUES (
                                                            '{data['srollno']}',
                                                            '{spassword_hash}',
                                                            '{data['sname']}',
                                                            '{data['sdept']}',
                                                            {data['syear']},
                                                            '{data['semail']}',
                                                            '{data['sphone']}',
                                                            '{data['spgname']}',
                                                            '{data['spgphone']}'
                                                            )"""
                                                            )
        except:
            return {"message":"Error inserting into STUDENTS"},500
        
        return {"message":"Student successfully registered"},201

class StudentUser():
    def __init__(self, srollno, spassword, sname, sdept, syear):
        self.srollno = srollno
        self.spassword = spassword
        self.sname = sname
        self.sdept = sdept
        self.syear = syear

    @classmethod
    def getStudentUserBySrollno(cls, srollno):
        result = query(f"""SELECT srollno, spassword, sname, sdept, syear FROM STUDENTS WHERE srollno = '{srollno}'""",return_json=False)
        if len(result)>0: return StudentUser(result[0]['srollno'], result[0]['spassword'], result[0]['sname'], result[0]['sdept'], result[0]['syear'])
        return None


class StudentLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('spassword', type = str, required = True, help = 'password cannot be left blank')
        data = parser.parse_args()
        bcrypt = Bcrypt()
            
        try:
            studentuser = StudentUser.getStudentUserBySrollno(data['srollno'])
            if studentuser and bcrypt.check_password_hash(studentuser.spassword, data['spassword']) :
                access_token = create_access_token(identity=studentuser.srollno, expires_delta = False)
                return {    "sname":studentuser.sname,
                            "sdept":studentuser.sdept,
                            "syear":studentuser.syear,
                            "access_token":access_token
                        },200
            return {"message":"Invalid credentials!"},401
        except:
            return {"message":"Error while logging in"},500