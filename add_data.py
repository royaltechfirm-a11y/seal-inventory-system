# add_data.py - Add your actual manufacturing data
import requests
import json

# Your Flask app URL
BASE_URL = "http://localhost:5000"

# Login first (using your demo credentials)
login_data = {
    "email": "admin@example.com",
    "password": "admin123"
}

# First, we need to simulate login by creating a session
# Since we're running locally, we'll use the database directly
# Let me give you a simpler method:

print("Adding your seal manufacturing data...")

# Raw Materials from your Excel
raw_materials = [
    {"name": "Rubber Sheet - NBR", "grade": "NBR", "unit": "kg", "current_stock": 500, "avg_cost": 180},
    {"name": "Rubber Sheet - Viton", "grade": "Viton", "unit": "kg", "current_stock": 300, "avg_cost": 220},
    {"name": "Steel Coin", "grade": "Carbon Steel", "unit": "pieces", "current_stock": 1000, "avg_cost": 85},
    {"name": "Steel Sheet", "grade": "SS304", "unit": "sheets", "current_stock": 200, "avg_cost": 1200},
    {"name": "Steel Wire", "grade": "Spring Steel", "unit": "meters", "current_stock": 500, "avg_cost": 45},
    {"name": "SSROD", "grade": "SS316", "unit": "meters", "current_stock": 150, "avg_cost": 350},
]

# Parts from your Excel
parts = [
    {"name": "Wati", "material_type": "Steel", "specific_type": "Wire/Coin/Sheet", "weight_per_unit": 0.5, "current_stock": 800},
    {"name": "Washer", "material_type": "Steel", "specific_type": "Wire/Coin/Sheet", "weight_per_unit": 0.3, "current_stock": 600},
    {"name": "Bellow", "material_type": "Rubber", "specific_type": "NBR/Viton", "weight_per_unit": 0.8, "current_stock": 400},
    {"name": "Buch", "material_type": "Rubber", "specific_type": "NBR/Viton", "weight_per_unit": 0.6, "current_stock": 300},
    {"name": "Cap", "material_type": "Rubber", "specific_type": "NBR/Viton", "weight_per_unit": 0.4, "current_stock": 500},
    {"name": "Oring", "material_type": "Rubber", "specific_type": "NBR/Viton", "weight_per_unit": 0.1, "current_stock": 1000},
]

print("✅ Data ready to add to your inventory system")
print("\nTo add manually, use the web interface at:")
print("http://localhost:5000")
print("\nOr use the API endpoints:")
print("POST /api/materials - Add raw materials")
print("POST /api/parts - Add parts")
print("\nExample material data:")
print(json.dumps(raw_materials[0], indent=2))