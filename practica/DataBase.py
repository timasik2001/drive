import math
import time
import sqlite3
from flask import url_for
import re


class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addUser(self, name, email, hpsw, hpsw2):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res["count"] > 0:
                print("Пользователь с таким email уже существует")
                res = False
                return res
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД" + str(e))
            return False
        res = True
        return res
    
    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False
    
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
        
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False
    
    def getAllUsers(self):
        try:
            self.__cur.execute("SELECT id, name, email FROM users ORDER by id DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения пользователей из БД " + str(e))

        return []
    
    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка при обновлении аватара " + str(e))
            return False
        return True

    def delUserById(self, id):
        try:
            self.__cur.execute(f"DELETE FROM users WHERE id = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения пользователей из БД " + str(e))
    
