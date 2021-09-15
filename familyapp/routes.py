from flask import render_template, flash, redirect, url_for, session, request
from functools import wraps
from sqlalchemy import asc, desc, func
import pickle

from familyapp import app, db
from familyapp.model import RegisterDetails, FamilyDetails, FamilyNames, Relation

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

def getbinarydat(filename):
    lst = []
    f = open("familyapp/" + filename, "rb")
    try:
        while True:
            line = pickle.load(f)
            lst.append(line)
    except EOFError:
        f.close()
    return lst

@app.route("/sitemap")
def sitemap():
    # Route to dynamically generate a sitemap of your website/application. lastmod and priority tags omitted on static pages. lastmod included on dynamic content such as blog posts.
    from flask import make_response, request, render_template
    from urllib.parse import urlparse
    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc
    # Static routes with static content
    urlstatic = []
    for rule in app.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/user"):
            urlstatic.append(f"{host_base}{str(rule)}")
    urlstatic.sort()
    xml_sitemap = render_template("sitemap.xml", urlstatic = urlstatic, host_base = host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"
    return response
    # Dynamic routes with dynamic content
    '''try:
        dynamic_urls = list()
        blog_posts = Post.objects(published = True)
        for post in blog_posts:
            url = {"loc": f"{host_base}/blog/{post.category.name}/{post.url}", "lastmod": post.date_published.strftime("%Y-%m-%dT%H:%M:%SZ")}
            dynamic_urls.append(url)
        xml_sitemap = render_template("sitemap.xml", urlstatic = urlstatic, dynamic_urls = dynamic_urls, host_base = host_base)
    except:
        xml_sitemap = render_template("sitemap.xml", urlstatic = urlstatic, host_base = host_base)'''

@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        phonecode = request.form["phonecode"]
        phone = request.form["phone"]
        phone = phonecode + " " + phone
        password = request.form["password"]
        famdet = FamilyDetails("", "", "2000-01-01", "", "", "", "", "", "", phone, "")
        db.session.add(famdet)
        data = RegisterDetails(name, phone, password, "")
        db.session.add(data)
        db.session.commit()
        flash("Please wait for approval from admin", "success")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/", methods = ["GET", "POST"])
@app.route("/login", methods = ["GET", "POST"])
def home():
    try:
        if session["logged_in"]:
            return redirect(url_for("index"))
    except:
        #session["maintenance"] = "maintain" maintain (or) production
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
                    if user.approval == "Approved":
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
                        flash("Contact T R Murali - 9952099044 or T M Arjun - 9489826248", "info")
                        return render_template("login.html")
        else:
            lstphonecodes = getbinarydat("phonecode.dat")
            return render_template("login.html", phonecodes = lstphonecodes)

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
        session["filtercoloumn"] = "default"
        session["filterrowval"] = "default"
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
    if session["filter"]:
        return redirect(url_for("index"))
    else:
        return redirect(url_for("indexfiltering", coloumn = session["filtercoloumn"], rowval = session["filterrowval"]))

@app.route("/index/filter/<coloumn>/<rowval>", methods = ["GET", "POST"])
def indexfiltering(coloumn, rowval):
    session["filtercoloumn"] = coloumn
    session["filterrowval"] = rowval
    usercode = session["userid"]
    person = db.session.query(FamilyDetails).filter(FamilyDetails.id == usercode).first()
    session["filter"] = False
    if coloumn == "Name":
        session["name"] = person.salutation + person.name
        sorting = session["sortid"]
        addressdata = db.session.query(FamilyDetails).distinct(FamilyDetails.city).all()
        familynames = db.session.query(FamilyNames).all()
        if session["sortby"] == "asc":
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(desc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
        else:
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(desc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(desc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(desc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(desc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
    elif coloumn == "Address":
        session["name"] = person.salutation + person.name
        sorting = session["sortid"]
        addressdata = db.session.query(FamilyDetails).distinct(FamilyDetails.city).all()
        familynames = db.session.query(FamilyNames).all()
        if session["sortby"] == "asc":
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(desc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
        else:
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(desc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(desc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(desc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(desc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
    elif coloumn == "FamilyName":
        session["name"] = person.salutation + person.name
        sorting = session["sortid"]
        addressdata = db.session.query(FamilyDetails).distinct(FamilyDetails.city).all()
        familynames = db.session.query(FamilyNames).all()
        if session["sortby"] == "asc":
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(desc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
        else:
            if sorting == "name":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(desc(FamilyDetails.name)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "phone":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(desc(FamilyDetails.phone)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "dob":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.dateofbirth)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            elif sorting == "familyname":
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(desc(FamilyDetails.familyname)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
            else:
                details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(desc(FamilyDetails.id)).all()
                return render_template("index.html", data = details, addressdata = addressdata, familynames = familynames)
    else:
        session["filter"] = True
        return redirect(url_for("indexsorting", sortid = "default", sortby = "asc"))

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
        country = request.form["country"]
        country = country[:country.find(" |"):]
        state = request.form["state"]
        state = state[:state.find(" |"):].strip(" ")
        city = request.form["city"].strip(" ")
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
        update.country = country
        update.state = state
        update.city = city
        update.pincode = pincode
        update.dateofbirth = dob
        update.phone = phone
        update.familyname = familyname
        db.session.commit()
        relationdet = Relation(update.id, name, "", "", "", "", "")
        db.session.add(relationdet)
        db.session.commit()
        flash("Details added", "success")
        return redirect(url_for("index"))
    lstcount = getbinarydat("country.dat")
    lststate = getbinarydat("state.dat")
    lstcity = getbinarydat("city.dat")
    lstphone = getbinarydat("phonecode.dat")
    return render_template("adddetails.html", data = update, familynames = db.session.query(FamilyNames).all(), phonenum = db.session.query(FamilyDetails).filter(FamilyDetails.id == usercode).first().phone, country = lstcount, states = lststate, cities = lstcity, phonecode = lstphone)###

@app.route("/details/edit", methods = ["GET", "POST"])
def editdetails():
    identifier = session["userid"]
    person = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
    if person.name == "" or person.housestreet == "" or person.neighbourhood == "" or person.city == "" or person.state == "" or person.pincode == "" or person.phone == "" or person.dateofbirth == "" or person.familyname == "":
        flash("Please enter the details", "danger")
        return redirect(url_for("adddetails"))
    else:
        if request.method == "POST":
            people = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
            housest = request.form["housest"]
            locality = request.form["locality"]
            country = request.form["country"]
            country = country[:country.find(" |"):]
            state = request.form["state"]
            state = state[:state.find(" |"):].strip(" ")
            city = request.form["city"].strip(" ")
            pincode = request.form["pincode"]
            phone = request.form["phone"]
            if housest != people.housestreet:
                people.housestreet = housest
            if locality != people.neighbourhood:
                people.neighbourhood = locality
            if country != people.country:
                people.country = country
            if state != people.state:
                people.state = state
            if city != people.city:
                people.city = city
            if pincode != people.pincode:
                people.pincode = pincode
            if phone != people.phone:
                people.phone = phone
            db.session.commit()
            flash("Profile updated", "success")
            return redirect(url_for("index"))
        lstcount = getbinarydat("country.dat")
        lststate = getbinarydat("state.dat")
        lstcity = getbinarydat("city.dat")
        lstphone = getbinarydat("phonecode.dat")
        return render_template("editdetails.html", profile = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first(), country = lstcount, states = lststate, cities = lstcity, phonecode = lstphone)

@app.route("/printpage", methods = ["GET", "POST"])
def printpdf():
    coloumn = session["filtercoloumn"]
    rowval = session["filterrowval"]
    if coloumn == "Name":
        details = db.session.query(FamilyDetails).filter(func.lower(FamilyDetails.name).startswith(rowval.lower())).order_by(asc(FamilyDetails.name)).all()
    elif coloumn == "Address":
        details = db.session.query(FamilyDetails).filter(FamilyDetails.city == rowval).order_by(asc(FamilyDetails.name)).all()
    elif coloumn == "FamilyName":
        details = db.session.query(FamilyDetails).filter(FamilyDetails.familyname == rowval).order_by(asc(FamilyDetails.name)).all()
    else:
        details = db.session.query(FamilyDetails).order_by(asc(FamilyDetails.name)).all()
    return render_template("printpage.html", data = details)

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

@app.route("/admin/approval/<stat>/<idapprove>", methods = ["GET", "POST"])
def adminapproval(stat,idapprove):
    if stat == "none":
        return render_template("adminapproval.html", data = db.session.query(RegisterDetails).filter(RegisterDetails.approval == "").all())
    elif stat == "approved":
        profile = db.session.query(RegisterDetails).filter(RegisterDetails.id == idapprove).first()
        profile.approval = "Approved"
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
    if addrownumber == "1and2":
        if request.method == "POST":
            username = request.form["username"]
            phonecode = request.form["phonecode"]
            mainphone = phonecode + " " + request.form["mainphone"]
            password = request.form["password"]
            approval = request.form["approval"]
            salutation = request.form["salutation"]
            name = request.form["name"]
            housestreet = request.form["housest"]
            neighbourhood = request.form["locality"]
            country = request.form["country"]
            country = country[:country.find(" |"):]
            state = request.form["state"]
            state = state[:state.find(" |"):].strip(" ")
            city = request.form["city"].strip(" ")
            pincode = request.form["pincode"]
            dateofbirth = request.form["dateofbirth"]
            phone = request.form["phone"]
            family = request.form["familyname"]
            if family == "other":
                familyname = request.form["otherfamilyname"]
                data = FamilyNames(familyname)
                db.session.add(data)
                db.session.commit()
            else:
                familyname = family
            data = RegisterDetails(username, mainphone, password, approval)
            db.session.add(data)
            db.session.commit()
            data = FamilyDetails(salutation, name, dateofbirth, housestreet, neighbourhood, city, state, country, pincode, phone, familyname)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for("admindashboard"))
        lstcount = getbinarydat("country.dat")
        lststate = getbinarydat("state.dat")
        lstcity = getbinarydat("city.dat")
        lstphone = getbinarydat("phonecode.dat")
        return render_template("adminaddtable.html", familynames = db.session.query(FamilyNames).all(), country = lstcount, states = lststate, cities = lstcity, phonecode = lstphone)
    elif addrownumber == "3":
        if request.method == "POST":
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
                phonecode = request.form["phonecode"]
                mainphone = phonecode + " " + request.form["mainphone"]
                password = request.form["password"]
                approval = request.form["approval"]
                data = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first()
                data.name = username
                data.phone = mainphone
                data.password = password
                data.approval = approval
                db.session.commit()
                return redirect(url_for("edittableshow", edittablenumber = session["editnumber"], identifier = "chooserow"))
            lstphone = getbinarydat("phonecode.dat")
            return render_template("adminedittable.html", table = "Row Edit", tableid = edittablenumber, registerdet = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first(), phonecode = lstphone)
        return render_template("admindisplaytables.html", table = "Row Edit", tableid = edittablenumber, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif edittablenumber == "2":
        if identifier != "chooserow":
            if request.method == "POST":
                salutation = request.form["salutation"]
                name = request.form["name"]
                dateofbirth = request.form["dob"]
                housestreet = request.form["housest"]
                neighbourhood = request.form["locality"]
                country = request.form["country"]
                country = country[:country.find(" |"):]
                state = request.form["state"]
                state = state[:state.find(" |"):].strip(" ")
                city = request.form["city"].strip(" ")
                pincode = request.form["pincode"]
                phone = request.form["phone"]
                family = request.form["familyname"]
                if family == "other":
                    familyname = request.form["otherfamilyname"]
                    data = FamilyNames(familyname)
                    db.session.add(data)
                    db.session.commit()
                else:
                    familyname = family
                data = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
                if housestreet != data.housestreet:
                    data.housestreet = housestreet
                if neighbourhood != data.neighbourhood:
                    data.neighbourhood = neighbourhood
                if country != data.country:
                    data.country = country
                if state != data.state:
                    data.state = state
                if city != data.city:
                    data.city = city
                if pincode != data.pincode:
                    data.pincode = pincode
                if phone != data.phone:
                    data.phone = phone
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
                return redirect(url_for("edittableshow", edittablenumber = session["editnumber"], identifier = "chooserow"))
            lstcount = getbinarydat("country.dat")
            lststate = getbinarydat("state.dat")
            lstcity = getbinarydat("city.dat")
            lstphone = getbinarydat("phonecode.dat")
            return render_template("adminedittable.html", table = "Row Edit", tableid = edittablenumber, familydet = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first(), familynames = db.session.query(FamilyNames).all(), country = lstcount, states = lststate, cities = lstcity, phonecode = lstphone)
        return render_template("admindisplaytables.html", table = "Row Edit", tableid = edittablenumber, familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif edittablenumber == "3":
        if identifier != "chooserow":
            if request.method == "POST":
                familyname = request.form["familyname"]
                data = db.session.query(FamilyNames).filter(FamilyDetails.id == identifier).first()
                data.name = familyname
                db.session.commit()
                return redirect(url_for("edittableshow", edittablenumber = session["editnumber"], identifier = "chooserow"))
            return render_template("adminedittable.html", table = "Row Edit", tableid = edittablenumber, familynames = db.session.query(FamilyNames).filter(FamilyNames.id == identifier).first())
        return render_template("admindisplaytables.html", table = "Row Edit", tableid = edittablenumber, familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
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
        return render_template("admindisplaytables.html", table = "Row Delete", registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all(), familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all(), familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    if session["deletenumber"] == "1":
        if identifier != "chooserow":
            data = db.session.query(RegisterDetails).filter(RegisterDetails.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete", tableid = deleterownumber, registerdet = db.session.query(RegisterDetails).order_by(RegisterDetails.id.asc()).all())
    elif session["deletenumber"] == "2":
        if identifier != "chooserow":
            data = db.session.query(FamilyDetails).filter(FamilyDetails.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete", tableid = deleterownumber, familydet = db.session.query(FamilyDetails).order_by(FamilyDetails.id.asc()).all())
    elif session["deletenumber"] == "3":
        if identifier != "chooserow":
            data = db.session.query(FamilyNames).filter(FamilyNames.id == identifier).first()
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for("deletetablerow", deleterownumber = deleterownumber, identifier = "chooserow"))
        return render_template("admindisplaytables.html", table = "Row Delete", tableid = deleterownumber, familynames = db.session.query(FamilyNames).order_by(FamilyNames.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for("admindashboard"))

'''@app.route("/admin/table/delete/<number>", methods = ["GET", "POST"])
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
'''
@app.route("/admin/relation", methods = ["GET", "POST"])
@is_admin
def relation():
    return render_template("adminrelation.html", relation = db.session.query(Relation).all())

@app.route("/admin/relation/show/<relationname>", methods = ["GET", "POST"])
def showrelations(relationname):
    relation = db.session.query(Relation).filter(Relation.name == relationname).all()
    return render_template("adminrelation.html", relation = relation)

@app.route("/admin/relation/edit/<number>", methods = ["GET", "POST"])
def editrelation(number):
    if request.method == "POST":
        name = request.form["name"]
        spouse = request.form["spouse"]
        father = request.form["father"]
        mother = request.form["mother"]
        children = request.form["children"]
        siblings = request.form["siblings"]
        first = db.session.query(Relation).filter(Relation.id == number).first()
        if first.name != name:
            first.name = name
        if first.spouse != spouse:
            first.spouse = spouse
        if first.father != father:
            first.father = father
        if first.mother != mother:
            first.mother = mother
        if first.child != children:
            first.child = children
        if first.sibling != siblings:
            first.sibling = siblings
        db.session.commit()
        return redirect(url_for("relation"))
    return render_template("adminrelationedit.html", person = db.session.query(FamilyDetails.name).order_by(FamilyDetails.name).all(), relationdet = db.session.query(Relation).filter(Relation.id == number).first())

@app.route("/admin/table/extraadd", methods = ["GET", "POST"])
@is_admin
def extradetailsadd():
    if request.method == "POST":
        id = request.form["id"]
        phone = request.form["phone"]
        famdet = FamilyDetails(id, "", "", "2000-01-01", "", "", "", "", "", "", phone, "")
        db.session.add(famdet)
        db.session.commit()
        return redirect(url_for("extradetailsadd"))
    return render_template("dummy.html")

@app.route("/admin/logout")
@is_admin
def adminlogout():
    session.clear()
    return redirect(url_for("home"))
