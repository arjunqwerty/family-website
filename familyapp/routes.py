from flask import render_template, flash, redirect, url_for, session, request
from functools import wraps
from passlib.hash import sha256_crypt as sa
import random as rd
from sqlalchemy import asc, desc

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
        phone = request.form["phone"]
        password = request.form["password"]
        famdet = FamilyDetails("", "", "2000-01-01", "", "", "", "", "", phone, "")
        db.session.add(famdet)
        data = RegisterDetails(name, phone, password, " ")
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
                session["logged_in"] = True
                session["userid"] = "1"
                session["sortid"] = ""
                session["sortby"] = "asc"
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
                if user.approval == "approved":
                    if password ==  user.password:
                        session["logged_in"] = True
                        session["username"] = peoplename
                        session["userid"] = user.id
                        session["sortid"] = ""
                        session["sortby"] = "asc"
                        flash("You are logged in", "success")
                        return redirect(url_for("index"))
                    else:
                        flash("Incorrect password", "danger")
                        return render_template("login.html")
                else:
                    flash("Please wait for admin approval", "danger")
                    flash("Contact T R Murali - 9952099044", "info")
                    return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/index", methods = ["GET", "POST"])
@is_logged_in
def index():
    usercode = session["userid"]
    person = db.session.query(FamilyDetails).filter(FamilyDetails.id == usercode).first()
    if person.name == "" or person.housestreet == "" or person.neighbourhood == "" or person.city == "" or person.state == "" or person.pincode == "" or person.phone == "" or person.dateofbirth == "" or person.familyname == "":
        flash("Please enter the details", "danger")
        return redirect(url_for("adddetails"))
    else:
        session["filter"] = True
        session["name"] = person.salutation + person.name
        sorting = session["sortid"]
        addressdata = db.session.query(FamilyDetails).distinct(FamilyDetails.city).all()
        familynames = db.session.query(FamilyNames).all()
        if session["sortby"] == "asc":
            if sorting == "name":
                details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).order_by(desc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
        else:
            if sorting == "name":
                details = db.session.query(FamilyDetails).order_by(desc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).order_by(desc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).order_by(desc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).order_by(desc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)

@app.route("/index/sorting/<sortid>/<sortby>", methods = ["GET", "POST"])
def indexsorting(sortid, sortby):
    session["sortid"] = sortid
    session["sortby"] = sortby
    return redirect(url_for("index"))

@app.route("/index/filter/<coloumn>/<rowval>", methods = ["GET", "POST"])
def indexfiltering(coloumn, rowval):
    session["filter"] = False
    if coloumn == "Address":
        details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(FamilyDetails.id.asc()).all()
    elif coloumn == "FamilyName":
        details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(FamilyDetails.id.asc()).all()
    return render_template("index.html", data = details, addressdata = db.session.query(FamilyDetails).distinct(FamilyDetails.city).all(), familynames = db.session.query(FamilyNames).all())

@app.route("/details", methods = ["GET", "POST"])
@is_logged_in
def details():
    return render_template("dummy.html")

@app.route("/details/add", methods = ["GET", "POST"])
@is_logged_in
def adddetails():
    usercode = session["userid"]
    update = db.session.query(FamilyDetails).filter(FamilyDetails.id == usercode).first()
    if request.method == "POST":
        salute = request.form["salutation"]
        name = request.form["name"]
        housest = request.form["housest"]
        locality = request.form["locality"]
        city = request.form["city"]
        state = request.form["state"]
        pincode = request.form["pincode"]
        dob = request.form["dob"]
        phone = request.form["phone"]
        family = request.form["familyname"]
        if family == "other":
            familyname = request.form["otherfamilyname"]
            data = FamilyNames(familyname)
            db.session.add(data)
            db.session.commit()
        else:
            familyname = family
        update.salutation = salute
        update.name = name
        update.housestreet = housest
        update.neighbourhood = locality
        update.city = city
        update.state = state
        update.pincode = pincode
        update.dateofbirth = dob
        update.phone = phone
        update.familyname = familyname
        db.session.commit()
        flash("Details added", "success")
        return redirect(url_for("index"))
    return render_template("adddetails.html", data = update, familynames = db.session.query(FamilyNames).all(), phonenum = db.session.query(FamilyDetails).filter(FamilyDetails.id == usercode).first().phone)

@app.route("/details/edit", methods = ["GET", "POST"])
def editdetails():
    identifier = session["userid"]
    if request.method == "POST":
        people = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
        housest = request.form["housest"]
        locality = request.form["locality"]
        city = request.form["city"]
        state = request.form["state"]
        pincode = request.form["pincode"]
        phone = request.form["phone"]
        if housest != people.housestreet:
            people.housestreet = housest
        if locality != people.neighbourhood:
            people.neighbourhood = locality
        if city != people.city:
            people.city = city
        if state != people.state:
            people.state = state
        if pincode != people.pincode:
            people.pincode = pincode
        if phone != people.phone:
            people.phone = phone
        db.session.commit()
        flash("Profile updated", "success")
        return redirect(url_for("index"))
    return render_template("editdetails.html", profile = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first())

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

#### Should add a route for admin to give approval to the requests
@app.route("/admin/approval/<stat>/<idapprove>", methods = ["GET", "POST"])
def adminapproval(stat,idapprove):
    if stat == "none":
        return render_template("approval.html", data = db.session.query(RegisterDetails).filter(RegisterDetails.approval == " ").all())
    elif stat == "approved":
        profile = db.session.query(RegisterDetails).filter(RegisterDetails.id == idapprove).first()
        profile.approval = "approved"
        db.session.commit()
        return redirect(url_for("adminapproval", stat = "none", idapprove = "none"))
    else:
        profile = db.session.query(RegisterDetails).filter(RegisterDetails.id == idapprove).first()
        db.session.delete(profile)
        register = db.session.query(FamilyDetails).filter(FamilyDetails.id == idapprove).first()
        db.session.delete(register)
        db.session.commit()
        return redirect(url_for("adminapproval", stat = "none", idapprove = "none"))

@app.route("/admin/table/display/<number>", methods = ["GET", "POST"])
@is_admin
def displaytables(number):
    session["displaynumber"] = number
    if number == "All":
        return render_template("admindisplaytables.html", table = "Display " + number, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all(), familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all(), familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    elif number == "1":
        return render_template("admindisplaytables.html", table = "Display " + number, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif number == "2":
        return render_template("admindisplaytables.html", table = "Display " + number, familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif number == "3":
        return render_template("admindisplaytables.html", table = "Display " + number, familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))

@app.route("/admin/table/row/add/<addrownumber>", methods = ["GET", "POST"])
@is_admin
def addtablerow(addrownumber):
    session["number"] = addrownumber
    if request.method == "POST":
        if addrownumber == "1and2":
            username = request.form["username"]
            mainphone = request.form["mainphone"]
            password = request.form["password"]
            approval = request.form["approval"]
            salutation = request.form["salutation"]
            name = request.form["name"]
            dateofbirth = request.form["dateofbirth"]
            housestreet = request.form["housestreet"]
            neighbourhood = request.form["neighbourhood"]
            city = request.form["city"]
            state = request.form["state"]
            pincode = request.form["pincode"]
            phone = request.form["phone"]
            familyname = request.form["familyname"]
            data = RegisterDetails(username, mainphone, password, approval)
            db.session.add(data)
            db.session.commit()
            data = FamilyDetails(salutation, name, dateofbirth, housestreet, neighbourhood, city, state, pincode, phone, familyname)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for("admindashboard"))
        elif addrownumber == "3":
            familyname = request.form["familyname"]
            data = FamilyNames(familyname)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for("admindashboard"))
    return render_template("adminaddtable.html")

@app.route("/admin/table/row/edit/<edittablenumber>/<identifier>", methods = ["GET", "POST"])
@is_admin
def edittableshow(edittablenumber, identifier):
    session["editnumber"] = edittablenumber
    session["rowid"] = identifier
    if edittablenumber == "1":
        if identifier != "chooserow":
            if request.method == "POST":
                username = request.form["username"]
                mainphone = request.form["mainphone"]
                password = request.form["password"]
                approval = request.form["approval"]
                data = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first()
                data.name = username
                data.phone = mainphone
                data.password = password
                data.approval = approval
                db.session.commit()
            return render_template("adminedittable.html", table = "Row Edit " + edittablenumber, register = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first())
        return render_template("admindisplaytables.html", table = "Row Edit " + edittablenumber, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif edittablenumber == "2":
        if identifier != "chooserow":
            if request.method == "POST":
                salutation = request.form["salutation"]
                name = request.form["name"]
                dateofbirth = request.form["dateofbirth"]
                housestreet = request.form["housestreet"]
                neighbourhood = request.form["neighbourhood"]
                city = request.form["city"]
                state = request.form["state"]
                pincode = request.form["pincode"]
                phone = request.form["phone"]
                familyname = request.form["familyname"]
                data = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
                data.salutation = salutation
                data.name = name
                data.dateofbirth = dateofbirth
                data.housestreet = housestreet
                data.neighbourhood = neighbourhood
                data.city = city
                data.state = state
                data.pincode = pincode
                data.phone = phone
                data.familyname = familyname
                db.session.commit()
            return render_template("adminedittable.html", table = "Row Edit " + edittablenumber, familydet = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first())
        return render_template("admindisplaytables.html", table = "Row Edit " + edittablenumber, familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif edittablenumber == "3":
        if identifier != "chooserow":
            if request.method == "POST":
                familyname = request.form["familyname"]
                data = db.session.query(FamilyNames).filter(FamilyDetails.id == identifier).first()
                data.name = familyname
                db.session.commit()
            return render_template("adminedittable.html", table = "Row Edit " + edittablenumber, familynames = db.session.query(FamilyNames).filter(FamilyNames.id == identifier).first())
        return render_template("admindisplaytables.html", table = "Row Edit " + edittablenumber, familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))

@app.route("/admin/table/row/delete/<deleterownumber>/<identifier>", methods = ["GET", "POST"])
@is_admin
def deletetablerow(deleterownumber, identifier):
    if identifier == "chooserow":
        session["deletenumber"] = deleterownumber
    if session["deletenumber"] == "All":
        if identifier != "chooserow":
            if deleterownumber == "1":
                data = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first()
                db.session.delete(data)
                db.session.commit()
            elif deleterownumber == "2":
                data = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
                db.session.delete(data)
                db.session.commit()
            elif deleterownumber == "3":
                data = db.session.query(FamilyNames).filter(FamilyNames.id == identifier).first()
                db.session.delete(data)
                db.session.commit()
            else:
                flash("No such table exists", "danger")
                return redirect(url_for("admindashboard"))
            return redirect(url_for("deletetablerow", deleterownumber = session["deletenumber"], identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete " + session["deletenumber"], registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all(), familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all(), familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    if session["deletenumber"] == "1":
        if identifier != "chooserow":
            data = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete " + deleterownumber, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif session["deletenumber"] == "2":
        if identifier != "chooserow":
            data = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete " + deleterownumber, familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif session["deletenumber"] == "3":
        if identifier != "chooserow":
            data = db.session.query(FamilyNames).filter(FamilyNames.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete " + deleterownumber, familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))

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

@app.route("/admin/logout")
@is_admin
def adminlogout():
    session.clear()
    return redirect(url_for("home"))
