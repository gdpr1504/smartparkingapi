from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from flask_bcrypt import Bcrypt

class StudentRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('spassword', type = str, required = True, help = 'password cannot be left blank')
        parser.add_argument('sname', type = str, required = True, help = 'name cannot be left blank')
        parser.add_argument('sdept', type = str, required = True, help = 'dept cannot be left blank')
        parser.add_argument('syear', type = str, required = True, help = 'year cannot be left blank')
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
            query(f"""INSERT INTO STUDENTS (srollno, spassword, sname, sdept, syear, semail, sphone, spgname, spgphone) VALUES (
                                                                                                                                '{data['srollno']}',
                                                                                                                                '{spassword_hash}',
                                                                                                                                '{data['sname']}',
                                                                                                                                '{data['sdept']}',
                                                                                                                                '{data['syear']}',
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
    def __init__(self, srollno, spassword, sname, sdept, syear, semail, sphone, spgname, spgphone):
        self.srollno = srollno
        self.spassword = spassword
        self.sname = sname
        self.sdept = sdept
        self.syear = syear
        self.semail = semail
        self.sphone = sphone
        self.spgname = spgname
        self.spgphone = spgphone

    @classmethod
    def getStudentUserBySrollno(cls, srollno):
        result = query(f"""SELECT * FROM STUDENTS WHERE srollno = '{srollno}'""",return_json=False)
        if len(result)>0: return StudentUser(result[0]['srollno'], result[0]['spassword'], result[0]['sname'], result[0]['sdept'], result[0]['syear'], result[0]['semail'], result[0]['sphone'], result[0]['spgname'], result[0]['spgphone'])
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
                return {    "srollno":studentuser.srollno,
                            "sname":studentuser.sname,
                            "sdept":studentuser.sdept,
                            "syear":studentuser.syear,
                            "access_token":access_token
                        },200
            return {"message":"Invalid credentials!"},401
        except:
            return {"message":"Error while logging in"},500


class EditStudentdetails(Resource):
    @jwt_required
    def post(self):

        try:
            parser = reqparse.RequestParser()

            parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')
            parser.add_argument('soldpassword', type = str, required = True, help = 'old password cannot be left blank')
            parser.add_argument('snewpassword', type = str)
            parser.add_argument('sname', type = str)
            parser.add_argument('sdept', type = str)
            parser.add_argument('syear', type = str)
            parser.add_argument('semail', type = str)
            parser.add_argument('sphone', type = str)
            parser.add_argument('spgname', type = str)
            parser.add_argument('spgphone', type = str)

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            bcrypt = Bcrypt()
            studentuser = StudentUser.getStudentUserBySrollno(data['srollno'])
            if not(studentuser and bcrypt.check_password_hash(studentuser.spassword, data['soldpassword'])):
                return {"message":"Wrong password"}
        except:
            return {"message":"Error in editing details"},500


        try:
            if data['sname'] == None:
                data['sname'] = studentuser.sname
            if data['sdept'] == None:
                data['sdept'] = studentuser.sdept
            if data['syear'] == None:
                data['syear'] = studentuser.syear
            if data['semail'] == None:
                data['semail'] = studentuser.semail
            if data['sphone'] == None:
                data['sphone'] = studentuser.sphone
            if data['spgname'] == None:
                data['spgname'] = studentuser.spgname
            if data['spgphone'] == None:
                data['spgphone'] = studentuser.spgphone
            if data['snewpassword'] == None:
                try:
                    x=query(f"""SELECT * FROM STUDENTS WHERE srollno = '{data["srollno"]}'""",return_json=False)
                    if len(x)>0:
                        query(f"""UPDATE STUDENTS SET
                                                        sname='{data['sname']}',
                                                        sdept='{data['sdept']}',
                                                        syear='{data['syear']}',
                                                        semail='{data['semail']}',
                                                        sphone='{data['sphone']}',
                                                        spgname='{data['spgname']}',
                                                        spgphone='{data['spgphone']}'
                                WHERE srollno = '{data['srollno']}'""")
                        return {"message" : "Details are edited successfully!"},200
                    return {"message" : "Srollno doesn't exist"},400
                except:
                    return{"message" : "Error in editing details1"},500
            else:
                spassword_hash = bcrypt.generate_password_hash(data['snewpassword']).decode('utf-8')
            

            x=query(f"""SELECT * FROM STUDENTS WHERE srollno = '{data["srollno"]}'""",return_json=False)
            if len(x)>0:
                query(f"""UPDATE STUDENTS SET
                                                spassword='{spassword_hash}',
                                                sname='{data['sname']}',
                                                sdept='{data['sdept']}',
                                                syear='{data['syear']}',
                                                semail='{data['semail']}',
                                                sphone='{data['sphone']}',
                                                spgname='{data['spgname']}',
                                                spgphone='{data['spgphone']}'
                        WHERE srollno = '{data['srollno']}'""")
                return {"message" : "Details are edited successfully!"},200
            return {"message" : "Srollno doesn't exist"},400

        except:
            return {"message":"Error in editing details"},500

class Outpassstatus(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('oid', type = int, required = True, help = 'oid cannot be left blank')

        data = parser.parse_args()

        try:
            return query(f"""SELECT ostatus FROM PASSES WHERE oid = '{data['oid']}'""", return_json=False),200
        except:
            return {"message":"oid doesn't exist"},500

class GetStudentHistory(Resource):
    @jwt_required
    def get(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            return query(f"""SELECT odate, odesc, ostatus FROM PASSES WHERE orollno = '{data["srollno"]}'""")
        except:
            return {"message":"Error while fetching data"},500