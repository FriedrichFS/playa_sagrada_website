from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User

views = Blueprint("views", __name__)

@views.route("/", methods = ["GET","POST"])
@login_required
def home():
    if request.method == 'POST':
        if request.form['home_button'] == 'Arbeitszeiten eintragen':
            return redirect(url_for("auth.enter_times", user = current_user))
        elif request.form['home_button'] == 'Arbeitszeiten verwalten':
            return redirect(url_for("auth.edit_times", user = current_user))
        elif request.form['home_button'] == 'Arbeitszeiten anzeigen':
            return redirect(url_for("auth.display_times", user = current_user))
        elif request.form['home_button'] == 'Einstellungen':
            return redirect(url_for("auth.settings", user = current_user))
    return render_template("home.html", user = current_user)