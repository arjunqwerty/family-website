from flask import render_template, flash, redirect, url_for, session, request
from functools import wraps
from passlib.hash import sha256_crypt as sa
import random as rd

from familyapp import app, db
from familyapp.model import RegisterDetails, FamilyDetails

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED, Please Login', 'danger')
            return redirect(url_for('home'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED', 'danger')
            return redirect(url_for('home'))
    return wrap

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        z = True
        code = []
        details = db.session.query(FamilyDetails).all()
        for detail in details:
            code.append(detail.identifier)
        while z == True:
            randomcode = rd.randint(100000,1000000)
            if randomcode not in code:
                z = False
                session["usercode"] = str(randomcode)
                famdet = FamilyDetails(randomcode, "", "", "", "")
                db.session.add(famdet)
                db.session.commit()
        data = RegisterDetails(name, password, randomcode)
        db.session.add(data)
        db.session.commit()
        flash("Please wait for approval from admin", "success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/", methods = ["GET", "POST"])
@app.route("/login", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        peoplename = request.form["name"]
        password = request.form["password"]
        if peoplename == "Admin":
            if password == "Admin":
                session['admin'] = True
                return redirect(url_for("admindashboard"))
            else:
                flash("Don't try to get into Administration", "danger")
                return redirect(url_for("home"))
        else:
            if db.session.query(RegisterDetails).filter(RegisterDetails.name == peoplename).count() == 0:
                flash('No such username exists', 'danger')
                return render_template('login.html')
            else:
                user = db.session.query(RegisterDetails).filter(RegisterDetails.name == peoplename).first()
                if password ==  user.password:
                    session["logged_in"] = True
                    session["username"] = peoplename
                    session["usercode"] = user.identifier
                    flash("You are logged in", "success")
                    return redirect(url_for("index"))
                else:
                    flash('Incorrect password', 'danger')
                    return render_template('login.html')
    else:
        return render_template("login.html")

@app.route("/index", methods = ["GET", "POST"])
@is_logged_in
def index():
    usercode = session["usercode"]
    person = db.session.query(FamilyDetails).filter(FamilyDetails.identifier == usercode).first()
    if person.name == "" or person.address == "" or person.phone == "" or person.familyname == "":
        flash("Please enter the details", "danger")
        return redirect(url_for("adddetails"))
    else:
        details = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all()
        if request.method == "POST":
            sorting = request.form["sort"]
            if sorting == "Name":
                details = db.session.query(FamilyDetails).order_by(FamilyDetails.name.asc()).all()
            elif sorting == "Address":
                details = db.session.query(FamilyDetails).order_by(FamilyDetails.address.asc()).all()
            elif sorting == "Phone":
                details = db.session.query(FamilyDetails).order_by(FamilyDetails.phone.asc()).all()
            elif sorting == "Family Name":
                details = db.session.query(FamilyDetails).order_by(FamilyDetails.familyname.asc()).all()
            else:
                details = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all()
            return render_template("index.html", data = details, sort = sorting)
        return render_template("index.html", data = details, sort = "")

@app.route("/details", methods = ["GET", "POST"])
@is_logged_in
def details():
    return render_template("dummy.html")

@app.route("/details/add", methods = ["GET", "POST"])
@is_logged_in
def adddetails():
    if request.method == "POST":
        usercode = session["usercode"]
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        familyname = request.form["familyname"]
        update = db.session.query(FamilyDetails).filter(FamilyDetails.identifier == usercode).first()
        update.name = name
        update.address = address
        update.phone = phone
        update.familyname = familyname
        db.session.commit()
        flash("Details added", "success")
        return redirect(url_for("index"))
    return render_template("adddetails.html")

@app.route("/details/edit/<id>", methods = ["GET", "POST"])
def editdetails(id):
    if request.method == "POST":
        people = db.session.query(FamilyDetails).filter(FamilyDetails.id == id).first()
        name = request.form["name"]
        address = request.form["adderss"]
        phone = request.form["phone"]
        familyname = request.form["familyname"]
        if name != "":
            people.name = name
        if address != "":
            people.address = address
        if phone != "":
            people.phone = phone
        if familyname != "":
            people.familyname = familyname
        db.session.commit()
        flash("Profile updated", "success")
        return redirect(url_for("index"))
    return render_template("editdetails.html")

@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for("home"))

@app.route("/admin/dashboard", methods = ["GET", "POST"])
@is_admin
def admindashboard():
    return render_template("admindashboard.html")

@app.route("/admin/logout")
@is_admin
def adminlogout():
    session.clear()
    return redirect(url_for("home"))
