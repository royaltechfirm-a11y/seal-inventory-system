# database.py - Database models for your inventory system
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ============== USER MANAGEMENT ==============
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='company', lazy=True)
    materials = db.relationship('RawMaterial', backref='company', lazy=True)
    products = db.relationship('Product', backref='company', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============== YOUR INVENTORY TABLES ==============
class RawMaterial(db.Model):
    __tablename__ = 'raw_materials'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    # Material details
    name = db.Column(db.String(100), nullable=False)  # "Rubber Sheet - NBR"
    grade = db.Column(db.String(50))                  # "Black 5mm"
    unit = db.Column(db.String(20))                   # "kg", "pieces", "meters"
    
    # Stock tracking
    opening_stock = db.Column(db.Numeric(12,4), default=0)
    current_stock = db.Column(db.Numeric(12,4), default=0)
    min_stock = db.Column(db.Numeric(12,4), default=0)
    
    # Cost tracking
    avg_cost = db.Column(db.Numeric(12,4), default=0)
    last_purchase_rate = db.Column(db.Numeric(12,4), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Part(db.Model):
    __tablename__ = 'parts'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    # Part details (from your Excel - Wati, Washer, Bellow, etc.)
    name = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.String(50))          # "Steel", "Rubber"
    specific_type = db.Column(db.String(100))         # "Wire/Coin/Sheet", "NBR/Viton"
    
    # Production details
    weight_per_unit = db.Column(db.Numeric(10,4))     # Weight in kg per piece
    current_stock = db.Column(db.Integer, default=0)
    avg_cost = db.Column(db.Numeric(12,4), default=0)  # Calculated from production
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    # Product details (from your Excel - Open, Close, J2, JC, etc.)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50))                   # "50mm", "75mm", "100mm"
    variant = db.Column(db.String(100))               # Any special variant
    
    current_stock = db.Column(db.Integer, default=0)
    selling_price = db.Column(db.Numeric(12,4), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============== PRODUCTION TABLES (Multi-output) ==============
class ProductionRun(db.Model):
    __tablename__ = 'production_runs'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    # Input details
    input_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'))
    input_quantity = db.Column(db.Numeric(12,4))
    input_cost = db.Column(db.Numeric(12,4))
    
    # For cost allocation
    total_output_weight = db.Column(db.Numeric(12,4))
    cost_per_kg = db.Column(db.Numeric(12,4))
    
    production_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class ProductionOutput(db.Model):
    __tablename__ = 'production_outputs'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('production_runs.id'))
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'))
    
    # Output details
    quantity_produced = db.Column(db.Integer)
    output_weight = db.Column(db.Numeric(12,4))      # quantity * weight_per_unit
    
    # Cost allocation
    allocated_cost = db.Column(db.Numeric(12,4))     # output_weight * cost_per_kg
    cost_per_unit = db.Column(db.Numeric(12,4))      # allocated_cost / quantity
    
    # Relationships
    run = db.relationship('ProductionRun', backref='outputs')
    part = db.relationship('Part', backref='productions')

# ============== ASSEMBLY TABLES ==============
class AssemblyRun(db.Model):
    __tablename__ = 'assembly_runs'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    quantity_assembled = db.Column(db.Integer)
    total_cost = db.Column(db.Numeric(12,4))
    cost_per_unit = db.Column(db.Numeric(12,4))
    
    assembly_date = db.Column(db.DateTime, default=datetime.utcnow)

class AssemblyComponent(db.Model):
    __tablename__ = 'assembly_components'
    id = db.Column(db.Integer, primary_key=True)
    assembly_id = db.Column(db.Integer, db.ForeignKey('assembly_runs.id'))
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'))
    
    quantity_used = db.Column(db.Integer)
    unit_cost = db.Column(db.Numeric(12,4))
    total_cost = db.Column(db.Numeric(12,4))
    
    # Relationships
    assembly = db.relationship('AssemblyRun', backref='components')
    part = db.relationship('Part')

# ============== TRANSACTION LOG ==============
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    transaction_type = db.Column(db.String(50))  # PURCHASE, PRODUCTION, ASSEMBLY, SALE, ADJUSTMENT
    reference_id = db.Column(db.Integer)         # ID of related record
    reference_type = db.Column(db.String(50))    # 'material', 'part', 'product'
    
    quantity = db.Column(db.Numeric(12,4))
    unit_price = db.Column(db.Numeric(12,4))
    total_value = db.Column(db.Numeric(12,4))
    
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))