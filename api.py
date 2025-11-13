import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ---------------- Database Configuration ----------------
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")  # "sqlite" or "mysql"

if DB_TYPE == "mysql":
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
        f"@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    )
else:
    # Default to SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'vendordb.sqlite')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- Database Model ----------------
class VendorDetails(db.Model):
    __tablename__ = 'vendordetails'
    PAN = db.Column(db.String(20), primary_key=True)
    Legal_Name = db.Column(db.String(100))
    Business_Type = db.Column(db.String(50))
    Registered_Address = db.Column(db.String(200))
    Communication_Address = db.Column(db.String(200))
    Email = db.Column(db.String(100))
    Phone_Number = db.Column(db.String(20))
    GSTIN = db.Column(db.String(20))
    CIN = db.Column(db.String(20))
    Udyam_ID = db.Column(db.String(50))
    IEC_Code = db.Column(db.String(50))
    TAN = db.Column(db.String(20))
    Bank_Name = db.Column(db.String(50))
    Branch = db.Column(db.String(50))
    IFSC_Code = db.Column(db.String(20))
    Account_Verification = db.Column(db.String(50))
    GSTIN_Status = db.Column(db.String(50))
    PAN_Status = db.Column(db.String(50))
    Name_Match = db.Column(db.String(50))
    PAN_Card = db.Column(db.String(100))
    GST_Certificate = db.Column(db.String(100))
    MSME_Certificate = db.Column(db.String(100))
    Incorporation_Deed = db.Column(db.String(100))
    Signature = db.Column(db.String(100))
    Bank_Proof = db.Column(db.String(100))
    Cancelled_Cheque = db.Column(db.String(100))
    Address_Proof = db.Column(db.String(100))
    City = db.Column(db.String(50))
    State = db.Column(db.String(50))
    Country = db.Column(db.String(50))
    Pincode = db.Column(db.String(10))
    Photo = db.Column(db.String(100))
    Vendor_Name = db.Column(db.String(100))
    Contact_Person_Designation = db.Column(db.String(50))

# Create tables if not exist
with app.app_context():
    db.create_all()

# ---------------- Routes ----------------

# GET all vendors
@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = VendorDetails.query.all()
    result = [v.__dict__ for v in vendors]
    for r in result:
        r.pop('_sa_instance_state', None)
    return jsonify(result), 200

# GET vendor by PAN
@app.route('/vendors/<string:pan>', methods=['GET'])
def get_vendor(pan):
    vendor = VendorDetails.query.get(pan)
    if vendor:
        data = vendor.__dict__
        data.pop('_sa_instance_state', None)
        return jsonify(data), 200
    return jsonify({"message": "Vendor not found"}), 404

# POST add new vendor
@app.route('/vendors', methods=['POST'])
def add_vendor():
    data = request.get_json()
    required_fields = ['Legal_Name', 'Business_Type', 'Registered_Address', 
                       'Communication_Address', 'Email', 'Phone_Number', 'PAN']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    vendor = VendorDetails(**data)
    db.session.add(vendor)
    db.session.commit()
    return jsonify({"message": "Vendor added successfully"}), 201

# PUT update vendor
@app.route('/vendors/<string:pan>', methods=['PUT'])
def update_vendor(pan):
    data = request.get_json()
    vendor = VendorDetails.query.get(pan)
    if not vendor:
        return jsonify({"message": "Vendor not found"}), 404

    for key, value in data.items():
        if hasattr(vendor, key):
            setattr(vendor, key, value)
    db.session.commit()
    return jsonify({"message": "Vendor updated successfully"}), 200

# DELETE vendor
@app.route('/vendors/<string:pan>', methods=['DELETE'])
def delete_vendor(pan):
    vendor = VendorDetails.query.get(pan)
    if not vendor:
        return jsonify({"message": "Vendor not found"}), 404

    db.session.delete(vendor)
    db.session.commit()
    return jsonify({"message": "Vendor deleted successfully"}), 200

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
