from flask import jsonify
from decimal import Decimal
from datetime import date, time, datetime
import pymysql

def query(querystr, return_json=True):
    connection = pymysql.connect(   host = 'new-restore.cunlgid42qzy.ap-south-1.rds.amazonaws.com',
                                    user = 'admin',
                                    password = 'password',
                                    db = 'smart',
                                    cursorclass = pymysql.cursors.DictCursor)
    connection.begin()
    cursor = connection.cursor()
    cursor.execute(querystr)
    result = encode(cursor.fetchall())
    connection.commit()
    cursor.close()
    connection.close()
    if return_json:
        return jsonify(result)
    else:
        return result

def encode(data):
    for row in data:
        for key, value in row.items():
            if isinstance(value, (Decimal, datetime, date, time)):
                row[key] = str(value)
    return data
