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
        "plan_name": "Basic Plan",
        "price": 9.99,
        "duration_days": 30,
        "image_url": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&auto=format&fit=crop&q=60"
    })
    plan_id_counter += 1

    plans.append({
        "id": plan_id_counter,
        "company_id": company_id,
        "plan_name": "Pro Plan",
        "price": 29.99,
        "duration_days": 365,
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60"
    })
    plan_id_counter += 1
    
    print("Data seeded successfully.")

# Initial seed
seed_data()
