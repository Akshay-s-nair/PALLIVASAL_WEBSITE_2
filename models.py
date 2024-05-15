from db import db
from slugify import slugify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session


class Details(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(14), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    services = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=True)
    slug = db.Column(db.String(80), nullable=True)
    file = db.Column(db.Text, nullable=False)
    accept = db.Column(db.Integer)
    
    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

db.event.listen(Details.name, 'set', Details.slugify, retval=False)
        
        
class Places(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=False)
    img1 = db.Column(db.Text , nullable=True)
    img2 = db.Column(db.Text , nullable=True)
    img3 = db.Column(db.Text , nullable=True)
    img4 = db.Column(db.Text , nullable=True)
    img5 = db.Column(db.Text , nullable=True)
    map =  db.Column(db.String(40) , nullable=True)


class LocalWorkforce(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    whatsapp_number = db.Column(db.String(80), nullable=True, default=None)
    years_of_exp = db.Column(db.String(80), nullable=True, default=None)
    technical_qualifications = db.Column(db.String(80), nullable=True, default=None)
    remuneration_details = db.Column(db.String(80), nullable=True, default=None)
    img = db.Column(db.Text , nullable=True)


    details = relationship("Details", back_populates="local_workforce")

Details.local_workforce = relationship("LocalWorkforce", order_by=LocalWorkforce.local_id, back_populates="details")

class Spices(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    name = db.Column(db.String(80), nullable=True, default=None)
    location = db.Column(db.String(80), nullable=True, default=None)
    contact2 = db.Column(db.String(80), nullable=True, default=None)
    img = db.Column(db.Text , nullable=True)

    details = relationship("Details", back_populates="spices")

Details.spices = relationship("Spices", order_by=Spices.local_id, back_populates="details")

class Spiceproducts(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('spices.local_id'))
    product = db.Column(db.String(80), nullable=True, default=None)
    price = db.Column(db.String(80), nullable=True, default=None)

    spices = relationship("Spices", back_populates="spiceproducts")

Spices.spiceproducts = relationship("Spiceproducts", order_by=Spiceproducts.local_id, back_populates="spices")



class WhereToStay(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    name = db.Column(db.String(80), nullable=True, default=None)
    location = db.Column(db.String(80), nullable=True, default=None)
    description = db.Column(db.String(80), nullable=True, default=None)
    contact2 = db.Column(db.String(80), nullable=True, default=None)
    facilities = db.Column(db.String(80), nullable=True, default=None)
    no_of_rooms = db.Column(db.String(80), nullable=True, default=None)
    services = db.Column(db.String(80), nullable=True, default=None)
    img1 = db.Column(db.Text, nullable=True, default=None)


    details = relationship("Details", back_populates="where_to_stay")

Details.where_to_stay = relationship("WhereToStay", order_by=WhereToStay.local_id, back_populates="details")


class Transportation(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    cost = db.Column(db.String(10), nullable=True, default=None)
    Trip_available = db.Column(db.String(10), nullable=True, default=None)
    Pick_up_and_Drop = db.Column(db.String(10), nullable=True, default=None)
    Duration = db.Column(db.String(80), nullable=True, default=None)
    vehicle = db.Column(db.String(80), nullable=True, default=None)
    no_of_persons = db.Column(db.String(80), nullable=True, default=None)
    Things_to_carry = db.Column(db.String(80), nullable=True, default=None)
    img = db.Column(db.Text, nullable=True, default=None)


    details = relationship("Details", back_populates="transportation")

Details.transportation = relationship("Transportation", order_by=Transportation.local_id, back_populates="details")

class Plantation(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    name = db.Column(db.String(80), nullable=True, default=None)
    address = db.Column(db.String(80), nullable=True, default=None)
    location = db.Column(db.String(80), nullable=True, default=None)
    contact = db.Column(db.String(80), nullable=True, default=None)
    Crops = db.Column(db.String(80), nullable=True, default=None)
    img = db.Column(db.Text , nullable=True)

    details = relationship("Details", back_populates="plantation")

Details.plantation = relationship("Plantation", order_by=Plantation.local_id, back_populates="details")


class Admin(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class HealthCare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    img = db.Column(db.Text , nullable=True)
    map =  db.Column(db.String(50) , nullable=True)

class Pharmacy(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    name = db.Column(db.String(80), nullable=True, default=None)
    address = db.Column(db.String(80), nullable=True, default=None)
    location = db.Column(db.String(80), nullable=True, default=None)
    contact = db.Column(db.String(80), nullable=True, default=None)
    type = db.Column(db.String(80), nullable=True, default=None)
    img = db.Column(db.Text , nullable=True)

    details = relationship("Details", back_populates="pharmacy")

Details.pharmacy = relationship("Pharmacy", order_by=Pharmacy.local_id, back_populates="details")

class Adventure(db.Model):
    local_id = db.Column(db.Integer, primary_key=True)
    details_id = db.Column(db.Integer, db.ForeignKey('details.sno'))
    name = db.Column(db.String(80), nullable=True, default=None)
    location = db.Column(db.String(80), nullable=True, default=None)
    description = db.Column(db.String(80), nullable=True, default=None)
    contact2 = db.Column(db.String(80), nullable=True, default=None)
    tariff = db.Column(db.String(80), nullable=True, default=None)
    img1 = db.Column(db.Text , nullable=True)


    details = relationship("Details", back_populates="adventure")

Details.adventure = relationship("Adventure", order_by=Adventure.local_id, back_populates="details")