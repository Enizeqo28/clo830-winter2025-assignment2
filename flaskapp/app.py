from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

# Set default database connection parameters
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))  # Default MySQL port if not set

COLOR_FROM_ENV = os.environ.get('APP_COLOR', "lime")

# Color mapping for UI
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

# Supported colors for validation
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Pick a default color
COLOR = random.choice(list(color_codes.keys()))

# Establish Database Connection with Error Handling
try:
    db_conn = connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )
    print(f"✅ Connected to MySQL Database: {DATABASE} on {DBHOST}:{DBPORT}")
except Exception as e:
    print(f"❌ Database Connection Failed: {e}")
    db_conn = None  # Set to None to avoid using an invalid connection

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes.get(COLOR, "#C1FF9C"))

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', color=color_codes.get(COLOR, "#C1FF9C"))

@app.route("/addemp", methods=['POST'])
def AddEmp():
    if not db_conn:
        return "❌ Database Connection Not Available", 500

    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        emp_name = "Error saving employee details"
    finally:
        cursor.close()

    print("✔ Employee added successfully.")
    return render_template('addempoutput.html', name=emp_name, color=color_codes.get(COLOR, "#C1FF9C"))

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes.get(COLOR, "#C1FF9C"))

@app.route("/fetchdata", methods=['POST'])
def FetchData():
    if not db_conn:
        return "❌ Database Connection Not Available", 500

    emp_id = request.form['emp_id']
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))  # FIX: Tuple should have a comma
        result = cursor.fetchone()

        if result:
            output["emp_id"], output["first_name"], output["last_name"], output["primary_skills"], output["location"] = result
        else:
            return "⚠ No employee found with that ID.", 404

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return "⚠ Error retrieving employee details.", 500
    finally:
        cursor.close()

    return render_template(
        "getempoutput.html",
        id=output["emp_id"],
        fname=output["first_name"],
        lname=output["last_name"],
        interest=output["primary_skills"],
        location=output["location"],
        color=color_codes.get(COLOR, "#C1FF9C")
    )

if __name__ == '__main__':
    # Handle Color Input from Environment or Command Line
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print(f"🎨 Color from command line: {args.color}")
        COLOR = args.color
        if COLOR_FROM_ENV:
            print(f"🌍 Env Color: {COLOR_FROM_ENV}, but CLI takes precedence.")

    elif COLOR_FROM_ENV:
        print(f"🌍 Color from environment: {COLOR_FROM_ENV}")
        COLOR = COLOR_FROM_ENV

    else:
        print(f"🎲 No color provided, choosing random: {COLOR}")

    # Validate Color
    if COLOR not in color_codes:
        print(f"❌ Unsupported color: '{COLOR}'. Use one of: {SUPPORTED_COLORS}")
        exit(1)

    # Start Flask Application
    print("🚀 Starting Flask App on Port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
