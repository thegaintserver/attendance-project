from flask import Flask, request, render_template, redirect, jsonify
from pymongo import MongoClient
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB connection
client = MongoClient("mongodb://mongo:27017/")
db = client.attendance_db
attendance_collection = db.attendance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        in_date = request.form['in_date']
        in_time = request.form['in_time']
        out_date = request.form['out_date']
        out_time = request.form['out_time']

        # Log the received data
        app.logger.debug(f'Received data: {student_id}, {student_name}, {in_date} {in_time}, {out_date} {out_time}')

        # Combine date and time, and parse the datetime strings into datetime objects
        try:
            in_time_dt = datetime.strptime(f"{in_date} {in_time}", '%Y-%m-%d %H:%M')
            out_time_dt = datetime.strptime(f"{out_date} {out_time}", '%Y-%m-%d %H:%M')
        except ValueError as e:
            app.logger.error(f'Time parsing error: {e}')
            return jsonify({"message": f"Invalid time format: {e}"}), 400

        attendance_record = {
            'student_id': student_id,
            'student_name': student_name,
            'in_time': in_time_dt,
            'out_time': out_time_dt
        }

        # Insert record into MongoDB
        try:
            attendance_collection.insert_one(attendance_record)
        except Exception as e:
            app.logger.error(f'Error inserting record into MongoDB: {e}')
            return jsonify({"message": f"Database error: {e}"}), 500

        app.logger.debug('Data inserted successfully')
        return jsonify({"message": "Attendance form submitted successfully!"}), 200

    except Exception as e:
        app.logger.error(f'Unexpected error: {e}')
        return jsonify({"message": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

