"""
@author: Kristina Bridgwater

this program defines the different routes of the flask app and runs the entire application

"""

# imports
from flask import Flask, render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField
import os


# configs
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = "mysecretkey"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Lc6yOYUAAAAAPTvhl7pz5jt224kFXuxDibBIYtL"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Lc6yOYUAAAAAKiCPcNN8bDw4cAqxJnwmn3WpHhw"



# define form objects
class Widgets(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField(label="Submit")

# define routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = Widgets()
    if form.validate_on_submit():
        return render_template('cmsc447main.html')
    return render_template('cmsc447home.html', form=form)


@app.route("/main", methods=["GET", "POST"])
def main():
    return render_template("cmsc447main.html")


@app.route("/terms")
def terms(): 
    return render_template("cmsc447terms.html")
    
@app.route("/rep")
def rep():
    return render_template("main_rep.html")

@app.route("/swing")
def swing():
    return render_template("main_swing.html")

# run in debug mode
if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 4444)))
