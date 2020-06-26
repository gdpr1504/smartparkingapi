from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required


class OutpassApplication(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('orollno', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('odate', type = str, required = True, help = 'date cannot be left blank')
        parser.add_argument('otime', type = str, required = True, help = 'time cannot be left blank')
        parser.add_argument('odesc', type = str, required = True, help = 'description cannot be left blank')

        data = parser.parse_args()
    
        try:
            isAlreadyPresent = query(f"""SELECT * FROM PASSES WHERE orollno = '{data['orollno']}' AND odate = '{data['odate']}'""", return_json = False)
            if len(isAlreadyPresent) > 0:
                return {"message":"Student has already applied for an outpass on the given date"},400
        except:
            return {"message":"Error in outpass application"},500

        try:
            query(f"""INSERT INTO PASSES (orollno, odate, otime, odesc) VALUES (
                                                            '{data['orollno']}',
                                                            '{data['odate']}',
                                                            '{data['otime']}',
                                                            '{data['odesc']}'
                                                            )"""
                                                            )
        except:
            return {"message":"Error in outpass application"},500
        
        return {"message":"Outpass application successfull"},201

class PendingOutpasses(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('adept', type = str, required = True, help = 'dept cannot be left blank')

        data = parser.parse_args()

        try:
            return query(f"""SELECT oid, srollno, sname, syear FROM STUDENTS INNER JOIN PASSES ON srollno = orollno WHERE ostatus = 'pending' AND sdept = '{data['adept']}'""", return_json=False),200
        except:
            return {"message":"Error in retrieving pending outpasses"},500

class SetOutpassStatus(Resource):
    @jwt_required
    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('oid', type = int, required = True, help = 'oid cannot be left blank')
            parser.add_argument('ostatus', type = str, required = True, help = 'status cannot be left blank')

            data = parser.parse_args()
        except:
            return {"message":"error in parsing data"},400

        try:
            query(f"""UPDATE PASSES SET ostatus = '{data['ostatus']}' WHERE oid = '{data['oid']}'""")
        except:
            return {"message":"Error in setting outpass status"},500
        return {"message":"Outpass status set successfully"},200