from flask import Flask, request, render_template, flash, redirect, session, url_for, g, make_response
import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from DataBase import DataBase
from UserLogin import UserLogin


DATABASE = "/tmp/drive.db"
DEBUG = True
SECRET_KEY = '7?4hJ2v8-EMLfK.CRjoepImVa'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "drive.db")))

login_manager = LoginManager(app)
#редирект если пользователь не залогинен в функциях login_required
login_manager.login_view = "login"
login_manager.login_message = "Для просмотра этой страницы необходимо войти в аккаунт"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)



def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn



def get_db():
    #соединение с бд (если оно не установлено)
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db



@app.teardown_appcontext
def close_db(error):
    # закрывает соединение если оно было установлено
    if hasattr(g, "link_db"):
        g.link_db.close()



# подключение к дб перед выполнением запроса
dbase = None
@app.before_request
def before_request():
    global dbase 
    db = get_db()
    dbase = DataBase(db)

@app.route("/")
def index():
    return render_template("index.html", title="Главная", current_user=current_user.is_authenticated)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form["email"])
        if user and check_password_hash(user["password"], request.form["password"]):
            userlogin = UserLogin().create(user)
            if "remember" in request.form:
                rm = True
            else:
                rm = False
            login_user(userlogin, remember=rm)
            flash("Успешный вход", category="success")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash("Неверный email или пароль", category="error")
    return render_template("login.html", title="Вход в учетную запись", current_user=current_user.is_authenticated)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hash = generate_password_hash(request.form["password"])
        hash2 = generate_password_hash(request.form["password2"])
        res = dbase.addUser(request.form["name"], request.form["email"], hash, hash2)
        if res:
            flash("Вы успешно зарегистрировались", category="success")
            return redirect(url_for("login"))
        elif request.form["password2"] != request.form["password"]:
            flash("Пароли не совпадают", category="error")
        else:
            flash("Произошла ошибка")
    return render_template("register.html", title="Регистрация", current_user=current_user.is_authenticated)

@app.route("/logout")
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for("login"))

@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    if request.method == "POST" and request.form["password"] == "12345" and request.form["login"] == "admin":
        flash("Вы вошли в админ панель", "success")
        session["username"] = request.form["login"]
        return redirect(url_for("admin"))
    else:
        flash("Неверный логин или пароль", "error")
    return render_template("adminlogin.html", title="Админ-панель", current_user=current_user.is_authenticated)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        dbase.delUserById(request.form["id"])
        return render_template("admin.html", title="Админ-панель", current_user=current_user.is_authenticated, users=dbase.getAllUsers())
    if "username" in session and session["username"] == "admin":
        return render_template("admin.html", title="Админ-панель", current_user=current_user.is_authenticated, users=dbase.getAllUsers())
    else:
        return redirect(url_for("adminlogin"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", title="Профиль")

@app.route("/userava")
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers["Content-Type"] = "image/png"
    return h

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
            except FileNotFoundError as e:
                print(str(e))
    return redirect(url_for("profile"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", title="Страница не найдена", current_user=current_user.is_authenticated)



# функция для создания бд
# def create_db():
    
#     db = connect_db()
#     with app.open_resource("sq_db.sql", mode="r") as f:
#         db.cursor().executescript(f.read())
#     db.commit()
#     db.close()


if __name__ == "__main__":
    session = {}
    app.run()