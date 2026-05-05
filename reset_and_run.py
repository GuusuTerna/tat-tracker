import os
import sqlite3
import shutil

# Delete all database files
db_files = ['tat.db', 'site.db', 'app.db', 'database.db']
for db_file in db_files:
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Deleted: {db_file}")

# Delete instance folder
if os.path.exists('instance'):
    shutil.rmtree('instance')
    print("Deleted instance folder")

print("\n✅ Database files cleaned!")
print("Now run: python app.py")