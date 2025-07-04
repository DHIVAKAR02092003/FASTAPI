from fastapi import FastAPI, HTTPException, Path
from typing import List
import pyodbc
import configparser
from app.models import User, CreateUser, UpdateUser

app = FastAPI()

config = configparser.ConfigParser()
config.read('config/config.ini')

server = config['sqlserver']['server']
database = config['sqlserver']['database']
username = config['sqlserver']['username']
password = config['sqlserver']['password']
driver = config['sqlserver']['driver']

connection_string = (
    f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

# DataBase Connection
def get_db_connection():
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        print("Connection Error:", e)
        return None

# For Reading All Users
@app.get("/users/", response_model=List[User])
def read_all_user():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("SELECT EmpId, Name, Address, Phone FROM test")
    rows = cursor.fetchall()
    result = [User(empId=row[0], name=row[1], address=row[2], phone=row[3]) for row in rows]
    conn.close()
    return result

# For Reading One User
@app.get("/users/{id}", response_model=User)
def read_user(id: int = Path(..., description="User ID")):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("SELECT EmpId, Name, Address, Phone FROM test WHERE EmpId = ?", id)
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(empId=row[0], name=row[1], address=row[2], phone=row[3])
    raise HTTPException(status_code=404, detail="User not found")

# Creating a new User
@app.post("/users/", response_model=User)
def create_user(user: CreateUser):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test (Name, Address, Phone) OUTPUT INSERTED.EmpId VALUES (?, ?, ?)",
        (user.name, user.address, user.phone)
    )
    emp_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return User(empId=emp_id, **user.dict())

# Update Existing User details
@app.put("/users/{id}", response_model=User)
def update_user(id: int, user: UpdateUser):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test WHERE EmpId = ?", id)
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    fields = []
    values = []
    if user.name is not None:
        fields.append("Name = ?")
        values.append(user.name)
    if user.address is not None:
        fields.append("Address = ?")
        values.append(user.address)
    if user.phone is not None:
        fields.append("Phone = ?")
        values.append(user.phone)

    values.append(id)
    cursor.execute(f"UPDATE test SET {', '.join(fields)} WHERE EmpId = ?", values)
    conn.commit()

    cursor.execute("SELECT EmpId, Name, Address, Phone FROM test WHERE EmpId = ?", id)
    row = cursor.fetchone()
    conn.close()
    return User(empId=row[0], name=row[1], address=row[2], phone=row[3])

# Delete User 
@app.delete("/users/{id}")
def delete_user(id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test WHERE EmpId = ?", id)
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    conn.close()
    return {"message": f"User with ID {id} deleted successfully"}
