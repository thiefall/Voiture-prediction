import os 

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost:5432/nomdelabase"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "supersecret"