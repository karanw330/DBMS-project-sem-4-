import sqlite3
import os
import hashlib
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "billing.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    """Simple SHA-256 hashing for the project."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('user', 'company')),
        upi_pin INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        price REAL NOT NULL,
        duration_days INTEGER NOT NULL,
        image_url TEXT,
        FOREIGN KEY (company_id) REFERENCES users (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (plan_id) REFERENCES plans (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        payment_date TEXT,
        payment_method TEXT DEFAULT 'UPI',
        FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER,
        qr_data TEXT NOT NULL,
        qr_status TEXT NOT NULL DEFAULT 'active',
        expiry TEXT,
        generated_at TEXT NOT NULL,
        FOREIGN KEY (payment_id) REFERENCES payments (id)
    )
    """)

    # --- Triggers for Automation and Integrity ---

    # 1. Automatically activate subscription and set dates after successful payment
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS activate_subscription_after_payment
    AFTER INSERT ON payments
    WHEN NEW.status = 'success'
    BEGIN
        UPDATE subscriptions
        SET status = 'active',
            start_date = datetime('now'),
            end_date = datetime('now', '+' || (
                SELECT p.duration_days 
                FROM plans p 
                JOIN subscriptions s ON s.plan_id = p.id 
                WHERE s.id = NEW.subscription_id
            ) || ' days')
        WHERE id = NEW.subscription_id;
    END;
    """)

    # 2. Prevent non-users (companies) from subscribing
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS validate_subscriber_role
    BEFORE INSERT ON subscriptions
    BEGIN
        SELECT CASE
            WHEN (SELECT role FROM users WHERE id = NEW.user_id) <> 'user'
            THEN RAISE(ABORT, 'Error: Only users can subscribe to plans.')
        END;
    END;
    """)

    # 3. Ensure payment amount matches plan price
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS validate_payment_amount
    BEFORE INSERT ON payments
    BEGIN
        SELECT CASE
            WHEN NEW.amount <> (
                SELECT p.price 
                FROM plans p 
                JOIN subscriptions s ON s.plan_id = p.id 
                WHERE s.id = NEW.subscription_id
            )
            THEN RAISE(ABORT, 'Error: Payment amount must match plan price.')
        END;
    END;
    """)

    # 4. Prevent duplicate active subscriptions for the same plan
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS prevent_subscription_overlap
    BEFORE INSERT ON subscriptions
    BEGIN
        SELECT CASE
            WHEN EXISTS (
                SELECT 1 FROM subscriptions 
                WHERE user_id = NEW.user_id AND plan_id = NEW.plan_id AND status = 'active'
            )
            THEN RAISE(ABORT, 'Error: User already has an active subscription for this plan.')
        END;
    END;
    """)

    # --- Views for Reporting ---

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS active_subscriptions_report AS
    SELECT 
        s.id AS subscription_id,
        u.name AS user_name,
        u.email AS user_email,
        p.plan_name,
        s.status,
        s.start_date,
        s.end_date,
        pay.amount AS paid_amount,
        pay.payment_date
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    JOIN plans p ON s.plan_id = p.id
    LEFT JOIN payments pay ON pay.subscription_id = s.id AND pay.status = 'success'
    WHERE s.status = 'active';
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
    
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    pwd = hash_password("password123")
    
    users_data = [
        ("Tech Corp", "admin@techcorp.com", pwd, "9876543210", "company", None),
        ("Alice Johnson", "alice@example.com", pwd, "1234567890", "user", 0000),
        ("Bob Smith", "bob@example.com", pwd, "5555555555", "user", 1)
    ]
    cursor.executemany(
        "INSERT INTO users (name, email, password, phone, role, upi_pin) VALUES (?, ?, ?, ?, ?, ?)",
        users_data
    )
    
    cursor.execute("SELECT id FROM users WHERE role='company' LIMIT 1")
    company_id = cursor.fetchone()[0]

    plans_data = [
        (company_id, "Netflix Monthly", "Unlimited movies, TV shows, and mobile games.", 499.0, 30, 
         "https://images.icon-icons.com/2699/PNG/512/netflix_logo_icon_170919.png"),
        (company_id, "Apple TV Yearly", "Apple Original series and movies from today's most imaginative storytellers.", 12999.0, 365, 
         "https://images.icon-icons.com/2890/PNG/512/apps_technology_logo_apple_tv_television_smart_tv_connect_icon_182742.png"),
        (company_id, "Youtube Premium Monthly", "Youtube Premium Monthly", 149.0, 30, 
         "https://www.numerama.com/wp-content/uploads/2022/03/youtube-premium.jpg"),
        (company_id, "Spotify Premium Monthly", "Spotify Premium Monthly", 129.0, 30, 
         "https://cdn.pixabay.com/photo/2016/10/22/00/15/spotify-1759471_1280.jpg"),
        (company_id, "Claude Pro Monthly", "Claude Pro Monthly", 1999.0, 30, 
         "https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/claude-ai-icon.png")
    ]
    cursor.executemany(
        "INSERT INTO plans (company_id, plan_name, description, price, duration_days, image_url) VALUES (?, ?, ?, ?, ?, ?)",
        plans_data
    )

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    init_db()
