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

    # ── Tables ────────────────────────────────────────────────────────────────

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT    NOT NULL,
        email    TEXT    NOT NULL UNIQUE,
        password TEXT    NOT NULL,
        phone    TEXT    NOT NULL,
        role     TEXT    NOT NULL CHECK (role IN ('user', 'company')),
        upi_pin  INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL,
        plan_name    TEXT    NOT NULL,
        description  TEXT    NOT NULL DEFAULT '',
        price        REAL    NOT NULL,
        duration_days INTEGER NOT NULL,
        image_url    TEXT,
        FOREIGN KEY (company_id) REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        plan_id    INTEGER NOT NULL,
        status     TEXT    NOT NULL DEFAULT 'pending',
        start_date TEXT,
        end_date   TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY (plan_id) REFERENCES plans (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL,
        amount          REAL    NOT NULL,
        status          TEXT    NOT NULL DEFAULT 'pending',
        payment_date    TEXT,
        payment_method  TEXT    DEFAULT 'UPI',
        FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_codes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id   INTEGER,
        qr_data      TEXT    NOT NULL,
        qr_status    TEXT    NOT NULL DEFAULT 'active',
        expiry       TEXT,
        generated_at TEXT    NOT NULL,
        FOREIGN KEY (payment_id) REFERENCES payments (id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
    )
    """)

    # ── Indexes ───────────────────────────────────────────────────────────────
    # Speeds up FK lookups, status filters, and date-range queries.

    # users
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_email
        ON users (email)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_role
        ON users (role)
    """)

    # plans
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_plans_company_id
        ON plans (company_id)
    """)

    # subscriptions
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id
        ON subscriptions (user_id)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id
        ON subscriptions (plan_id)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_subscriptions_status
        ON subscriptions (status)
    """)

    # payments
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_payments_subscription_id
        ON payments (subscription_id)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_payments_status
        ON payments (status)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_payments_payment_date
        ON payments (payment_date)
    """)

    # qr_codes
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_qr_codes_payment_id
        ON qr_codes (payment_id)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_qr_codes_qr_status
        ON qr_codes (qr_status)
    """)

    # ─────────────────────────────────────────────────────────────────────────

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    pwd = hash_password("password123")

    users_data = [
        ("Tech Corp",      "admin@techcorp.com", pwd, "9876543210", "company", None),
        ("Alice Johnson",  "alice@example.com",  pwd, "1234567890", "user",    0000),
        ("Bob Smith",      "bob@example.com",    pwd, "5555555555", "user",    1),
    ]
    cursor.executemany(
        "INSERT INTO users (name, email, password, phone, role, upi_pin) VALUES (?, ?, ?, ?, ?, ?)",
        users_data
    )

    cursor.execute("SELECT id FROM users WHERE role='company' LIMIT 1")
    company_id = cursor.fetchone()[0]

    plans_data = [
        (company_id, "Netflix Monthly",
         "Unlimited movies, TV shows, and mobile games.", 499.0, 30,
         "https://images.icon-icons.com/2699/PNG/512/netflix_logo_icon_170919.png"),

        (company_id, "Apple TV Yearly",
         "Apple Original series and movies from today's most imaginative storytellers.", 12999.0, 365,
         "https://images.icon-icons.com/2890/PNG/512/apps_technology_logo_apple_tv_television_smart_tv_connect_icon_182742.png"),

        (company_id, "Youtube Premium Monthly",
         "Youtube Premium Monthly", 149.0, 30,
         "https://www.numerama.com/wp-content/uploads/2022/03/youtube-premium.jpg"),

        (company_id, "Spotify Premium Monthly",
         "Spotify Premium Monthly", 129.0, 30,
         "https://cdn.pixabay.com/photo/2016/10/22/00/15/spotify-1759471_1280.jpg"),

        (company_id, "Claude Pro Monthly",
         "Claude Pro Monthly", 1999.0, 30,
         "https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/claude-ai-icon.png"),
    ]
    cursor.executemany(
        "INSERT INTO plans (company_id, plan_name, description, price, duration_days, image_url) VALUES (?, ?, ?, ?, ?, ?)",
        plans_data
    )

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    init_db()
