from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "jobportal_secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="security",
    database="jobportal"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        cursor = db.cursor()

        query = """
        INSERT INTO users (full_name, email, password)
        VALUES (%s, %s, %s)
        """

        values = (full_name, email, password)

        cursor.execute(query, values)
        db.commit()

        cursor.close()

        return "Registration Successful!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        cursor.close()

        if user:
            session["user_email"] = user["email"]
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/my-applications")
def my_applications():

    if "user_email" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT * FROM applications
    WHERE email = %s
    ORDER BY created_at DESC
    """

    cursor.execute(query, (session["user_email"],))

    applications = cursor.fetchall()

    cursor.close()

    return render_template(
        "my-applications.html",
        applications=applications
    )

@app.route("/jobs")
def jobs():

    keyword = request.args.get("keyword", "")
    location = request.args.get("location", "")

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT * FROM jobs
        WHERE
        (title LIKE %s OR company LIKE %s OR skills LIKE %s)
        AND location LIKE %s
    """

    search_keyword = "%" + keyword + "%"
    search_location = "%" + location + "%"

    cursor.execute(
        query,
        (
            search_keyword,
            search_keyword,
            search_keyword,
            search_location
        )
    )

    jobs = cursor.fetchall()

    cursor.close()

    return render_template(
        "jobs.html",
        jobs=jobs,
        keyword=keyword,
        location=location
    )


@app.route("/job-details/<int:job_id>")
def job_details(job_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM jobs WHERE id = %s",
        (job_id,)
    )

    job = cursor.fetchone()

    cursor.close()

    if job is None:
        return "Job not found!", 404

    return render_template(
        "job-details.html",
        job=job
    )



@app.route("/apply.html")
def apply():
    return render_template("apply.html")

@app.route("/submit-application", methods=["POST"])
def submit_application():

    full_name = request.form["full_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    resume = request.form["resume"]
    cover_message = request.form["cover_message"]

    cursor = db.cursor()

    query = """
    INSERT INTO applications
    (full_name, email, phone, resume, cover_message, applied_job)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        full_name,
        email,
        phone,
        resume,
        cover_message,
        "Python Developer"
    )

    cursor.execute(query, values)
    db.commit()

    cursor.close()

    return "Application Submitted Successfully!"

@app.route("/admin/applications")
def admin_applications():

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM applications ORDER BY created_at DESC"
    )

    applications = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin-applications.html",
        applications=applications
    )
if __name__ == "__main__":
    app.run(debug=True)