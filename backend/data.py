from datetime import datetime

# In-memory storage
users = []
plans = []
subscriptions = []
payments = []

# ID Counters
user_id_counter = 1
plan_id_counter = 1
sub_id_counter = 1
payment_id_counter = 1

def seed_data():
    global user_id_counter, plan_id_counter
    
    # 1 Company Account
    users.append({
        "id": user_id_counter,
        "name": "Tech Corp",
        "email": "admin@techcorp.com",
        "password": "password123",
        "role": "company"
    })
    company_id = user_id_counter
    user_id_counter += 1

    # 2 User Accounts
    users.append({
        "id": user_id_counter,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "password": "password123",
        "upi": "0000",
        "role": "user"
    })
    user_id_counter += 1

    users.append({
        "id": user_id_counter,
        "name": "Bob Smith",
        "email": "bob@example.com",
        "password": "password123",
        "upi": "0001",
        "role": "user"
    })
    user_id_counter += 1

    # 2 Plans
    plans.append({
        "id": plan_id_counter,
        "company_id": company_id,
        "plan_name": "Netlflix Monthly",
        "price": 499,
        "duration_days": 30,
        "image_url": "https://images.icon-icons.com/2699/PNG/512/netflix_logo_icon_170919.png"
    })
    plan_id_counter += 1

    plans.append({
        "id": plan_id_counter,
        "company_id": company_id,
        "plan_name": "Apple TV Yearly",
        "price": 12999,
        "duration_days": 365,
        "image_url": "https://images.icon-icons.com/2890/PNG/512/apps_technology_logo_apple_tv_television_smart_tv_connect_icon_182742.png"
    })
    plan_id_counter += 1
    
    print("Data seeded successfully.")

# Initial seed
seed_data()
