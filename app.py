from flask import Flask, redirect, url_for,jsonify, render_template, request, send_from_directory, session ,flash 
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from datetime import timedelta
from db import db_init, db
from sqlalchemy.orm import Session
from flask_mail import Mail,Message
from logging import FileHandler , WARNING
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
# from twilio.rest import Client
# import keys

from flask_compress import Compress

from models import Details , Places , LocalWorkforce, Spices, HealthCare,Pharmacy , Art ,Bank , Shop , CivilSupply , Public ,Gallery
from models import WhereToStay,Plantation,Spiceproducts, Transportation ,Admin , Adventure ,Others,Project , Worship , Eservices

from sqlalchemy.sql.expression import update


with open('config.json', 'r') as c:
    data = json.load(c)["data"]

local_server=True    


app = Flask(__name__)
Compress(app)

available_languages = {
    'en': 'English',
    'ml': 'മലയാളം'
}
# client = Client(keys.account_sid , keys.auth_token)

app.config['SECRET_KEY']='dgw^9ej(l4vq_06xig$vw+b(-@#00@8l7jlv77=sq5r_sf3nu'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.permanent_session_lifetime = timedelta(minutes=10)
app.config['DB_SERVER'] = data['local_uri']

app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']="explorepallivasalgp@gmail.com"
app.config['MAIL_PASSWORD']="aapnsstawfopxmle"
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True


mail=Mail(app)

file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

app.logger.addHandler(file_handler)

bcrypt=Bcrypt(app)

def truncate_string(input_string, max_length):
    if len(input_string) > max_length:
        return input_string[:max_length]
    else:
        return input_string
    
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DB_SERVER']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
}


db_init(app)

@app.route('/')
def index():
    if 'language' not in session:
        session['language'] = 'en'  # Default language
    list = Project.query.filter_by().order_by().all()
    return render_template('index.html', language=session['language'], available_languages=available_languages,list = list)

@app.route('/set_language', methods=['POST'])
def set_language():
    selected_language = request.form.get('language')
    session['language'] = selected_language
    return redirect(url_for('index'))

@app.route('/get_translation')
def get_translation():
    language = session.get('language', 'en')
    try:
        with open(f'translations_{language}.json', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    except FileNotFoundError:
        return jsonify({"error": "Translations not found"}), 404


@app.route('/home')
def home():
    list = Project.query.filter_by().order_by().all()
    return render_template("index.html",list = list,language=session['language'], available_languages=available_languages)

@app.route('/view')
def view():
    return render_template('view.html',language=session['language'], available_languages=available_languages)

def authenticate_user(contact, password):
    list = Details.query.filter_by(contact=contact).first()
    if list.accept == 1 and list.password == password:
        return True, list.sno
    else:
        return False, None

@app.route('/userdash/<int:sno>', methods=['GET', 'POST'])
def userdash(sno):
    if(request.method == 'POST'):
        entry1 = LocalWorkforce.query.join(Details).filter(Details.sno == sno).first()
        entry2 = Spices.query.join(Details).filter(Details.sno == sno).first()
        entry3 = WhereToStay.query.join(Details).filter(Details.sno == sno).first()
        entry4 = Plantation.query.join(Details).filter(Details.sno == sno).first()
        entry5 = Transportation.query.join(Details).filter(Details.sno == sno).first()
        entry6 = Pharmacy.query.join(Details).filter(Details.sno == sno).first()
        entry7 = Adventure.query.join(Details).filter(Details.sno == sno).first()
        entry8 = Art.query.join(Details).filter(Details.sno == sno).first()
        entry9 = Others.query.join(Details).filter(Details.sno == sno).first()
        entry10 = Shop.query.join(Details).filter(Details.sno == sno).first()

        if entry1:
            entry1.whatsapp_number = request.form.get('whatsapp')
            entry1.remuneration_details = request.form.get('remuneration')
            entry1.technical_qualifications = request.form.get('technical')
            entry1.years_of_exp = request.form.get('exp')
            pic = request.files['img']
            
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry1.img=filename   

            db.session.commit()

        elif entry2:
            entry2.name=request.form.get('shop')
            entry2.location=request.form.get('loc')
            entry2.contact2=request.form.get('contact2')
            pic = request.files['img']
            
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry2.img=filename   
            db.session.commit()

        elif entry3:
                entry3.name = request.form.get('name')
                entry3.location = request.form.get('location')
                entry3.description = request.form.get('description')
                entry3.facilities = request.form.get('facilities')
                entry3.no_of_rooms = request.form.get('rooms')
                entry3.services = request.form.get('services')
                # img1 = request.files['img1']

                # if img1:
                #     filename = secure_filename(img1.filename)
                #     if (request.method == 'POST'):    
                #         img1.save(os.path.join('static', 'uploads', filename))
                #         # mimetype = pic.mimetype
                # else:
                #     filename = None
                # entry3.img1 = filename
                # db.session.commit()
                if 'files[]' not in request.files:
                    flash('No file selected')
                    return redirect(request.url)

                files = request.files.getlist('files[]')
                num = len(files)
                file_names = []

                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_names.append(filename)
                        file.save(os.path.join('static', 'uploads', filename))

                if num <= 5:
                    for i in range(num):
                        setattr(entry3, f'img{i+1}', file_names[i])
                    db.session.commit()
                else:
                    flash('Only a maximum of 5 should be uploaded!')

        elif entry4:
            entry4.name=request.form.get('name')
            entry4.address=request.form.get('address')
            entry4.location=request.form.get('location')
            entry4.contact=request.form.get('contact')
            entry4.Crops=request.form.get('Crops')
            pic = request.files['img']
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry4.img=filename   
            db.session.commit()

        elif entry5:
            entry5.cost=request.form.get('cost')
            entry5.Trip_available=request.form.get('Trip_available')
            entry5.Pick_up_and_Drop=request.form.get('Pick_up_and_Drop')
            entry5.Duration=request.form.get('Duration')
            entry5.vehicle=request.form.get('vehicle')
            entry5.no_of_persons=request.form.get('no_of_persons')
            entry5.Things_to_carry=request.form.get('Things_to_carry')
            pic = request.files['img']
            
            filename = secure_filename(pic.filename)
            entry5.img=filename   
            pic.save(os.path.join('static', 'uploads', filename))
            db.session.commit()

        elif entry6:
            entry6.name=request.form.get('name')
            entry6.address=request.form.get('address')
            entry6.location=request.form.get('location')
            entry6.contact=request.form.get('contact')
            entry6.type=request.form.get('type')
            pic = request.files['img']
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry6.img=filename   
            db.session.commit()
        
        
        elif entry7:
            entry7.name=request.form.get('name')
            entry7.location=request.form.get('location')
            entry7.description=request.form.get('description')
            entry7.contact=request.form.get('contact')
            entry7.tariff=request.form.get('tariff')
            if 'files[]' not in request.files:
                flash('No file selected')
                return redirect(request.url)

            files = request.files.getlist('files[]')
            num = len(files)
            file_names = []

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_names.append(filename)
                    file.save(os.path.join('static', 'uploads', filename))

            if num <= 5:
                for i in range(num):
                    setattr(entry3, f'img{i+1}', file_names[i])
                db.session.commit()
            else:
                flash('Only a maximum of 5 should be uploaded!')
                
        elif entry8:
            entry8.name = request.form.get('name')
            entry8.location = request.form.get('location')
            entry8.description = request.form.get('description')
            entry8.contact2 = request.form.get('contact')
            entry8.place = request.form.get('place')

            if 'files[]' not in request.files:
                flash('No file selected')
                return redirect(request.url)

            files = request.files.getlist('files[]')
            num = len(files)
            file_names = []

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_names.append(filename)
                    file.save(os.path.join('static', 'uploads', filename))

            if num <= 5:
                for i in range(num):
                    setattr(entry8, f'img{i+1}', file_names[i])

                db.session.commit()
            else:
                flash('Only a maximum of 5 should be uploaded!')

        elif entry9:
            entry9.name=request.form.get('name')
            entry9.location=request.form.get('location')
            entry9.description=request.form.get('description')
            entry9.contact2=request.form.get('contact')
            entry9.place=request.form.get('place')
            pic = request.files['img1']
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry9.img1=filename   
            db.session.commit()

        elif entry10:
            entry10.name=request.form.get('name')
            entry10.shop_type=request.form.get('shop_type')
            entry10.location=request.form.get('location')
            entry10.description=request.form.get('description')
            entry10.contact2=request.form.get('contact')
            entry10.place=request.form.get('place')
            entry10.wt=request.form.get('wt')
            if 'files[]' not in request.files:
                flash('No file selected')
                return redirect(request.url)

            files = request.files.getlist('files[]')
            num = len(files)
            file_names = []

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_names.append(filename)
                    file.save(os.path.join('static', 'uploads', filename))

            if num <= 5:
                for i in range(num):
                    setattr(entry3, f'img{i+1}', file_names[i])
                db.session.commit()
            else:
                flash('Only a maximum of 5 should be uploaded!')



    list = Details.query.filter_by(sno=sno , accept = 1).order_by().all()
    localworkforce = LocalWorkforce.query.filter_by(details_id = sno).order_by().all()
    wheretostay = WhereToStay.query.filter_by(details_id = sno).order_by().all()
    spices = Spices.query.filter_by(details_id = sno).order_by().all()
    spiceproducts = Spiceproducts.query.filter_by().order_by().all()
    plantation = Plantation.query.filter_by(details_id = sno).order_by().all()
    transport=Transportation.query.filter_by(details_id = sno).order_by().all()
    pharmacy=Pharmacy.query.filter_by(details_id = sno).order_by().all()
    adventure=Adventure.query.filter_by(details_id = sno).order_by().all()
    art=Art.query.filter_by(details_id = sno).order_by().all()
    shop=Shop.query.filter_by(details_id = sno).order_by().all()
    others=Others.query.filter_by(details_id = sno).order_by().all()
    return render_template('userdash.html', list = list , transport = transport ,local = localworkforce , stay = wheretostay , spices = spices , prod = spiceproducts , plant = plantation,pharma=pharmacy ,adventure=adventure, art = art ,shop = shop, others=others,language=session['language']) 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')

        if len(contact) != 10:
            flash('Invalid Mobile number. Please try with a different one.')
            return redirect(url_for('register'))

        try:
            existing_entry = Details.query.filter_by(contact=contact).first()

            if existing_entry:
                flash('Account exists with this number. Please try with a different one.')
                return redirect(url_for('register'))
        except Exception as e:
            flash(f"Error executing query: {e}")
            return redirect(url_for('register'))

        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash('Password combination does not match. Please try again.')
            return redirect(url_for('register'))

        email = request.form.get('email')

        if '@' not in email or '.' not in email:
            flash('Invalid email format. Please try again.')
            return redirect(url_for('register'))

        services = request.form.get('services')
        pic = request.files.get('file1')

        if not pic:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('register'))

        filename = secure_filename(pic.filename)[:15]

        entry = Details(
            name=name, address=address, contact=contact,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            email=email, services=services,
            date=datetime.now().date(), file=filename
        )

        # number = '+91'+contact
        # message = client.messages.create(
        #         body="Thank you for registering you will get a conformation after the admins verify your application.",
        #         from_=keys.twilio_number,
        #         to=number
        #     )
        try:
            img = Image.open(pic)
            db.session.add(entry)
            db.session.commit()
            img.save(os.path.join('static', 'uploads', filename), format=img.format, quality=70)
            return render_template('confirm.html')
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('register'))

    return render_template('register.html', language=session['language'])

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    user_contact = None
    
    if request.method == 'POST':
        user_contact = request.form.get('contact')
        user_password = request.form.get('password')

        details = Details.query.filter_by(contact=user_contact).first()
        try:
            if details and bcrypt.check_password_hash(details.password, user_password) and details.accept==1:
                session.permanent = True
                session['user'] = user_contact
                return redirect(url_for('userdash', sno=details.sno))
            elif details.accept!=1:
                flash("Account is not yet verified.")
                return redirect(url_for('signin'))
            else:
                flash('Invalid credentials. Please try again.')
                return redirect(url_for('signin'))
        except:
            flash('Please enter valid contact number and password.')
            return redirect(url_for('signin'))


    if 'user' in session and session['user'] == user_contact:
        return render_template('admin_dash.html', data=data)

    details_list = Details.query.filter_by(accept=1).order_by().all()
    return render_template('signin.html', list=details_list, language=session['language'])

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    error = None
    username = None

    if request.method == "POST":
        username = request.form.get("username", "")
        userpass = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password, userpass):
            session.permanent = True
            session['user'] = username
            return render_template('admin_dash.html', data=data)

        else:
            flash('Invalid credentials. Please try again.')
            error = data.get('error')
            return render_template('admin.html', data=data, error=error)

    if 'user' in session and session['user'] == username:
        return render_template('admin_dash.html', data=data)

    return render_template('admin.html', data=data, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('admin'))

@app.route("/signin_logout")
def signin_logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/admin_view/<int:sno>/<string:slug>' , methods = ["GET" , "POST"])
def admin_view(sno ,slug):
    if "user" in session:
        list = Details.query.filter_by(sno = sno ,slug=slug ,accept = None).first()           
        return render_template('admin_view.html' , list=list )
    else:
        return render_template('admin.html')

@app.route('/admin_dash')
def admin_dash():
    if "user" in session:
        return render_template('admin_dash.html')
    else:
        return render_template('admin.html')

@app.route('/admin_accept', methods=['POST'])
def admin_accept():
    try:
        row_id = request.form.get('row_id')
        details_instance = Details.query.filter_by(sno=row_id).first()
        details_instance.accept = 1
        service = details_instance.services
        db.session.commit()

        if service in ["Carpentary works", 'Plumbing services', 'Electrical works','Trekking Guide','Art and Craft','Mason','Painter','Goldsmith','Blacksmith']:
            new_local_workforce = LocalWorkforce(details_id=details_instance.sno)
            db.session.add(new_local_workforce)
        elif service == 'Spices outlet':
            spiceobj = Spices(details_id=details_instance.sno)
            db.session.add(spiceobj)
        elif service in ["Home stay", "Resorts", "Tent Camping", "Dormitories"]:
            new_wheretostay = WhereToStay(details_id=details_instance.sno)
            db.session.add(new_wheretostay)
        elif service == 'plantation':
            plantation = Plantation(details_id=details_instance.sno)
            db.session.add(plantation)
        elif service == 'Pharmacy Store':
            pharmacy_store = Pharmacy(details_id=details_instance.sno)
            db.session.add(pharmacy_store)
        elif service in ["Jeep Safari", 'Taxi service', 'Bike Rental', "Auto Rickshaw", "Ambulance", "Bike mechanic", "Car mechanic", 'Car Rental']:
            transport = Transportation(details_id=details_instance.sno)
            db.session.add(transport)
        elif service == 'Adventure Activity':
            adventure = Adventure(details_id=details_instance.sno)
            db.session.add(adventure)
        elif service == 'Art and Cultural':
            art = Art(details_id=details_instance.sno)
            db.session.add(art)
        elif service == 'Shop':
            shop = Shop(details_id=details_instance.sno)
            db.session.add(shop)
        elif service in '["Restaurant","Beauty Parlour","Hair Saloon" ,"Studio"]':
            others = Others(details_id=details_instance.sno)
            db.session.add(others)

        db.session.commit()
        
        return render_template('admin_accept.html')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in admin_accept: {e}")
        return render_template('admin_view.html')


@app.route('/admin_reject', methods=['POST'])     
def admin_reject():
    row_id2 = request.form.get('row_id2')
    try:
        row = Details.query.filter_by(sno = row_id2).first()
        filename = row.file
        if row:
            spices_to_delete=Spices.query.filter_by(details_id=row.sno).order_by().all()
            for spice in spices_to_delete:
                spiceproducts_to_delete = Spiceproducts.query.filter_by(details_id=spice.local_id).order_by().all()
                for spiceproduct in spiceproducts_to_delete:
                    db.session.delete(spiceproduct)
                for spice in spices_to_delete:
                    db.session.delete(spice)
            try:
                os.remove(os.path.join('static', 'uploads', filename))
            except:
                pass

            try:
                transportation_to_delete=Transportation.query.filter_by(details_id=row.sno).first()
                db.session.delete(transportation_to_delete)
            except:
                pass

            try:
                LocalWorkforce_to_delete=LocalWorkforce.query.filter_by(details_id=row.sno).first()
                db.session.delete(LocalWorkforce_to_delete)
            except:
                pass

            try:
                Pharmacy_to_delete=Pharmacy.query.filter_by(details_id=row.sno).first()
                db.session.delete(Pharmacy_to_delete)
            except:
                pass

            try:
                WhereToStay_to_delete=WhereToStay.query.filter_by(details_id=row.sno).first()
                db.session.delete(WhereToStay_to_delete)
            except:
                pass

            try:
                Plantation_to_delete=Plantation.query.filter_by(details_id=row.sno).first()
                db.session.delete(Plantation_to_delete)
            except:
                pass
            try:
                Adventure_to_delete=Adventure.query.filter_by(details_id=row.sno).first()
                db.session.delete(Adventure_to_delete)
            except:
                pass
            try:
                Art_to_delete=Art.query.filter_by(details_id=row.sno).first()
                db.session.delete(Art_to_delete)
            except:
                pass
            try:
                Shop_to_delete=Shop.query.filter_by(details_id=row.sno).first()
                db.session.delete(Shop_to_delete)
            except:
                pass
            try:
                other_to_delete=Others.query.filter_by(details_id=row.sno).first()
                db.session.delete(other_to_delete)
            except:
                pass           
            db.session.delete(row)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('admin_reject.html')
    
    return render_template('admin_reject.html')

@app.route('/approved_remove', methods=['POST'])    
def approved_remove():
    row_id2 = request.form.get('row_id2')
    try:
        row = Details.query.filter_by(sno = row_id2).first()
        filename = row.file
        if row:
            spices_to_delete=Spices.query.filter_by(details_id=row.sno).order_by().all()
            for spice in spices_to_delete:
                spiceproducts_to_delete = Spiceproducts.query.filter_by(details_id=spice.local_id).order_by().all()
                for spiceproduct in spiceproducts_to_delete:
                    db.session.delete(spiceproduct)
                for spice in spices_to_delete:
                    db.session.delete(spice)
            try:
                os.remove(os.path.join('static', 'uploads', filename))
            except:
                pass
            try:
                transportation_to_delete=Transportation.query.filter_by(details_id=row.sno).first()
                db.session.delete(transportation_to_delete)
            except:
                pass

            try:
                LocalWorkforce_to_delete=LocalWorkforce.query.filter_by(details_id=row.sno).first()
                db.session.delete(LocalWorkforce_to_delete)
            except:
                pass

            try:
                Pharmacy_to_delete=Pharmacy.query.filter_by(details_id=row.sno).first()
                db.session.delete(Pharmacy_to_delete)
            except:
                pass
            try:
                WhereToStay_to_delete=WhereToStay.query.filter_by(details_id=row.sno).first()
                db.session.delete(WhereToStay_to_delete)
            except:
                pass

            try:
                Plantation_to_delete=Plantation.query.filter_by(details_id=row.sno).first()
                db.session.delete(Plantation_to_delete)
            except:
                pass
            try:
                Adventure_to_delete=Adventure.query.filter_by(details_id=row.sno).first()
                db.session.delete(Adventure_to_delete)
            except:
                pass
            try:
                Art_to_delete=Art.query.filter_by(details_id=row.sno).first()
                db.session.delete(Art_to_delete)
            except:
                pass 
            try:
                Shop_to_delete=Shop.query.filter_by(details_id=row.sno).first()
                db.session.delete(Shop_to_delete)
            except:
                pass   
            try:
                other_to_delete=Others.query.filter_by(details_id=row.sno).first()
                db.session.delete(other_to_delete)
            except:
                pass  
            db.session.delete(row)
            db.session.commit()
    except Exception as e:
        db.session.rollback()   
    return render_template('approved_remove.html')


@app.route('/requests', methods=["GET" ,"POST"])
def requests():
    if "user" in session:
        list = Details.query.filter_by(accept = None).order_by().all()
        return render_template('requests.html', list=list)
    else:
        return render_template('admin.html')

@app.route('/approved_app', methods=["GET" ,"POST"])
def approved_app():
    if "user" in session:
        list = Details.query.filter_by(accept = 1).order_by().all()
        return render_template('approved_app.html', list=list)
    else:
        return render_template('admin.html')

@app.route('/approved_view/<int:sno>/<string:slug>' , methods = ["GET" , "POST"])
def approved_view(sno ,slug ):
    if "user" in session:
        list = Details.query.filter_by(sno = sno ,slug=slug ,accept = 1).first()                
        return render_template('approved_view.html' , list=list )
    else:
        return render_template('admin.html')

@app.route('/edit_pages', methods=["GET", "POST"])
def edit_pages():
    if "user" in session:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('desc')
            map_location = request.form.get('map')

            if 'files[]' not in request.files:
                flash('No file selected')
                return redirect(request.url)

            files = request.files.getlist('files[]')
            num = len(files)
            file_names = []

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_names.append(filename)
                    file.save(os.path.join('static', 'uploads', filename))

            if num <= 5:
                entry_data = {'name': name, 'description': description, 'map': map_location}
                for i in range(1, num + 1):
                    entry_data[f'img{i}'] = file_names[i - 1]

                entry = Places(**entry_data)
                db.session.add(entry)
                db.session.commit()
            else:
                flash('Only a maximum of 5 should be uploaded!')

        return render_template('edit_pages.html')
    else:
        return render_template('admin.html')
    
@app.route('/confirm')
def confirm():
    return render_template('confirm.html',language=session['language'])

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/tour')
def tour():
    list = Places.query.filter_by().order_by().all()
    return render_template('tour.html' , list = list,language=session['language'])

@app.route('/place/<int:id>', methods = ["GET" , "POST"])
def place(id):
    list = Places.query.filter_by(id = id ).first()                
    return render_template('place.html' , list = list,language=session['language'])

@app.route('/added_places', methods=["GET" ,"POST"])
def added_places():
    list = Places.query.filter_by().order_by().all()
    return render_template('addedplaces.html', list=list,language=session['language'])

@app.route('/addedplace_detail/<int:id>' , methods = ["GET" , "POST"])
def addedplace_detail(id):
    list = Places.query.filter_by(id = id ).first()                
    return render_template('addedplace_detail.html' , list=list,language=session['language'] )

@app.route('/place_remove', methods=['POST'])    
def place_remove():
    row_id2 = request.form.get('row_id2')
    row = Places.query.filter_by(id = row_id2).first()
    img1 = row.img1
    img2 = row.img2
    img3 = row.img3
    img4 = row.img4
    img5 = row.img5
    if row:
        try:
            os.remove(os.path.join('static', 'uploads', img1))
            os.remove(os.path.join('static', 'uploads', img2))
            os.remove(os.path.join('static', 'uploads', img3))
            os.remove(os.path.join('static', 'uploads', img4))
            os.remove(os.path.join('static', 'uploads', img5))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return redirect(url_for('added_places'))


@app.route('/where_to_stay')
def where_to_stay():
    list = Details.query.filter_by(accept = 1).order_by().all()
    return render_template('where_to_stay.html', list = list,language=session['language'])


@app.route('/dormitories')
def dormitories():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = WhereToStay.query.filter_by().order_by().all()
    return render_template('dormitories.html', info = info , list = list,language=session['language'] )

@app.route('/view_dormitories/<int:id>')
def view_dormitories(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_dormitories.html' , list = list , info = info,language=session['language'])


@app.route('/home_stay')
def home_stay():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = WhereToStay.query.filter_by().order_by().all()
    return render_template('home_stay.html', info = info , list = list,language=session['language'] )

@app.route('/view_homestay/<int:id>')
def view_homestay(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_homestay.html' , list = list , info = info,language=session['language'])


@app.route('/resorts')
def resorts():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = WhereToStay.query.filter_by().order_by().all()
    return render_template('resorts.html', info = info , list = list,language=session['language'] )

@app.route('/view_resorts/<int:id>')
def view_resorts(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_resorts.html' , list = list , info = info,language=session['language'])

@app.route('/tent_camping')
def tent_camping():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = WhereToStay.query.filter_by().order_by().all()
    return render_template('tent_camping.html', info = info , list = list,language=session['language'] )

@app.route('/view_tent/<int:id>')
def view_tent_camping(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_tent.html' , list = list , info = info,language=session['language'])

@app.route('/local_workforce')
def local_workforce():
    list = Details.query.filter_by(accept = 1).order_by().all()
    return render_template('local_workforce.html' , list = list,language=session['language'])

@app.route('/carpendry_work')
def carpendry_work():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('carpendry.html', info = info , list = list,language=session['language'] )

@app.route('/view_carpendry/<int:id>')
def view_carpendry_work(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_carpendry.html' , list = list , info = info,language=session['language'])

@app.route('/plumbers')
def plumbers():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('plumbers.html', info = info , list = list,language=session['language'] )

@app.route('/view_plumbers/<int:id>')
def view_plumbers(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_plumbers.html' , list = list , info = info,language=session['language'])


@app.route('/Electrical')
def Electrical():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('electricians.html', info = info , list = list,language=session['language'] )

@app.route('/view_Electrical/<int:id>')
def view_Electrical(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_electricians.html' , list = list , info = info,language=session['language'])


@app.route('/Trekking')
def Trekking():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('Trekking.html', info = info , list = list,language=session['language'] )

@app.route('/view_Trekking/<int:id>')
def view_Trekking(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_Trekking.html' , list = list , info = info,language=session['language'])

@app.route('/artandCraft')
def artandCraft():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('artandCraft.html', info = info , list = list,language=session['language'] )

@app.route('/view_artandCraft/<int:id>')
def view_artandCraft(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_artandCraft.html' , list = list , info = info,language=session['language'])



@app.route('/mason')
def mason():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('mason.html', info = info , list = list,language=session['language'] )

@app.route('/view_mason/<int:id>')
def view_mason(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_mason.html' , list = list , info = info,language=session['language'])



@app.route('/painter')
def painter():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('painter.html', info = info , list = list,language=session['language'] )

@app.route('/view_painter/<int:id>')
def view_painter(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_painter.html' , list = list , info = info,language=session['language'])



@app.route('/goldsmith')
def goldsmith():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('goldsmith.html', info = info , list = list,language=session['language'] )

@app.route('/view_goldsmith/<int:id>')
def view_goldsmith(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_goldsmith.html' , list = list , info = info,language=session['language'])



@app.route('/blacksmith')
def blacksmith():
    list = Details.query.filter_by( accept = 1).order_by().all()
    info = LocalWorkforce.query.filter_by().order_by().all()
    return render_template('blacksmith.html', info = info , list = list,language=session['language'] )

@app.route('/view_blacksmith/<int:id>')
def view_blacksmith(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = id)
    return render_template('view_blacksmith.html' , list = list , info = info,language=session['language'])



@app.route('/view_localworkforce/<int:sno>', methods=['GET', 'POST'])
def view_localworkforce(sno):
    list = Details.query.filter_by(sno = sno , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = sno)  
    return render_template('view_localworkforce.html' , list = list, info = info,language=session['language'] )


@app.route('/plantation_crops')
def plantation_crops():
    list1 = Plantation.query.filter_by().order_by().all()
    return render_template('plantation_crops.html',list=list1,language=session['language'])

@app.route('/spices')
def spices():
    list = Details.query.filter_by().order_by().all()
    return render_template('spices.html',list=list,language=session['language'])

@app.route('/spices_view')
def spices_view():
    lis1=Details.query.filter_by(services='Spices outlet').order_by().all()
    lis2 = Spices.query.filter_by().order_by().all()
    lis3=Spiceproducts.query.filter_by().order_by().all()
    lis4 = Spiceproducts.query.with_entities(Spiceproducts.product).order_by().all()
    product_list = [item.product for item in lis4]
    product_list=list(set(product_list))
    return render_template('spices_view.html',lis1=lis1,lis2=lis2,lis3=lis3,product_list=product_list,language=session['language'])

@app.route('/view_spices/<int:sno>', methods=['GET', 'POST'])
def view_spices(sno):
    lis1 = Details.query.filter_by(sno = sno , accept = 1)
    lis2 = Spices.query.filter_by(details_id = sno)  
    lis3=Spiceproducts.query.filter_by().order_by().all()
    return render_template('view_spices.html' ,lis2=lis2,lis1=lis1,lis3=lis3,language=session['language'] )

@app.route('/addspiceproduct/<int:sno>', methods=['GET', 'POST'])
def addspiceproduct(sno):
    if(request.method == 'POST'):
        product=request.form.get('product')
        price=request.form.get('price')
        details_instance = Details.query.filter_by(sno=sno).first()
        details_instance_spices = Spices.query.filter_by(details_id=details_instance.sno).first()
        spiceobj = Spiceproducts(product=product,price=price,details_id=details_instance_spices.local_id)
        db.session.add(spiceobj)
        db.session.commit()

    list = Details.query.filter_by(sno=sno , accept = 1).order_by().all()
    list1=Spices.query.filter_by().order_by().all()
    list2=Spiceproducts.query.filter_by().order_by().all()
    return render_template('add_spices.html', list = list ,list1=list1, list2=list2,language=session['language'])


@app.route('/deletespiceproduct/<int:sno>/<int:id>', methods=['GET', 'POST'])
def deletespiceproduct(sno , id):
    if(request.method == 'POST'):
        deletespice = Spiceproducts().query.filter_by( local_id = id).first()
        db.session.delete(deletespice)
        db.session.commit()
    return redirect(url_for('addspiceproduct', sno=sno,language=session['language'])) 
    

@app.route('/transport')
def transport():
    list1 = Details.query.filter_by(accept = 1).order_by().all()
    trans=Details.query.with_entities(Details.services).order_by().all()
    product_list = [item.services for item in trans]
    product_list=list(set(product_list))
    return render_template('transport.html',language=session['language'], list = list1, list2=product_list)

@app.route('/transport_view/<int:sno>', methods=["GET" ,"POST"])
def transport_view(sno):
    t = Details.query.filter_by(sno=sno , accept = 1).first()
    list = Details.query.filter_by(services = t.services , accept = 1)
    return render_template('transport_view.html', list=list,language=session['language'])

@app.route('/transport_detail_view/<int:sno>', methods=["GET" ,"POST"])
def transport_detail_view(sno):
    list = Details.query.filter_by(sno = sno , accept = 1)
    list1=Transportation.query.filter_by(details_id = sno).first()
    return render_template('view_transportation.html', list=list,list1=list1,language=session['language'])

@app.route('/transport_view/busview')
def busview():
    return render_template('bus.html',language=session['language'])

@app.route('/image/<string:img>', methods=['GET', 'POST'])
def image(img):
    return render_template('image.html' , img = img )

@app.route('/<text>', methods=['GET', 'POST'])
def all_routes(text):
    return redirect(url_for('index'))

@app.route('/eservices', methods=['GET', 'POST'])
def eservices():
    list = Eservices.query.filter_by().order_by().all()
    return render_template('eservices.html', list = list)


@app.route('/addeservices', methods=['GET', 'POST'])
def addeservices():
    if request.method == 'POST':
        name = request.files.get('name')
        link = request.form.get('link')
        
        entry = Eservices(name=name, link=link)
        try:
            db.session.add(entry)
            db.session.commit()
            flash('eservices is added. Click + button to add more')
            return redirect(url_for('addeservices'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addeservices'))

    return render_template('addeservices.html',language=session['language'])

@app.route('/addedeservices', methods=['GET','POST'])
def addedeservices():
    list = Eservices.query.order_by().all()
    return render_template('addedeservices.html',list=list,language=session['language'])

@app.route('/eservices_remove', methods=['POST'])    
def eservices_remove():
    row_id2 = request.form.get('row_id2')
    row = eservices.query.filter_by(id = row_id2).first()
    
    db.session.delete(row)
    db.session.commit()     
    return redirect(url_for('addedeservices',language=session['language']))


@app.route('/forgotpass', methods=['GET', 'POST'])
def forgotpass():
    return render_template('forgot.html',language=session['language'])

@app.route('/forgotcheck', methods=['GET', 'POST'])
def forgotcheck():
    if(request.method == 'POST'):
        email=request.form.get('email')
        mobile=request.form.get('mobile')
        t = Details.query.filter_by(email=email , accept = 1).first()
        if t:
            u=Details.query.filter_by(contact=mobile , accept = 1).first()
            if u:
                if t.sno==u.sno:
                    return render_template('forgotnumb.html',no=t.sno,language=session['language'])
                else:
                    flash('Phonenumber and email does not match! try again.')
                    return redirect(url_for('forgotcheck'))
                # return render_template('forgotnumb.html',list1=t)
            else:
                flash('Mobile number is incorrect! Try Again.')
        else:
            flash('Email does not Exist! try again.')
            return redirect(url_for('forgotcheck'))
    return render_template('forgot.html',language=session['language'])

@app.route('/forgotemail/<int:sno>', methods=['GET', 'POST'])
def forgotemail(sno):
    if(request.method == 'POST'):
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        if password1==password2:
            # t = Details.query.get(sno)
            t=db.session.get(Details, sno)
            
            t.password=bcrypt.generate_password_hash(password1).decode('utf-8')
            db.session.commit()
            subject="Hi "+t.name
            sender1="noreply@app.com"
            msg= Message(subject,sender=sender1,recipients=[t.email])
            # subject="Your application for "+details_instance.services+" in Pallivasal website is Accepted"
            msg.body="Your password to login the pallivasal website is changed successfully.\nif not done by you, please contact us.\n\n\nRegards,\nPallivasal Gramapanchayath\nMail: explorepallivasalgp@gmail.com\nWebsite: https://explorepallivasalgp.org/" 
            try:
                mail.send(msg)
                return render_template('emailsend.html')
            except :
                pass
            return render_template('emailsend.html')
        else:
            flash('Password does not match.')
            return render_template('forgotnumb.html',no=sno,language=session['language'])

    return render_template('forgotnumb.html',no=sno)

@app.route('/addHealthcare', methods=['GET','POST'])
def addHealthcare():
    if(request.method == 'POST'):
        name=request.form.get('name')
        map=request.form.get('map')
        pic = request.files.get('img')
        types = request.form.get('hospital-type')
        category = request.form.get('hospital-catogery')
        description = request.form.get('description')
        contact = request.form.get('contact')
        place = request.form.get('place')
        time = request.form.get('workingtime')
        if not pic:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addedHealthcare'))

        filename = secure_filename(pic.filename)[:15]

        entry = HealthCare(name=name,img=filename,map=map,types = types , category = category,description=description , contact2=contact,place=place,time= time)
        db.session.add(entry)
        db.session.commit()
        pic.save(os.path.join('static', 'uploads', filename))
        flash('Hospital '+ name+' added. click + button to add more')
        return render_template('addHealthcare.html',language=session['language'])
    else:
        return render_template('addHealthcare.html',language=session['language'])
    
@app.route('/addedhospital_detail/<int:id>' , methods = ["GET" , "POST"])
def addedhospital_detail(id):
    list = HealthCare.query.filter_by(id = id ).first()                
    return render_template('addedplace_detail.html' , list=list,x=1,language=session['language'] )

@app.route('/addedHealthcare', methods=['GET','POST'])
def addedHealthcare():
    list=HealthCare.query.filter_by().order_by().all()
    return render_template('adminviewHealthcare.html',list=list,language=session['language'])

@app.route('/Hospital_remove', methods=['GET','POST'])
def Hospital_remove():
    rid = request.form.get('id')
    row = HealthCare.query.filter_by(id = rid).first()
    img = row.img
    if row:
        try:
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return redirect(url_for('addedHealthcare',language=session['language']))

@app.route('/Hospitals', methods=['GET','POST'])
def Hospitals():
    list=HealthCare.query.filter_by().order_by().all()
    return render_template('view_hospitals.html',list=list,language=session['language'])

@app.route('/hospitalview/<int:id>', methods=['GET','POST'])
def hospitalview(id):
    list=HealthCare.query.filter_by(id=id)
    return render_template('hospitalview.html',info=list,language=session['language'])
  

@app.route('/Pharmacyfn', methods=['GET','POST'])
def Pharmacyfn():
    list=Pharmacy.query.filter_by().order_by().all()
    return render_template('Pharmacy.html',list=list,language=session['language'])


@app.route('/pharmacyview/<int:id>', methods = ["GET" , "POST"])
def pharmacyview(id):
    list = Pharmacy.query.filter_by(local_id = id ).first()                
    return render_template('pharmacyview.html' , list = list,language=session['language'])

@app.route('/adventure', methods=['GET','POST'])
def adventure():
    list = Adventure.query.filter_by().order_by().all()  
    return render_template('adventure.html',list=list,language=session['language'])

@app.route('/view_adventure/<int:id>', methods = ["GET" , "POST"])
def view_adventure(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = Adventure.query.filter_by(details_id = id)        
    return render_template('view_adventure.html' , list = list ,info = info,language=session['language'])

@app.route('/art', methods=['GET','POST'])
def art():
    list = Art.query.filter_by().order_by().all()  
    return render_template('art.html',list=list,language=session['language'])

@app.route('/view_art/<int:id>', methods = ["GET" , "POST"])
def view_art(id):
    list = Art.query.filter_by(details_id = id)
    for_contact = Details.query.filter_by(sno = id , accept = 1)       
    return render_template('view_art.html' ,info = for_contact , list = list,language=session['language'])

@app.route('/bank', methods=['GET','POST'])
def bank():
    list = Bank.query.filter_by().order_by().all()  
    return render_template('banks.html', list = list,language=session['language'])

@app.route('/addmore', methods=['GET','POST'])
def addmore():
    return render_template('addmore.html',language=session['language'])

@app.route('/addbank', methods=['GET','POST'])
def addbank():
    if(request.method == 'POST'):
        name=request.form.get('name')
        map=request.form.get('map')
        contact = request.form.get('contact')

        entry = Bank(name=name,map=map,contact=contact)
        db.session.add(entry)
        db.session.commit()
        flash('Bank '+ name+' added. click + button to add more')
        return render_template('addbank.html')
    else:
        return render_template('addbank.html')


@app.route('/other_services', methods=['GET','POST'])
def other_services():
    return render_template('other_services.html',language=session['language'])


@app.route('/restaurants', methods=['GET','POST'])
def restaurants():
    desired_services = ['Restaurant']
    result = db.session.query(Others).join(Details).filter(
        Details.accept == 1,
        Details.services.in_(desired_services)
    ).order_by().all()
    return render_template('restaurants.html', result = result,language=session['language'])

@app.route('/view_restaurant/<int:id>', methods=['GET','POST'])
def view_restaurant(id):
    info = Others.query.filter_by(local_id = id).first()
    return render_template('view_restaurant.html' , info = info,language=session['language'])

@app.route('/hair_saloons', methods=['GET','POST'])
def hair_saloons():
    desired_services = ['Hair Saloon', 'Beauty Parlour']
    result = db.session.query(Others).join(Details).filter(
        Details.accept == 1,
        Details.services.in_(desired_services)
    ).order_by().all()
    return render_template('hair_saloons.html',result = result,language=session['language'])


@app.route('/view_hair_saloon/<int:id>', methods=['GET','POST'])
def view_hair_saloon(id):
    info = Others.query.filter_by(local_id = id).first()
    return render_template('view_hair_saloon.html' , info = info,language=session['language'])

@app.route('/studio', methods=['GET','POST'])
def studio():
    desired_services = ['Studio']
    result = db.session.query(Others).join(Details).filter(
        Details.accept == 1,
        Details.services.in_(desired_services)
    ).order_by().all()
    return render_template('studio.html', result = result,language=session['language'])

@app.route('/view_studio/<int:id>', methods=['GET','POST'])
def view_studio(id):
    info = Others.query.filter_by(local_id = id).first()
    return render_template('view_studio.html',info = info,language=session['language'])

@app.route('/shops', methods=['GET','POST'])
def shops():
    list = Shop.query.filter_by().order_by().all()  
    return render_template('shops.html' , list = list,language=session['language'])

@app.route('/view_shop/<int:id>', methods=['GET','POST'])
def view_shop(id):
    list = Shop.query.filter_by(details_id = id).first()    
    return render_template('view_shop.html', list=list,language=session['language'])

@app.route('/addedbank', methods=['GET','POST'])
def addedbank():
    list = Bank.query.filter_by().order_by().all()
    return render_template('addedbank.html',list=list,language=session['language'])

@app.route('/bank_remove', methods=['POST'])    
def bank_remove():
    row_id2 = request.form.get('row_id2')
    row = Bank.query.filter_by(id = row_id2).first()
    db.session.delete(row)
    db.session.commit()     
    return redirect(url_for('addedbank'))

@app.route('/addproject', methods=['GET', 'POST'])
def addproject():
    if request.method == 'POST':
        img = request.files.get('img')
        description = request.form.get('desc')
        
        if not img:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addproject'))

        filename = secure_filename(img.filename)
        if not filename:
            flash('Invalid image filename. Please try again.')
            return redirect(url_for('addproject'))

        try:
            img_path = os.path.join('static', 'uploads', filename)
            img = Image.open(img)
            img.save(img_path)
        except Exception as e:
            flash(f"Error saving image: {e}")
            return redirect(url_for('addproject'))

        entry = Project(img=filename, desc=description)
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Project is added. Click + button to add more')
            return redirect(url_for('addproject'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addproject'))

    return render_template('addproject.html',language=session['language'])

@app.route('/addedproject', methods=['GET','POST'])
def addedproject():
    list = Project.query.order_by().all()
    return render_template('addedproject.html',list=list,language=session['language'])

@app.route('/project_remove', methods=['POST'])    
def project_remove():
    row_id2 = request.form.get('row_id2')
    row = Project.query.filter_by(id = row_id2).first()
    if row:
        try:
            img = row.img
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return redirect(url_for('addedproject',language=session['language']))

@app.route('/publiccenters', methods=['GET','POST'])
def publiccenters():
    return render_template('publiccenters.html',language=session['language'])

####rationshop
@app.route('/rationshop', methods=['GET','POST'])
def rationshop():
    list = CivilSupply.query.filter_by(type='Ration').order_by().all()
    return render_template('rationshop.html', list = list,language=session['language'])


@app.route('/addrationshop', methods=['GET', 'POST'])
def addrationshop():
    if request.method == 'POST':
        type = "Ration"
        name = request.form.get('name')
        map = request.form.get('map')
        img = request.files.get('file')
        contact = request.form.get('contact')
        wt = request.form.get('wt')
        
        if not img:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addrationshop'))

        filename = secure_filename(img.filename)
        if not filename:
            flash('Invalid image filename. Please try again.')
            return redirect(url_for('addrationshop'))

        try:
            img_path = os.path.join('static', 'uploads', filename)
            img = Image.open(img)
            img.save(img_path)
        except Exception as e:
            flash(f"Error saving image: {e}")
            return redirect(url_for('addrationshop'))

        entry = CivilSupply(type = type , name = name , map = map , img=filename , contact = contact , wt = wt)
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Ration shop is added. Click + button to add more')
            return redirect(url_for('addrationshop'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addrationshop'))

    return render_template('addrationshop.html',language=session['language'])

@app.route('/addedrationshop', methods=['GET','POST'])
def addedrationshop():
    list = CivilSupply.query.filter_by(type='Ration').order_by().all()
    return render_template('addedrationshop.html',list=list,language=session['language'])

@app.route('/rationshop_remove', methods=['POST'])    
def rationshop_remove():
    row_id2 = request.form.get('row_id2')
    row = rationshop.query.filter_by(id = row_id2).first()
    if row:
        try:
            img = row.img
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('addedrationshop',language=session['language']))

@app.route('/view_rationshop/<int:id>')
def view_rationshop(id):
    info = CivilSupply.query.filter_by(id = id)
    return render_template('view_rationshop.html' ,info = info,language=session['language'])


#supplyco
@app.route('/supplyco', methods=['GET','POST'])
def supplyco():
    list = CivilSupply.query.filter_by(type='Supplyco').order_by().all()
    return render_template('supplyco.html', list = list,language=session['language'])


@app.route('/addsupplyco', methods=['GET', 'POST'])
def addsupplyco():
    if request.method == 'POST':
        type = "Supplyco"
        name = request.form.get('name')
        map = request.form.get('map')
        img = request.files.get('file')
        contact = request.form.get('contact')
        wt = request.form.get('wt')
        
        if not img:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addsupplyco'))

        filename = secure_filename(img.filename)
        if not filename:
            flash('Invalid image filename. Please try again.')
            return redirect(url_for('addsupplyco'))

        try:
            img_path = os.path.join('static', 'uploads', filename)
            img = Image.open(img)
            img.save(img_path)
        except Exception as e:
            flash(f"Error saving image: {e}")
            return redirect(url_for('addsupplyco'))

        entry = CivilSupply(type = type , name = name , map = map , img=filename , contact = contact , wt = wt)
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Supplyco is added. Click + button to add more')
            return redirect(url_for('addsupplyco'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addsupplyco'))

    return render_template('addsupplyco.html',language=session['language'])

@app.route('/addedsupplyco', methods=['GET','POST'])
def addedsupplyco():
    list = CivilSupply.query.filter_by(type='Supplyco').order_by().all()
    return render_template('addedsupplyco.html',list=list,language=session['language'])

@app.route('/supplyco_remove', methods=['POST'])    
def supplyco_remove():
    row_id2 = request.form.get('row_id2')
    row = CivilSupply.query.filter_by(id = row_id2).first()
    if row:
        try:
            img = row.img
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('addedsupplyco',language=session['language']))

@app.route('/view_supplyco/<int:id>')
def view_supplyco(id):
    info = CivilSupply.query.filter_by(id = id)
    return render_template('view_supplyco.html' ,info = info,language=session['language'])

##publicdepartments
@app.route('/publicdepartments', methods=['GET','POST'])
def publicdepartments():
    list = Public.query.filter_by().order_by(Public.name).all()  
    return render_template('publicdepartments.html', list = list,language=session['language'])

@app.route('/addpublicdepartments', methods=['GET','POST'])
def addpublicdepartments():
    if(request.method == 'POST'):
        name=request.form.get('name')
        contact = request.form.get('contact')
        map=request.form.get('map')

        entry = Public(name=name,contact=contact,map=map)
        db.session.add(entry)
        db.session.commit()
        flash('public department '+ name+' added. click + button to add more')
        return render_template('addpublicdepartments.html',language=session['language'])
    else:
        return render_template('addpublicdepartments.html',language=session['language'])

@app.route('/addedpublicdepartments', methods=['GET','POST'])
def addedpublicdepartments():
    list = Public.query.filter_by().order_by().all()
    return render_template('addedpublicdepartments.html',list=list)

@app.route('/publicdepartments_remove', methods=['POST'])    
def publicdepartments_remove():
    row_id2 = request.form.get('row_id2')
    row = Public.query.filter_by(id = row_id2).first()
    db.session.delete(row)
    db.session.commit()     
    return redirect(url_for('addedpublicdepartments',language=session['language']))

##worship
@app.route('/worship', methods=['GET','POST'])
def worship():
    list = Worship.query.filter_by().order_by().all()
    return render_template('worship.html', list = list,language=session['language'])


@app.route('/addworship', methods=['GET', 'POST'])
def addworship():
    if request.method == 'POST':
        name = request.form.get('name')
        map = request.form.get('map')
        img = request.files.get('file')
        
        if not img:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addworship'))

        filename = secure_filename(img.filename)
        if not filename:
            flash('Invalid image filename. Please try again.')
            return redirect(url_for('addworship'))

        try:
            img_path = os.path.join('static', 'uploads', filename)
            img = Image.open(img)
            img.save(img_path)
        except Exception as e:
            flash(f"Error saving image: {e}")
            return redirect(url_for('addworship'))

        entry = Worship(name = name , map = map , img=filename )
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Worship center is added. Click + button to add more')
            return redirect(url_for('addworship'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addworship'))

    return render_template('addworship.html',language=session['language'])

@app.route('/addedworship', methods=['GET','POST'])
def addedworship():
    list = Worship.query.filter_by().order_by().all()
    return render_template('addedworship.html',list=list,language=session['language'])

@app.route('/worship_remove', methods=['POST'])    
def worship_remove():
    row_id2 = request.form.get('row_id2')
    row = Worship.query.filter_by(id = row_id2).first()
    if row:
        try:
            img = row.img
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('addedworship',language=session['language']))

@app.route('/aboutus', methods=['GET','POST'])
def aboutus():
    return render_template('aboutus.html')

@app.route('/history', methods=['GET','POST'])
def history():
    return render_template('history.html')

@app.route('/gallery', methods=['GET','POST'])
def gallery():
    list = Gallery.query.filter_by().order_by().all()
    return render_template('gallery.html', list = list,language=session['language'])

@app.route('/addgallery', methods=['GET','POST'])
def addgallery():
    if request.method == 'POST':
        name = request.form.get('name')
        img = request.files.get('file')
        
        if not img:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('addgallery'))

        filename = secure_filename(img.filename)
        if not filename:
            flash('Invalid image filename. Please try again.')
            return redirect(url_for('addgallery'))

        try:
            img_path = os.path.join('static', 'uploads', filename)
            img = Image.open(img)
            img.save(img_path)
        except Exception as e:
            flash(f"Error saving image: {e}")
            return redirect(url_for('addgallery'))

        entry = Gallery(name = name, img=filename )
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Image is added. Click + button to add more')
            return redirect(url_for('addgallery'))
        except Exception as e:
            flash(f"Error committing changes: {e}")
            return redirect(url_for('addgallery'))

    return render_template('addgallery.html',language=session['language'])


@app.route('/addedgallery', methods=['GET','POST'])
def addedgallery():
    list = Gallery.query.filter_by().order_by().all()
    return render_template('addedgallery.html',list=list,language=session['language'])


@app.route('/gallery_remove', methods=['POST'])    
def gallery_remove():
    row_id2 = request.form.get('row_id2')
    row = Gallery.query.filter_by(id = row_id2).first()
    if row:
        try:
            img = row.img
            os.remove(os.path.join('static', 'uploads', img))
        except:
            pass
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('addedgallery',language=session['language']))

@app.route('/auditorium', methods=['GET','POST'])
def auditorium():
    return render_template('auditorium.html')

@app.route('/hiringservices', methods=['GET','POST'])
def hiringservices():
    return render_template('hiringservices.html')

@app.route('/view_hiringservices', methods=['GET','POST'])
def view_hiringservices():
    return render_template('view_hiringservices.html')

##add admin
@app.route('/admin-addadmin-pallivasal', methods=['GET','POST'])
def addadmin():
    if(request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        entry = Admin(username = username , password = hashed_password)
            
        db.session.add(entry)
        db.session.commit()
        
    return render_template('admin_add.html')

if __name__ == ("__main__"):
    app.run(debug=True)
