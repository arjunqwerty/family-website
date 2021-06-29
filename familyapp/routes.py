from flask import render_template, flash, redirect, url_for, session, request
from functools import wraps
from passlib.hash import sha256_crypt as sa
import random as rd

from familyapp import app, db
from familyapp.model import RegisterDetails, FamilyDetails, FamilyNames

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("UNAUTHORISED, Please Login", "danger")
            return redirect(url_for("home"))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "admin" in session:
            return f(*args, **kwargs)
        else:
            flash("UNAUTHORISED", "danger")
            return redirect(url_for("home"))
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
                session["admin"] = True
                return redirect(url_for("admindashboard"))
            else:
                flash("Don't try to get into Administration", "danger")
                return redirect(url_for("home"))
        else:
            if db.session.query(RegisterDetails).filter(RegisterDetails.name == peoplename).count() == 0:
                flash("No such username exists", "danger")
                return render_template("login.html")
            else:
                user = db.session.query(RegisterDetails).filter(RegisterDetails.name == peoplename).first()
                if password ==  user.password:
                    session["logged_in"] = True
                    session["username"] = peoplename
                    session["usercode"] = user.identifier
                    flash("You are logged in", "success")
                    return redirect(url_for("index"))
                else:
                    flash("Incorrect password", "danger")
                    return render_template("login.html")
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
        session["name"] = person.name
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
    return render_template("adddetails.html", familynames = db.session.query(FamilyNames).all())

@app.route("/details/edit", methods = ["GET", "POST"])
def editdetails():
    identifier = session["usercode"]
    if request.method == "POST":
        people = db.session.query(FamilyDetails).filter(FamilyDetails.identifier == identifier).first()
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
    return render_template("editdetails.html", profile = db.session.query(FamilyDetails).filter(FamilyDetails.identifier == identifier).first())

@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("home"))

@app.route("/admin/dashboard", methods = ["GET", "POST"])
@is_admin
def admindashboard():
    return render_template("admindashboard.html")

@app.route("/admin/table/display/<number>", methods = ["GET", "POST"])
@is_admin
def displaytables(number):
    session["number"] = number
    if number == "All":
        return render_template("displaytables.html", registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all(), familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all(), familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    elif number == "1":
        return render_template("displaytables.html", registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif number == "2":
        return render_template("displaytables.html", familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif number == "3":
        return render_template("displaytables.html", familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))
    return render_template("displaytables.html")

@app.route("/admin/table/delete/<number>", methods = ["GET", "POST"])
@is_admin
def deletetables(number):
    if number == "All":
        db.session.query(RegisterDetails).delete()
        db.session.query(FamilyDetails).delete()
        db.session.query(FamilyNames).delete()
        db.session.commit()
    elif number == "1":
        db.session.query(RegisterDetails).delete()
        db.session.commit()
    elif number == "2":
        db.session.query(FamilyDetails).delete()
        db.session.commit()
    elif number == "3":
        db.session.query(FamilyNames).delete()
        db.session.commit()
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))
    return redirect(url_for("admindashboard"))

@app.route("/admin/table/delete/row/<number>", methods = ["GET", "POST"])
@is_admin
def deletetablerow(number):
    session["number"] = number
    if number == "All":
        return render_template("deletetablerow.html", registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all(), familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all(), familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    elif number == "1":
        return render_template("deletetablerow.html", registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif number == "2":
        return render_template("deletetablerow.html", familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif number == "3":
        return render_template("deletetablerow.html", familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))
    return render_template("deletetablerow.html")

@app.route("/admin/delete/row/<chumma>", methods = ["GET", "POST"])
@is_admin
def deleterow(chumma):
    number = session["number"]
    session["chumma"] = chumma
    if number == "1":
        data = db.session.query(RegisterDetails).filter(RegisterDetails.id == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for("deletetablerow", number = "1"))
    elif number == "2":
        data = db.session.query(FamilyDetails).filter(FamilyDetails.id == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for("deletetablerow", number = "2"))
    elif number == "3":
        data = db.session.query(FamilyNames).filter(FamilyNames.id == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for("deletetablerow", number = "3"))
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))
    return render_template("deletetablerow.html")

@app.route("/admin/logout")
@is_admin
def adminlogout():
    session.clear()
    return redirect(url_for("home"))
