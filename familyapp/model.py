from familyapp import db

class RegisterDetails(db.Model):
    __tablename__ = "register"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(20))
    approval = db.Column(db.String(10))

    def __init__(self, name, phone, password, approval):
        self.name = name
        self.phone = phone
        self.password = password
        self.approval = approval

class FamilyDetails(db.Model):
    __tablename__ = "details"
    id = db.Column(db.Integer, primary_key = True)
    salutation = db.Column(db.String(10))
    name = db.Column(db.String(200))
    dateofbirth = db.Column(db.Date())
    housestreet = db.Column(db.String(100))
    neighbourhood = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    phone = db.Column(db.String(100))
    familyname = db.Column(db.String(200))

    def __init__(self, salutation, name, dateofbirth, housestreet, neighbourhood, city, state, pincode, phone, familyname):
        self.salutation = salutation
        self.name = name
        self.dateofbirth = dateofbirth
        self.housestreet = housestreet
        self.neighbourhood = neighbourhood
        self.city = city
        self.state = state
        self.pincode = pincode
        self.phone = phone
        self.familyname = familyname

class FamilyNames(db.Model):
    __tablename__ = "familyname"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name
