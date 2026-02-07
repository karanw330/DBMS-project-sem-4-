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
        "role": "user"
    })
    user_id_counter += 1

    users.append({
        "id": user_id_counter,
        "name": "Bob Smith",
        "email": "bob@example.com",
        "password": "password123",
        "role": "user"
    })
    user_id_counter += 1

    # 2 Plans
    plans.append({
        "id": plan_id_counter,
        "company_id": company_id,
        "plan_name": "Basic Plan",
        "price": 9.99,
        "duration_days": 30
    })
    plan_id_counter += 1

    plans.append({
        "id": plan_id_counter,
        "company_id": company_id,
        "plan_name": "Pro Plan",
        "price": 29.99,
        "duration_days": 365
    })
    plan_id_counter += 1
    
    print("Data seeded successfully.")

# Initial seed
seed_data()
