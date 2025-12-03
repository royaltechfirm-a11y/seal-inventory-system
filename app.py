import os


# Database configuration for Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
# app.py - COMPLETE Inventory Management System
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'seal-inventory-secret-2024')

# Database configuration for Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============== DATABASE MODELS ==============
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(200))
    role = db.Column(db.String(50), default='user')  # ADDED: role field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RawMaterial(db.Model):
    __tablename__ = 'raw_materials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50))
    unit = db.Column(db.String(20))
    current_stock = db.Column(db.Numeric(12,4), default=0)
    min_stock = db.Column(db.Numeric(12,4), default=0)
    avg_cost = db.Column(db.Numeric(12,4), default=0)

class Part(db.Model):
    __tablename__ = 'parts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.String(50))
    specific_type = db.Column(db.String(100))
    weight_per_unit = db.Column(db.Numeric(10,4))
    current_stock = db.Column(db.Integer, default=0)
    avg_cost = db.Column(db.Numeric(12,4), default=0)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50))
    current_stock = db.Column(db.Integer, default=0)
    selling_price = db.Column(db.Numeric(12,4), default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============== ROUTES ==============
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/health')
def health_check():
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'service': 'Seal Inventory System',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        company = request.form.get('company_name')
        
        if User.query.filter_by(email=email).first():
            return "Email already exists", 400
        
        user = User(email=email, company_name=company)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    materials = RawMaterial.query.filter_by(user_id=current_user.id).count()
    parts = Part.query.filter_by(user_id=current_user.id).count()
    products = Product.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html',
                         materials_count=materials,
                         parts_count=parts,
                         products_count=products)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ============== API ENDPOINTS ==============
@app.route('/api/materials', methods=['GET', 'POST'])
@login_required
def materials_api():
    if request.method == 'POST':
        data = request.json
        material = RawMaterial(
            user_id=current_user.id,
            name=data['name'],
            grade=data.get('grade'),
            unit=data.get('unit', 'kg'),
            current_stock=data.get('current_stock', 0),
            avg_cost=data.get('avg_cost', 0)
        )
        db.session.add(material)
        db.session.commit()
        return jsonify({'success': True, 'id': material.id})
    
    materials = RawMaterial.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'current_stock': float(m.current_stock),
        'unit': m.unit,
        'avg_cost': float(m.avg_cost)
    } for m in materials])

@app.route('/api/parts', methods=['GET', 'POST'])
@login_required
def parts_api():
    if request.method == 'POST':
        data = request.json
        part = Part(
            user_id=current_user.id,
            name=data['name'],
            material_type=data.get('material_type'),
            specific_type=data.get('specific_type'),
            weight_per_unit=data.get('weight_per_unit', 0),
            current_stock=data.get('current_stock', 0)
        )
        db.session.add(part)
        db.session.commit()
        return jsonify({'success': True, 'id': part.id})
    
    parts = Part.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'material_type': p.material_type,
        'current_stock': p.current_stock,
        'weight_per_unit': float(p.weight_per_unit) if p.weight_per_unit else 0
    } for p in parts])

@app.route('/api/production/run', methods=['POST'])
@login_required
def create_production():
    """Multi-output production with cost allocation"""
    data = request.json
    
    # Calculate cost allocation based on weight
    input_cost = float(data.get('input_cost', 0))
    outputs = data.get('outputs', [])
    
    # Calculate total weight
    total_weight = sum(float(o.get('weight', 0)) * o.get('quantity', 0) for o in outputs)
    
    if total_weight == 0:
        return jsonify({'error': 'No valid outputs'}), 400
    
    cost_per_kg = input_cost / total_weight
    
    results = []
    for output in outputs:
        weight = float(output.get('weight', 0))
        quantity = output.get('quantity', 0)
        output_weight = weight * quantity
        allocated_cost = output_weight * cost_per_kg
        cost_per_unit = allocated_cost / quantity if quantity > 0 else 0
        
        results.append({
            'part_name': output.get('part_name'),
            'quantity': quantity,
            'allocated_cost': round(allocated_cost, 2),
            'cost_per_unit': round(cost_per_unit, 2)
        })
    
    return jsonify({
        'success': True,
        'input_cost': input_cost,
        'cost_per_kg': round(cost_per_kg, 2),
        'outputs': results
    })

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create demo data if no users exist
        if User.query.count() == 0:  # FIXED: Changed from Company.query
            print("Creating your seal manufacturing database...")
            
            # Create admin user
            user = User(
                email="admin@example.com",
                company_name="Tanvir's Seal Manufacturing",
                role="admin"
            )
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
            
            # ========== ADD YOUR ACTUAL RAW MATERIALS (From Excel Sheet 1) ==========
            print("Adding your raw materials...")
            raw_materials = [
                # name, grade, unit, stock, cost
                ("Rubber Sheet - NBR", "NBR", "kg", 500, 180),
                ("Rubber Sheet - Viton", "Viton", "kg", 300, 220),
                ("Steel Coin", "Carbon Steel", "pieces", 1000, 85),
                ("Steel Sheet", "SS304", "sheets", 200, 1200),
                ("Steel Wire", "Spring Steel", "meters", 500, 45),
                ("SSROD", "SS316", "meters", 150, 350),
            ]
            
            for name, grade, unit, stock, cost in raw_materials:
                material = RawMaterial(
                    user_id=user.id,
                    name=name,
                    grade=grade,
                    unit=unit,
                    current_stock=stock,
                    avg_cost=cost
                )
                db.session.add(material)
            
            # ========== ADD YOUR PARTS (From Excel Sheet 2) ==========
            print("Adding your parts inventory...")
            parts = [
                # name, material_type, specific_type, weight_per_unit, stock
                ("Wati", "Steel", "Wire/Coin/Sheet", 0.5, 800),
                ("Washer", "Steel", "Wire/Coin/Sheet", 0.3, 600),
                ("Bellow", "Rubber", "NBR/Viton", 0.8, 400),
                ("Buch", "Rubber", "NBR/Viton", 0.6, 300),
                ("Cap", "Rubber", "NBR/Viton", 0.4, 500),
                ("Oring", "Rubber", "NBR/Viton", 0.1, 1000),
                ("Spring", "Steel", "Wire", 0.2, 700),
                ("Rotary face", "Carbon/Ceramic/Tungsten", "Ceramic HW, LW, Pink", 0.7, 200),
                ("Stationary face", "Carbon/Ceramic/Tungsten", "Ceramic HW, LW, Pink", 0.7, 200),
            ]
            
            for name, material_type, specific_type, weight, stock in parts:
                part = Part(
                    user_id=user.id,
                    name=name,
                    material_type=material_type,
                    specific_type=specific_type,
                    weight_per_unit=weight,
                    current_stock=stock
                )
                db.session.add(part)
            
            # ========== ADD YOUR SEAL PRODUCTS (From Excel Sheet 3) ==========
            print("Adding your seal products...")
            products = [
                # name, size
                ("Open", "50mm"),
                ("Open", "75mm"),
                ("Open", "100mm"),
                ("Close", "50mm"),
                ("Close", "75mm"),
                ("Close", "100mm"),
                ("J2", "25mm"),
                ("J2", "50mm"),
                ("J2", "75mm"),
                ("JC", "50mm"),
                ("JC", "100mm"),
                ("Single Robin", "Standard"),
                ("Double Robin", "Standard"),
                ("Stork", "Standard"),
                ("MG", "Standard"),
                ("Honda", "Standard"),
                ("Type2100", "Standard"),
            ]
            
            for name, size in products:
                product = Product(
                    user_id=user.id,
                    name=name,
                    size=size,
                    current_stock=50,  # Starting stock
                    selling_price=0  # Will calculate later
                )
                db.session.add(product)
            
            db.session.commit()
            print("✅ Database created with YOUR actual manufacturing data!")
            print(f"   Raw Materials: {len(raw_materials)} items")
            print(f"   Parts: {len(parts)} items")
            print(f"   Seal Products: {len(products)} types")
            print("\n👤 Login: admin@example.com / admin123")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Inventory System at: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)