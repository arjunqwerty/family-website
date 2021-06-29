from familyapp import db

class RegisterDetails(db.Model):
    __tablename__ = "register"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(20))
    identifier = db.Column(db.String(10))

    def __init__(self, name, password, identifier):
        self.name = name
        self.password = password
        self.identifier = identifier

class FamilyDetails(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key = True)
    identifier = db.Column(db.String(10))
    name = db.Column(db.String(200))
    address = db.Column(db.Text())
    phone = db.Column(db.String(50))
    familyname = db.Column(db.String(200))

    def __init__(self, identifier, name, address, phone, familyname):
        self.identifier = identifier
        self.name = name
        self.address = address
        self.phone = phone
        self.familyname = familyname
