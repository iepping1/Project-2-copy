import os

from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)

class Message:
    def __init__(self, username, chat):
        self.username = username
        self.time = datetime.now()
        self.chat = chat

class Channel:
    def __init__(self, name, password, desciption):
        self.name = name
        self.password = password
        self.desciption = desciption
        self.no_people = 0
        self.message = []

    def __str__(self):
        return self.name

def channel_check(channel_list, name):
    for i in channel_list:
        if i.name == name:
            return False
    return True
def addMessage(channel_list, channel, message):
    for i in channel_list:
        if i.name == channel:
            i.message.append(message)
            return True
    return 
