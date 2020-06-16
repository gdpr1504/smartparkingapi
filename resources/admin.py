from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import safe_str_cmp
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
            isAlreadyPresent = query(f"""SELECT * FROM ADMINS WHERE ausername = '{data['ausername']}'""", return_json = False)
            if len(isAlreadyPresent) > 0:
                return {"message":"Admin with given username already exists"},400
        except:
            return {"message":"Error inserting into ADMINS1"},500

        try:
            bcrypt = Bcrypt()
            apassword_hash = bcrypt.generate_password_hash(data['apassword'])
            print(apassword_hash)
        except:
            return {"message":"Password hash not generated"},500

        if data['adept']!=None:
            try:
                query(f"""INSERT INTO ADMINS VALUES (
                                                                '{data['ausername']}',
                                                                "{apassword_hash}",
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