from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from typing import Optional, List
from uuid import UUID, uuid4 
from models import User, Gender, Role , UserUpdateRequest 

app = FastAPI() 

#DB Lists
db: List[User] = [
    User(
        id= uuid4(),
        first_name= "Dhivakar",
        last_name= "Jayakumar",
        gender = Gender.male,
        roles = [Role.admin, Role.user]
    ),

    User(
        id= uuid4(),
        first_name= "Monika",
        last_name= "Elango",
        gender = Gender.female,
        roles = [Role.student]
    )
]

#Retrieve
@app.get("/api/users")
def users():
    return db

#Create
@app.post("/api/users")
def adduser(user: User):
    db.append(user)
    return {"id":user.id}

#Update
@app.put("/api/users/{user_id}")
def updateUser(user_update: UserUpdateRequest, user_id: UUID):
    for user in db:
        if user.id == user_id:
            if user_update.first_name is not None:
                user.first_name = user_update.first_name 
            if user_update.last_name is not None:
                user.last_name = user_update.last_name 
            if user_update.roles is not None:
                user.roles = user_update.roles
        return 
    raise HTTPException(
        status_code = 404,
        detail = f"User with id: {user_id} does not exists"
    )

#Delete
@app.delete("/api/users/{user_id}")
def deleteUser(user_id:UUID):
    for user in db:
        if user.id == user_id:
            db.remove(user)
            return{"msg":"Deleted"} 
        
    raise HTTPException(
        status_code = 404,
        detail = f"User with id: {user_id} does not exists"
    ) 