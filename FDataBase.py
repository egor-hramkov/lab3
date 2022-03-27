import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def adduser(self, name, surname, email, age, work, position, password, photo):
        try:
            self.__cur.execute("INSERT INTO users VALUES(NULL,?, ?, ?, ?, ?, ?, ?, ?)", (name, surname, email, age, work, position, password, photo))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False
        return True

    def getUser(self, userId):
        try:
            self.__cur.execute(f"SELECT name, surname, email, age, worked, post, password, photo FROM users WHERE id = {userId}")
            res = self.__cur.fetchone()
            print(res[1])
            if res:
                return res[1]
        except sqlite3.Error as e:
            print("Ошибка получения пользователя из БД "+str(e))
        return(False, False)

    def getAllUsers(self):
        try:
            self.__cur.execute(f"SELECT name, surname, email, age, worked, post, password, photo FROM users")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения пользователя из БД "+str(e))
        return []
