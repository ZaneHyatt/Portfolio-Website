from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
import smtplib
from chat import chat
import os
from dotenv import load_dotenv

load_dotenv()

OWN_EMAIL = os.getenv("PW_EMAIL")
print(OWN_EMAIL)
OWN_PASSWORD = os.getenv("PW_PASSWORD")
print(OWN_PASSWORD)

app = Flask(__name__)
app.secret_key = os.getenv("PW_SECRET_KEY")
bootstrap = Bootstrap(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/work")
def work():
    return render_template("work.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        if data["name"] and data["email"] and data["message"] != "":
            send_email(data["name"], data["email"], data["phone"], data["message"])
        else:
            flash("You can't send a message without filling name, email and message fields.")
            return render_template("contact.html", msg_sent=False)
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)

@app.route("/chat_bot", methods=["GET", "POST"])
def chat_bot():
    if request.method == "POST":
        data = request.form
        return render_template("chat_bot.html", message=str(chat(data["message"])))
    return render_template("chat_bot.html")

if __name__ == "__main__":
    app.run(debug=True)