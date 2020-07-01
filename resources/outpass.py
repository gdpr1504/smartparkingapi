from flask_restful import Resource, reqparse
from db import query
from flask_jwt_extended import create_access_token, jwt_required


class OutpassApplication(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('srollno', type = str, required = True, help = 'roll no cannot be left blank')
        parser.add_argument('odate', type = str, required = True, help = 'date cannot be left blank')
        parser.add_argument('otime', type = str, required = True, help = 'time cannot be left blank')
        parser.add_argument('odesc', type = str, required = True, help = 'description cannot be left blank')

        data = parser.parse_args()
    
        try:
            isapplicable = query(f"""SELECT passesleft FROM STUDENTS WHERE srollno = '{data['srollno']}' AND passesleft > 0""", return_json=False)
            if len(isapplicable)<1:
                return {"message":"Maximum no of outpasses applied"},400

            isAlreadyPresent = query(f"""SELECT * FROM PASSES WHERE orollno = '{data['srollno']}' AND odate = '{data['odate']}' AND ostatus not in ('rejected','come to cabin')""", return_json = False)
            if len(isAlreadyPresent) > 0:
                return {"message":"Student has already applied for an outpass on the given date"},400
        except:
            return {"message":"Error in outpass application"},500

        try:
            query(f"""INSERT INTO PASSES (orollno, odate, otime, odesc) VALUES (
                                                            '{data['srollno']}',
                                                            '{data['odate']}',
                                                            '{data['otime']}',
                                                            '{data['odesc']}'
                                                            )"""
                                                            )
        except:
            return {"message":"Error in outpass application"},500

        try:
            result = query(f"""SELECT oid FROM PASSES order by oid desc limit 1""", return_json=False)
            if len(result)>0:
                oid = result[0]['oid']
        except:
            return {"message":"Error in getting oid"},500
        
        return {"message":"Outpass application successfull",
                "oid":oid},201

class PendingOutpasses(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('adept', type = str, required = True, help = 'dept cannot be left blank')

        data = parser.parse_args()

        try:
            query(f"""UPDATE PASSES SET ostatus = 'rejected' WHERE odate < CURDATE() AND ostatus = 'pending'""")
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

class Outpasssdetails(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('oid', type = int, required = True, help = 'oid cannot be left blank')

        data = parser.parse_args()

        try:
            return query(f"""SELECT oid, orollno, odate, odesc, ostatus FROM PASSES WHERE oid = '{data['oid']}'""", return_json=False),200
        except:
            return {"message":"oid doesn't exist"},500
