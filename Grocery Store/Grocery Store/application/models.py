from application.database import db
from datetime import datetime

class Categories(db.Model):
    __tablename__ = 'Categories'
    C_ID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    C_name = db.Column(db.String, nullable=False , unique=True)
    products = db.relationship("Products",back_populates="category",cascade='all, delete-orphan', lazy=True)
    
class Products(db.Model):
    __tablename__ = 'Products'
    P_ID = db.Column(db.Integer,autoincrement=True, primary_key=True, unique=True, nullable=False)
    C_ID = db.Column(db.Integer, db.ForeignKey("Categories.C_ID",ondelete='CASCADE') ,nullable=False )
    P_name = db.Column(db.String , nullable=False)
    unit = db.Column(db.String )
    price_per_unit = db.Column(db.Integer , nullable=False)
    manf_exp_Date = db.Column(db.String , nullable=True)
    umo_id = db.Column(db.Integer , db.ForeignKey("uom.uom_id",ondelete='CASCADE'),nullable=False)
    avable_qunty = db.Column(db.Integer)
    remaining_quantity = db.Column(db.Integer, nullable=False)
    category = db.relationship("Categories", back_populates="products")
    

class Orders(db.Model):
    __tablename__ = 'Orders'
    orderID = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('Users.userID'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class OrderDetails(db.Model):
    __tablename__ = 'OrderDetails'
    detailID = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    orderID = db.Column(db.Integer, db.ForeignKey('Orders.orderID'), nullable=False)
    productID = db.Column(db.Integer, db.ForeignKey('Products.P_ID'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)



class uom(db.Model):
    __tablename__ = 'uom'
    uom_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    uom_name = db.Column(db.String, nullable=False)
    

class Users(db.Model):
    __tablename__ = 'Users'
    userID = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    

class Admin(db.Model):
    __tablename__ = 'Admin'
    adminID = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # Add other admin-related attributes and relationships here




    


