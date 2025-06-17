from flask import Flask
from flask import render_template, url_for, request, redirect
import pymysql
pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

import os
load_dotenv()
app = Flask(__name__)

app.config['DEBUG'] = True

app.config['ENV'] = 'development'

app.config['FLASK_ENV'] = 'development'

app.config['SECRET_KEY'] = 'secretkey'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:' + os.getenv('password')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:spacex27@localhost:3306/new_device_mgmt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DeviceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(128))
    devices = db.relationship('Device',backref='devicecategory',lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(128))
    device_description = db.Column(db.String(512))
    inventory = db.Column(db.Integer)
    device_category = db.Column(db.Integer, db.ForeignKey('device_category.id'),nullable=False)

    def __str__(self):
        return f"{self.device_name} - {self.inventory} in stock at present"
    

db.create_all()

@app.route('/list_devices')
def list_devices():
    result_set = db.session.query(Device).all()
    rows = []
    for row in result_set:
        print(row.__dict__)
        rows.append(row)
    print(rows)
    return render_template("list_devices.html",rows=rows,rows_count=len(rows))

@app.route('/new_device_form', methods=['GET', 'POST'])
def new_device_form():
    if request.method == 'GET':
        return render_template("new_device_form.html")

    elif request.method == 'POST':
        valid_device_category = \
            DeviceCategory.query.filter(DeviceCategory.id == request.form.get('device_category')).count()
        if valid_device_category:
            new_device = Device(device_name=request.form.get('device_name'),
                                device_description=request.form.get('device_description'),
                                inventory=request.form.get('Inventory'),
                                device_category=request.form.get('device_category'))

            db.session.add(new_device)
            db.session.commit()
        else:
            return f"<h2>Invalid Device Category {request.form.get('device_category')}</h2>"

        strn = url_for("list_devices")
        print(strn)
        return redirect(strn)
    

@app.route('/delete_a_device/<int:device_id>')
def delete_a_device(device_id):
    device_deleted = Device.query.filter(Device.id == device_id).delete()
    if device_deleted:
        db.session.commit()
    else:
        return f'<h2>Invalid Device ID {device_id}</h2>'

    strn = url_for("list_devices")
    return redirect(strn)

@app.route('/update_a_device/<int:device_id>')
def update_a_device(device_id):
    valid_device = Device.query.get(device_id)
    device_category = request.args.get('device_cat')
    valid_device_category = 0
    if device_category:
        valid_device_category = DeviceCategory.query.filter(DeviceCategory.id == device_category).count()
    else:
        device_category = valid_device.device_category
        valid_device_category = 1

    print(device_category, valid_device_category)

    if valid_device and valid_device_category:
        device_name = request.args.get('device_name')
        device_description = request.args.get('description')
        inventory = request.args.get('inventory')

        if device_name:
            valid_device.device_name = device_name

        if device_description:
            valid_device.device_description = device_description

        if inventory:
            valid_device.inventory = inventory

        if valid_device_category:
            valid_device.device_category = device_category

        db.session.add(valid_device)
        db.session.commit()
    else:
        return f'<h2>Invalid Device {device_id} or Device Category {device_category}</h2>'

    strn = url_for("list_devices")
    return redirect(strn)










if __name__=="__main__":
    app.run(debug=True)