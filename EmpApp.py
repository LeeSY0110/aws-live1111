from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'company'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('CompanyRegister.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')


@app.route("/addcmp", methods=['POST'])
def AddCom():

    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']
    address = request.form['address']
    typeOfBusiness = request.form['typeOfBusiness']
    numOfEmployee = request.form['numOfEmployee']
    overview = request.form['overview']
    relevantDocument = request.files['relevantDocument']

    insert_sql = "INSERT INTO company VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if relevantDocument.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (name, email, contact, address, typeOfBusiness, numOfEmployee, overview))
        db_conn.commit()
        # Uplaod image file in S3 #
        relevantDocument = "emp-id-" + str(name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=relevantDocument_in_s3, Body=relevantDocument)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                relevantDocument_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('CompanyRegister.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

