import os
import pymysql # Make sure to install this: pip install pymysql
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ---------------- Database Configuration ----------------
DB_TYPE = os.environ.get("DB_TYPE", "mysql") # Default to mysql now

if DB_TYPE == "mysql":
    # Aiven requires SSL. We must point to the ca.pem file.
    # Ensure ca.pem is uploaded to Render in the same folder as app.py
    ssl_args = {
        "ssl": {
            "ca": "ca.pem" 
        }
    }
    
    # Construct the Aiven MySQL Connection String
    # Format: mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    dbname = os.environ.get('DB_NAME')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": ssl_args}

elif DB_TYPE == "postgres":
    # ... (Keep your old Postgres code here if you want a backup) ...
    pass
else:
    # SQLite fallback
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'vendordb.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ---------------- Database Model ----------------
class VendorDetails(db.Model):
    __tablename__ = 'vendordetails'
    
    # --- CHANGE 1: New Primary Key ---
    Aadhar_No = db.Column(db.String(12), primary_key=True)
    
    # --- CHANGE 2: PAN is now just Unique, not PK ---
    PAN = db.Column(db.String(20), unique=True, nullable=False)
    
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

# Create tables if not exist (Note: This won't update existing tables, see /reset-db below)
with app.app_context():
    db.create_all()

# ---------------- Routes ----------------

# --- CHANGE 3: Reset DB Route (Use this ONCE after deployment) ---
@app.route('/reset-db', methods=['POST'])
def reset_db():
    try:
        # WARNING: This deletes all existing data!
        db.drop_all()   
        db.create_all() 
        return jsonify({"message": "Database reset successfully. New Aadhar schema applied."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = VendorDetails.query.all()
    result = [v.__dict__ for v in vendors]
    for r in result:
        r.pop('_sa_instance_state', None)
    return jsonify(result), 200

# --- CHANGE 4: Updated to fetch by Aadhar ---
@app.route('/vendors/<string:aadhar>', methods=['GET'])
def get_vendor(aadhar):
    vendor = VendorDetails.query.get(aadhar) # Looks up by PK (Aadhar)
    if vendor:
        data = vendor.__dict__
        data.pop('_sa_instance_state', None)
        return jsonify(data), 200
    return jsonify({"message": "Vendor not found"}), 404

@app.route('/vendors', methods=['POST'])
def add_vendor():
    data = request.get_json()
    # --- CHANGE 5: Added Aadhar_No to required fields ---
    required_fields = ['Legal_Name', 'Business_Type', 'Registered_Address', 
                       'Communication_Address', 'Email', 'Phone_Number', 'PAN', 'Aadhar_No']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        vendor = VendorDetails(**data)
        db.session.add(vendor)
        db.session.commit()
        return jsonify({"message": "Vendor added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CHANGE 6: Updated to update by Aadhar ---
@app.route('/vendors/<string:aadhar>', methods=['PUT'])
def update_vendor(aadhar):
    data = request.get_json()
    vendor = VendorDetails.query.get(aadhar)
    if not vendor:
        return jsonify({"message": "Vendor not found"}), 404

    for key, value in data.items():
        if hasattr(vendor, key):
            setattr(vendor, key, value)
    db.session.commit()
    return jsonify({"message": "Vendor updated successfully"}), 200

# --- CHANGE 7: Updated to delete by Aadhar ---
@app.route('/vendors/<string:aadhar>', methods=['DELETE'])
def delete_vendor(aadhar):
    vendor = VendorDetails.query.get(aadhar)
    if not vendor:
        return jsonify({"message": "Vendor not found"}), 404

    db.session.delete(vendor)
    db.session.commit()
    return jsonify({"message": "Vendor deleted successfully"}), 200

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
