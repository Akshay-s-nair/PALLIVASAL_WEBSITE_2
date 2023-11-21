from db import db
from slugify import slugify

class Details(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(14), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    confirm = db.Column(db.String(20), nullable=False)
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
    description = db.Column(db.String(40), nullable=False)
    img1 = db.Column(db.Text , nullable=True)
    img2 = db.Column(db.Text , nullable=True)
    img3 = db.Column(db.Text , nullable=True)
    img4 = db.Column(db.Text , nullable=True)
    img5 = db.Column(db.Text , nullable=True)
    map =  db.Column(db.String(40) , nullable=True)


