from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Database initialized successfully!")
    print("👉 Run 'python app.py' to start the server")