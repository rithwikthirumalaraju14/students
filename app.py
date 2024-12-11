from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "1234"
CORS(app)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2024'
app.config['MYSQL_DB'] = 'student_management'

mysql = MySQL(app)

@app.route('/get/all-students', methods=['GET'])
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    ret_list = []

    for i in students:
        temp_dict = {
            'rollNumber': i[0],
            'name': i[1],
            'age': i[2],
            'department': i[3],
            'fee': i[4]
        }
        ret_list.append(temp_dict)
    cur.close()
    return jsonify(ret_list)

@app.route('/create/student', methods=['POST'])
def create():
    if request.method == 'POST':
        data = request.get_json()
        print(data)

        rollnumber = int(data.get('rollNumber', 0))
        if rollnumber <= 0:
            return jsonify({'message': 'Roll number 0 or negative values are not permitted'}), 409

        name = data.get('name')
        age = data.get('age')
        department = data.get('department')
        fee = data.get('fee')

        cur = mysql.connection.cursor()

        # Check if roll number already exists
        cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (rollnumber,))
        result = cur.fetchone()
        if result[0] > 0:
            cur.close()
            return jsonify({'message': f'Roll number {rollnumber} already exists'}), 409

        # Insert new student if roll number is unique
        cur.execute("INSERT INTO students (id, name, age, department, fee) VALUES (%s, %s, %s, %s, %s)",
                    (rollnumber, name, age, department, fee))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Student added successfully!'}), 201
    else:
        return jsonify({'message': 'Request must be JSON'}), 409

@app.route('/update/student', methods=['PUT'])
def update():
    if request.method == 'PUT':
        data = request.get_json()
        print(data)

        rollnumber = int(data.get('rollNumber', 0))
        if rollnumber <= 0:
            return jsonify({'message': 'Roll number 0 or negative values are not permitted'}), 409

        name = data.get('name')
        age = data.get('age')
        department = data.get('department')
        fee = data.get('fee')

        cur = mysql.connection.cursor()

        # Check if the student exists
        cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (rollnumber,))
        result = cur.fetchone()
        if result[0] == 0:
            cur.close()
            return jsonify({'message': f'Student with roll number {rollnumber} does not exist'}), 404

        # Update student details
        cur.execute("UPDATE students SET name = %s, age = %s, department = %s, fee = %s WHERE id = %s",
                    (name, age, department, fee, rollnumber))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Student updated successfully!'}), 200
    else:
        return jsonify({'message': 'Request must be JSON'}), 409



@app.route('/delete/student', methods=['DELETE'])
def delete():
    rollnumber = request.args.get('rollNumber', default=0, type=int)
    if rollnumber <= 0:
        return jsonify({'message': 'Invalid roll number provided'}), 400

    cur = mysql.connection.cursor()

    # Check if the student exists
    cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (rollnumber,))
    result = cur.fetchone()
    if result[0] == 0:
        cur.close()
        return jsonify({'message': f'Student with roll number {rollnumber} does not exist'}), 404

    # Delete the student
    cur.execute("DELETE FROM students WHERE id = %s", (rollnumber,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Student deleted successfully!'}), 200




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
