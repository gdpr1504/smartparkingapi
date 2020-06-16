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
            spassword_hash = bcrypt.generate_password_hash(data['spassword'])
            print(spassword_hash)
        except:
            return {"message":"Password hash not generated"},500

        try:
            query(f"""INSERT INTO STUDENTS VALUES (
                                                            '{data['srollno']}',
                                                            "{spassword_hash}",
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