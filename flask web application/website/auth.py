from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, send_file
import openpyxl
from .models import User, Arbeit, Note, Vacation 
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import json
from datetime import datetime
import pandas as pd
import os
import pathlib as Path
import shutil
from dotenv import load_dotenv
from twilio.rest import Client
import sqlite3
from pprint import pprint

load_dotenv()
TWILIO_ACCOUNT_SID = 'AC5b2b173993defc40a9e555c54fa2e82a'
TWILIO_AUTH_TOKEN= 'cda12fa4da4c294e64109bb8dafaf3ca'
TWILIO_VERIFY_SERVICE = 'VA552a5e3eef19995560d6de1dfe31927b'
SENDGRID_API_KEY=  'd-6ac8199c58b4497f9ef7568aa05d409b'
TWILIO_VERIFY_SERVICE = 'VA552a5e3eef19995560d6de1dfe31927b'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)  

sqlite_connection= sqlite3.connect('database.db', check_same_thread=False)


auth = Blueprint("auth", __name__)


def date_dif(d1, d2):
    d1_date = datetime.strptime(d1, '%H:%M')
    d2_date = datetime.strptime(d2, '%H:%M')
    return str(d2_date - d1_date)

def calc_complete_time(time_length: str, time_break: int) -> float:
    time_1 = str(datetime.strptime(time_length, '%H:%M:%S'))
    time_1_hours = int(time_1[11:13])*60
    time_1_minutes = int(time_1[14:16])
    time_1_whole = (time_1_hours + time_1_minutes - time_break) / 60
    return time_1_whole

def time_check(worked_times: list) -> bool:
    correct_times = worked_times
    marked_times = [] 
    for t1 in worked_times:
        for t2 in worked_times:
            if t1 != t2:
                if t1.von < t2.von:
                    if t1.bis > t2.von:
                        return False
                elif t1.von > t2.von:
                    if t2.bis > t1.von:
                       return False
    return True

def check_break(work_times_day: int, entered_break_time: int) -> bool:
    if work_times_day < 360:
        return True
    elif work_times_day < 540 and entered_break_time >= 30:
        return True
    elif work_times_day > 540 and entered_break_time>= 45:
        return True
    else:
        return False

def convert_time(time_1: str) -> int:
        break_time_hours = int(time_1[0:2])*60 
        break_time_minutes = int(time_1[3:5])
        return break_time_hours + break_time_minutes

def send_verification(to_email: str):
    verification = client.verify \
        .services(TWILIO_VERIFY_SERVICE) \
        .verifications \
        .create(to=to_email, channel = 'email')
    print(verification.sid)

def check_verification_token(phone, token):
    check = client.verify \
        .services(TWILIO_VERIFY_SERVICE) \
        .verification_checks \
        .create(to=phone, code=token)    
    return check.status == 'approved'

def create_dataframe(import_dict: dict, month: str):
    output = pd.DataFrame.from_dict(import_dict)
    output["Gesamt"] = output["Gesamt"].astype(float)
    df_sum = output["Gesamt"].sum()
    print(df_sum)
    output.loc[len(output.index)] = ["", "", "", "", ""]
    output.loc[len(output.index)] = ["", "", "", "Gesamtstundenzahl:",df_sum]
    output.loc[len(output.index)] = ["", "", "", "Monat:",month]
    return output


def calc_month_len(input_array: list) -> float:
    length = 0
    for i in range(1,int(len(input_array)/4)+1):
        length = length + float(input_array[i*4-1])
    return length


def move_file(file_name):
    Path("export_files").mkdir(exist_ok = True)
    print("test")
    shutil.move(f"../{file_name}", "website/export_files")
    return True
    #except:
     #   return False


def create_data(user) -> dict:

    #Creating monthly lists
    january_list = list()
    february_list = list()
    march_list = list()
    april_list = list()
    may_list = list()
    june_list = list()
    july_list = list()
    august_list = list()
    september_list = list()
    october_list = list()
    november_list = list()
    december_list = list()

    #Create lists for every month containg each date, from, until and the length worked on that day
    for i in user.work:
        if i.date[5:7] == "01":
            january_list.append(i.date)
            january_list.append(i.von)
            january_list.append(i.bis)
            january_list.append(i.length)
           

        if i.date[5:7] == "02":
            february_list.append(i.date)
            february_list.append(i.von)
            february_list.append(i.bis)
            february_list.append(i.length)


        if i.date[5:7] == "03":
            march_list.append(i.date)
            march_list.append(i.von)
            march_list.append(i.bis)
            march_list.append(i.length)

       
        if i.date[5:7] == "04":
            april_list.append(i.date)
            april_list.append(i.von)
            april_list.append(i.bis)
            april_list.append(i.length)

        
        if i.date[5:7] == "05":
            may_list.append(i.date)
            may_list.append(i.von)
            may_list.append(i.bis)
            may_list.append(i.length)
        
        if i.date[5:7] == "06":
            june_list.append(i.date)
            june_list.append(i.von)
            june_list.append(i.bis)
            june_list.append(i.length)

        
        if i.date[5:7] == "07":
            july_list.append(i.date)
            july_list.append(i.von)
            july_list.append(i.bis)
            july_list.append(i.length)
        

        if i.date[5:7] == "08":
            august_list.append(i.date)
            august_list.append(i.von)
            august_list.append(i.bis)
            august_list.append(i.length)

        
        if i.date[5:7] == "09":
            september_list.append(i.date)
            september_list.append(i.von)
            september_list.append(i.bis)
            september_list.append(i.length)
        
        if i.date[5:7] == "10":
            october_list.append(i.date)
            october_list.append(i.von)
            october_list.append(i.bis)
            october_list.append(i.length)

        
        if i.date[5:7] == "11":
            november_list.append(i.date)
            november_list.append(i.von)
            november_list.append(i.bis)
            november_list.append(i.length)
    
        if i.date[5:7] == "12":
            december_list.append(i.date)
            december_list.append(i.von)
            december_list.append(i.bis)
            december_list.append(i.len)

    return_dict_month_list =  { 
                                "January": january_list, 
                                "February": february_list, 
                                "March": march_list, 
                                "April": april_list,
                                "May": may_list, 
                                "June": june_list, 
                                "July": july_list, 
                                "August": august_list, 
                                "September": september_list, 
                                "October": october_list, 
                                "November": november_list, 
                                "December": december_list
                                }

    return_dict_len =         {
                                "january_len": calc_month_len(january_list), 
                                "february_len": calc_month_len(february_list),
                                "march_len": calc_month_len(march_list),
                                "april_len":  calc_month_len(april_list),
                                "may_len":  calc_month_len(may_list),
                                "june_len": calc_month_len(june_list),
                                "july_len":  calc_month_len(july_list),
                                "august_len":  calc_month_len(august_list),
                                "september_len": calc_month_len(september_list),
                                "october_len":  calc_month_len(october_list),
                                "november_len": calc_month_len(november_list),
                                "december_len": calc_month_len(december_list)
                                }

    return return_dict_len, return_dict_month_list


def evaluate_soll_time(user_dep: str) -> int:

    #VWorking hours per month declaration for the different user departments
    if user_dep == "Geschäftsführer":
        soll_user = 60
    elif user_dep == "Vollzeit":
        soll_user = 160
    elif user_dep == "Teilzeit":
        soll_user = 80
    elif user_dep == "Werkstudent":
        soll_user = 80
    elif user_dep == "Mini-Job":
        soll_user = 40
    return soll_user


@auth.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["button"] == "login":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email = email.lower()).first()
            if user:
                if check_password_hash(user.password, password):
                    flash("Erfolgreich eingeloggt!", category = "success")
                    login_user(user, remember = True)
                    return redirect(url_for("views.home"))
                else:
                    flash("Passwort inkorrekt!", category = "error")
            else:
                flash ("E-Mail existiert nicht", category = "error")
        elif request.form["button"] == "Passwort vergessen":
            return redirect(url_for("auth.reset_request"))

    return render_template("login.html", user = current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign_up", methods = ["GET","POST"])
@login_required
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        second_name = request.form.get("secondName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_stat = request.form.get("user_stat")
        user_dep = request.form.get("user_dep")
        user = User.query.filter_by(email = email.lower()).first()

        if user:
            flash("E-Mail existiert bereits", category = "error")
        else:
            if len(email) < 4:
                flash("Email muss mindestens 4 Buchstaben beinhalten.", category = "error")
            elif len(first_name) < 2:
                flash("Vorname muss mindestens 2 Buchstaben beinhalten.", category = "error")
            elif len(second_name) < 2:
                flash("Nachname muss mindestens 4 Buchstaben beinhalten.", category = "error")
            elif len(password1) < 4:
                flash("Passwort muss mindesten 4 Buchstaben oder Zeichen enthalten.", category = "error")
            elif password1 != password2:
                flash("Passwörter stimmen nicht überein!", category = "error")
            elif user_stat != "Admin" and user_stat != "User":
                flash ("Status muss Admin oder User sein!", category = "error")
            elif user_dep != "Geschäftsführung" and user_dep != "Vollzeit" and user_dep != "Teilzeit" and user_dep != "Werkstudent" and user_dep != "Mini-Job":
                flash("Bitte gebe einen gültige Wert ein! (Geschäftsführung / Vollzeit / Teilzeit / Werkstudent / Mini-Job", category = "error")
            else:
                new_user = User(email = email.lower(), first_name = first_name, second_name = second_name, password = generate_password_hash(password1, method = "sha256"), user_stat = user_stat, user_dep = user_dep)
                db.session.add(new_user)
                db.session.commit()
                flash("User erfolgreich angelegt!", category = "success")
                return redirect(url_for("views.home"))

    return render_template("sign_up.html", user = current_user)


@auth.route("/enter", methods = ["GET","POST"])
@login_required
def enter_times():
    if request.method == "POST":
        
        #get all data
        date = request.form.get("date")
        von = request.form.get("von")
        bis = request.form.get("bis")
        break_time = request.form.get("break_time")
        length = date_dif(von, bis)
        worked_times = Arbeit.query.order_by(Arbeit.date).filter_by(date = date).all()
        new_time = Arbeit(date = date, von = von, bis = bis, user_id = current_user.id, length = length, break_user = 0)
        worked_times.append(new_time)
        #Check for empty fields
        if not date:
            flash("Bitte wähle ein Datum aus", category = "error")
        elif not von:
            flash("Bitte wähle einen Startzeitzeitpunkt aus", category = "error")
        elif not bis:
            flash("Bitte wähle einen Endzeitpunkt aus", category = "error")
        elif not break_time:
            flash("Bitte trage eine Pausenzeit ein!", category = "error")
        elif von > bis:
            flash("Der Arbeitsbeginn darf nicht vor dem Arbeitsende liegen bzw. diesem entsprechen!", category = "error")
        else:
            amount = 0
            for time in worked_times:
                start_min = int(time.von[3:5])
                start_hours = int(time.von[:2])
                end_min = int(time.bis[3:5])
                end_hours = int(time.bis[0:2])
                amount = amount + (end_hours - start_hours)*60 + ( end_min - start_min)

    
            break_time_converted = convert_time(break_time)
            time_delta_status = time_check(worked_times)
            check_break_status = check_break(amount, break_time_converted)

            if not time_delta_status:
                flash("Dein Speicherungsversuch überschneidet sich mit einem bereits vorhandenen Eintrag!", category = "error")
            elif not check_break_status:
                if amount >= 360:
                    flash("Deine eingetragene Pausenzeit entspricht nicht den Vorgaben: Ab 6h Arbeitszeit müssen mindestens 30 min Pause eingelegt werden.", category = "error")
                elif amount >= 540:
                    flash("Deine eingetragene Pausenzeit entspricht nicht den Vorgaben: Ab h Arbeitszeit müssen mindestens 45 min Pause eingelegt werden.", category = "error")
            else:
                new_arbeitszeit = Arbeit(date = date, von = von, bis = bis, user_id = current_user.id, length = round(calc_complete_time(length, break_time_converted), 2), break_user = break_time_converted)
                db.session.add(new_arbeitszeit)
                db.session.commit()
                flash("Deine Arbeitszeit wurde für den " + date + " für den Zeitraum " + von +" Uhr bis " + bis + " Uhr erfolgreich gespeichert", category = "success")

    return render_template("enter_times.html", user = current_user)

@auth.route("/edit", methods = ["POST","GET"])
@login_required
def edit_times():
    if request.method == "POST":
        date = request.form.get("date")
        
        stored = Arbeit.query.filter_by(date = date).first()
        if not date:
            flash("Bitte wähle ein Datum aus", category = "error")
        elif stored:
            data = Arbeit.query.filter_by(date = date)
            note = Arbeit.query.get(date)
            data.delete(note)
            db.session.commit()
            flash("Arbeitszeiten vom " + str(date) + " wurden erfolgreich gelöscht!", category = "success")
            return redirect(url_for("views.home"))
        else:
            flash("Das ausgewählte Datum ist noch nicht eingespeichert!", category = "error")
    return render_template("edit_times.html", user = current_user)


@auth.route("/display", methods = ["POST","GET"])
@login_required
def display_times():
    
    current_month = str(datetime.now().month)
    user_work_sorted = Arbeit.query.order_by(Arbeit.date).all()
    soll_user = evaluate_soll_time(current_user.user_dep)
    dict_len, dict_month_list = create_data(current_user)
    #Set ist_user variable for the ist time for the month, needed for the first if-statement in display_times.html
    if current_month == "1":
        ist_user = float(dict_len["january_len"])
    elif current_month == "2":
        ist_user = float(dict_len["february_len"])
    elif current_month == "3":
        ist_user = float(dict_len["march_len"])
    elif current_month == "4":
        ist_user = float(dict_len["april_len"])
    elif current_month == "5":
        ist_user = float(dict_len["may_len"])
    elif current_month == "6":
        ist_user = float(dict_len["june_len"])
    elif current_month == "7":
        ist_user = float(dict_len["july_len"])
    elif current_month == "8":
        ist_user = float(dict_len["august_len"])
    elif current_month == "9":
        ist_user = float(dict_len["september_len"])
    elif current_month == "10":
        ist_user = float(dict_len["october_len"])
    elif current_month == "11":
        ist_user = float(dict_len["november_len"])
    else:
        ist_user = float(dict_len["december_len"])

    

    return render_template("display_times.html", 
        user = current_user, 
        arbeit = user_work_sorted, 
        soll_user = soll_user,
        ist_user = ist_user,

        january_len = dict_len["january_len"], 
        february_len = dict_len["february_len"],
        march_len = dict_len["march_len"],
        april_len = dict_len["april_len"],
        may_len = dict_len["may_len"],
        june_len = dict_len["june_len"],
        july_len = dict_len["july_len"],
        august_len = dict_len["august_len"],
        september_len = dict_len["september_len"],
        october_len = dict_len["october_len"],
        november_len = dict_len["november_len"],
        december_len = dict_len["december_len"],
        current_month = current_month,

        january_list = dict_month_list["January"],
        february_list = dict_month_list["February"],
        march_list = dict_month_list["March"],
        april_list = dict_month_list["April"],
        may_list = dict_month_list["May"],
        june_list = dict_month_list["June"],
        july_list = dict_month_list["July"],
        august_list = dict_month_list["August"],
        september_list = dict_month_list["September"],
        october_list = dict_month_list["October"],
        november_list = dict_month_list["November"],
        december_list = dict_month_list["December"])
       
        
        

@auth.route("/notes", methods = ["GET", "POST"])
@login_required
def note():
    if request.method == "POST":
        note = request.form.get("note")

        if len(note) < 1:
            flash('Notiz ist zu kurz!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Notiz hinzugefügt', category='success')


    return render_template("notes.html", user = current_user)

@auth.route("/delete-note", methods = ["POST"])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note["noteId"]
    note = Note.query.get(noteId)
    flash("Notiz erfolgreich gelöscht!", category = "success")
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            return jsonify({})


@auth.route("/export", methods = ["POST","GET"])
@login_required
def export():
    rows = User.query.count()
    names = User.query.all()
    if request.method == "POST":
        #month = request.form.get("dropdown_month")
        #export_user = request.form.get("user_name") 
        month = "06"
        export_user = "Friedrich"

        #Creating monthly dictionarys

        january_dict =  {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        february_dict = {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        march_dict =    {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        april_dict =    {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        may_dict =      {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        june_dict =     {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        july_dict =     {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        august_dict =   {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        september_dict ={"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        october_dict =  {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        november_dict = {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        december_dict = {"Datum": [], "Von": [], "Bis": [], "Pause": [], "Gesamt": []}
        
        
        #e lists for  month contai, from, until length worked on that day
        export_queryd_user = User.query.filter_by(first_name = export_user ).first()
        for i in export_queryd_user.work:
            if i.date[5:7] == "01":
                if january_dict:
                    january_dict["Datum"].append(i.date)
                    january_dict["Von"].append(i.von)
                    january_dict["Bis"].append(i.bis)
                    january_dict["Pause"].append(i.break_user)
                    january_dict["Gesamt"].append(i.length)

            if i.date[5:7] == "02":
                if february_dict:
                    february_dict["Datum"].append(i.date)
                    february_dict["Von"].append(i.von)
                    february_dict["Bis"].append(i.bis)
                    february_dict["Pause"].append(i.break_user)
                    february_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "03":
                if march_dict:
                    march_dict["Datum"].append(i.date)
                    march_dict["Von"].append(i.von)
                    march_dict["Bis"].append(i.bis)
                    march_dict["Pause"].append(i.break_user)
                    march_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "04":
                if april_dict:
                    april_dict["Datum"].append(i.date)
                    april_dict["Von"].append(i.von)
                    april_dict["Bis"].append(i.bis)
                    april_dict["Pause"].append(i.break_user)
                    april_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "05":
                if may_dict:
                    may_dict["Datum"].append(i.date)
                    may_dict["Von"].append(i.von)
                    may_dict["Bis"].append(i.bis)
                    may_dict["Pause"].append(i.break_user)
                    may_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "06":
                if june_dict:
                    june_dict["Datum"].append(i.date)
                    june_dict["Von"].append(i.von)
                    june_dict["Bis"].append(i.bis)
                    june_dict["Pause"].append(i.break_user)
                    june_dict["Gesamt"].append(i.length)

            
            if i.date[5:7] == "07":
                if july_dict:
                    july_dict["Datum"].append(i.date)
                    july_dict["Von"].append(i.von)
                    july_dict["Bis"].append(i.bis)
                    july_dict["Pause"].append(i.break_user)
                    july_dict["Gesamt"].append(i.length)

            
            if i.date[5:7] == "08":
                if august_dict:
                    august_dict["Datum"].append(i.date)
                    august_dict["Von"].append(i.von)
                    august_dict["Bis"].append(i.bis)
                    august_dict["Pause"].append(i.break_user)
                    august_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "09":
                if september_dict:
                    september_dict["Datum"].append(i.date)
                    september_dict["Von"].append(i.von)
                    september_dict["Bis"].append(i.bis)
                    september_dict["Pause"].append(i.break_user)
                    september_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "10":
                if october_dict:
                    october_dict["Datum"].append(i.date)
                    october_dict["Von"].append(i.von)
                    october_dict["Bis"].append(i.bis)
                    october_dict["Pause"].append(i.break_user)
                    october_dict["Gesamt"].append(i.length)
                    

            if i.date[5:7] == "11":
                if november_dict:
                    november_dict["Datum"].append(i.date)
                    november_dict["Von"].append(i.von)
                    november_dict["Bis"].append(i.bis)
                    november_dict["Pause"].append(i.break_user)
                    november_dict["Gesamt"].append(i.length)
                    
            if i.date[5:7] == "12":
                if december_dict:
                    december_dict["Datum"].append(i.date)
                    december_dict["Von"].append(i.von)
                    december_dict["Bis"].append(i.bis)
                    december_dict["Pause"].append(i.break_user)
                    december_dict["Gesamt"].append(i.length)

        if month == "01":
            export_dataframe = create_dataframe(january_dict, month)
        elif month == "02":
            export_dataframe = create_dataframe(february_dict, month)
        elif month == "03":
            export_dataframe = create_dataframe(march_dict, month)
        elif month == "04":
            export_dataframe = create_dataframe(april_dict, month)
        elif month == "05":
            export_dataframe = create_dataframe(may_dict, month)
        elif month == "06":
            export_dataframe = create_dataframe(june_dict, month)
        elif month == "07":
            export_dataframe = create_dataframe(july_dict, month)
        elif month == "08":
            export_dataframe = create_dataframe(august_dict, month)
        elif month == "09":
            export_dataframe = create_dataframe(september_dict, month)
        elif month == "10":
            export_dataframe = create_dataframe(october_dict, month)
        elif month == "11":
            export_dataframe = create_dataframe(november_dict, month)
        else:
            export_dataframe = create_dataframe(december_dict, month)
        

        
        file_name = f"{export_queryd_user.first_name}_{export_queryd_user.second_name}_mediceo_arbeitszeiten.xlsx"
        export_dataframe.to_excel(file_name , engine = "openpyxl")
        flash ("Es wurden erfolgreich die Daten von " + str(export_user) + " des Monats "+ str(month) +" exportiert!", category = "success")
        #move_file(f"{export_queryd_user.first_name}_{export_queryd_user.second_name}_mediceo_arbeitszeiten")

        #return "In the future, a download will be available here."
        #return export_dataframe.to_excel(f"{export_user}_{export_queryd_user.second_name}_mediceo_arbeitszeiten_{month}.xlsx", engine = "openpyxl"), redirect(url_for("auth.home", user = current_user))
        return redirect(url_for("views.home", user = current_user))

        

    return render_template("export.html", user = current_user, rows = rows, names = names)

@auth.route("/settings", methods = ["POST","GET"])
@login_required
def settings():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password_1= request.form.get("new_password_1")
        new_password_2 = request.form.get("new_password_2")

        if not old_password:
            flash("Bitte gib dein altes Passwort ein!", category = "error")
        elif not new_password_1:
            flash("Bitte gib dein neues Passwort ein!", category = "error")
        elif not new_password_2:
            flash("Bitte bestätige dein Passwort", category = "error")
        else:
            if check_password_hash(current_user.password, old_password):
                if new_password_1 == new_password_2:   
                    change_user = User.query.filter_by(id = current_user.id).first()
                    change_user.password = generate_password_hash(new_password_1, method = "sha256")
                    db.session.commit()
                    flash(f"Passwort erfolgreich zurück gesetzt! - Logge {current_user.first_name} aus",)
                    logout()
                    redirect(url_for("auth.login"))
                    
                else: 
                    flash("Falsches Passwort", category = "error")
            else: 
                flash("Die beiden neuen Passwörter stimmen nicht überein!", category = "error")


    return render_template("settings.html", user = current_user)


@auth.route("/reset_request", methods = ["POST","GET"])
def reset_request():
    if request.method == "POST":
        to_email = request.form.get("email").lower()
        user = User.query.filter_by(email = to_email).first()  

        if not to_email:
            flash("Bitte gib eine E-Mail Adresse ein.")
        if not user:
            flash("Es wurde kein Account mit dieser E-Mail Adresse gefunden", category = "error")
        else:
            session["to_email"] = to_email.lower()
            send_verification(to_email)
            flash("Du erhälst eine E-Mail mit einem Link zum zurücksetzen des Passworts. Bitte schaue auch in deinem Spam-Ordner nach.", category = "success")
            return redirect(url_for("auth.generate_verification_code"))

    return render_template("reset_request.html", user = current_user)

@auth.route("/profile", methods = ["POST","GET"])
@login_required
def profile():
    return render_template("profile.html", user = current_user)


@auth.route('/verifyme', methods=['GET', 'POST'])
def generate_verification_code():
    to_email = session['to_email']
    error = None

    if request.method == 'POST':
        verification_code = request.form['verificationcode']
        if check_verification_token(to_email, verification_code):
            flash("Verifizierungscode gültig!", category = "success")
            return redirect(url_for("auth.new_password"))
        else:
            flash("Falscher Verifikationscode. Bitte erneut versuchen! ", category = "error")
    return render_template("verifypage.html", user = current_user)

@auth.route("/new_password", methods = ["POST","GET"])
def new_password():
    if request.method == "POST":
        new_password_1= request.form.get("new_password_1")
        new_password_2 = request.form.get("new_password_2")
        
        if not new_password_1:
            flash("Bitte gib dein neues Passwort ein!", category = "error")
        elif not new_password_2:
            flash("Bitte bestätige dein Passwort", category = "error")
        else:
            if new_password_1 == new_password_2: 
                change_user = User.query.filter_by(email = session["to_email"]).first()
                change_user.password = generate_password_hash(new_password_1, method = "sha256")
                db.session.commit()

                flash("Passwort geändert. Bitte logge dich erneut ein!", category = "success")
                return redirect(url_for("auth.login")) 
                    
            else: 
                flash("Die beiden neuen Passwörter stimmen nicht überein!", category = "error")
                return "An error occured when trying to commit changes to the database. Please inform the system administrator and do not proceed with the password reset process."
    return render_template("new_password.html", user = current_user)


@auth.route("/coworker_times", methods = ["POST","GET"])
@login_required
def coworker_times():
    rows = User.query.count()
    names = User.query.all()

    if request.method == "POST":
        #user_first_name = request.form.get("user_first_name")
        #user_second_name = request.form.get("user_second_name")
        user_first_name = "Friedrich"
        user_second_name = "Friedrich"
        user_to_display = User.query.filter_by(first_name = user_first_name, second_name = user_second_name).first()
        soll_user = evaluate_soll_time(user_to_display.user_dep)
        dict_len, dict_month_list = create_data(user_to_display)

        return render_template("user_specified_view.html", 
        january_len = dict_len["january_len"], 
        february_len = dict_len["february_len"],
        march_len = dict_len["march_len"],
        april_len = dict_len["april_len"],
        may_len = dict_len["may_len"],
        june_len = dict_len["june_len"],
        july_len = dict_len["july_len"],
        august_len = dict_len["august_len"],
        september_len = dict_len["september_len"],
        october_len = dict_len["october_len"],
        november_len = dict_len["november_len"],
        december_len = dict_len["december_len"],

        january_list = dict_month_list["January"],
        february_list = dict_month_list["February"],
        march_list = dict_month_list["March"],
        april_list = dict_month_list["April"],
        may_list = dict_month_list["May"],
        june_list = dict_month_list["June"],
        july_list = dict_month_list["July"],
        august_list = dict_month_list["August"],
        september_list = dict_month_list["September"],
        october_list = dict_month_list["October"],
        november_list = dict_month_list["November"],
        december_list = dict_month_list["December"],

        user = user_to_display, 
        soll = soll_user, 
        rows = rows, 
        names = names)
        
    return render_template("user_specified_view.html", user = current_user, rows = rows, names = names)

@auth.route("/vacation_menu", methods = ["POST","GET"])
@login_required
def vacation_menu():
    if request.method == 'POST':
        if request.form['home_button'] == "Urlaub eintrage":
            return redirect(url_for("auth.vacation", user = current_user))
        elif request.form['home_button'] == "Urlaubsanträge":
            return redirect(url_for("auth.vacation_approval", user = current_user))
    return render_template("vacation_menu.html", user = current_user)


@auth.route("/vacation", methods = ["POST","GET"])
@login_required
def vacation():
    if request.method == "POST":
        vac_date = request.form.get("date")
        vac_type = request.form.get("type")
        return vac_date, vac_type
    return render_template("vacation.html", user = current_user)


@auth.route("/vacation_approval", methods = ["POST","GET"])
@login_required
def vacation_approval():
    return render_template("vacation_approval.html", user = current_user)