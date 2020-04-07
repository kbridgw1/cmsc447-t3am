# imports
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField

# configs
app = Flask(__name__)
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

# run in debug mode
if __name__ == '__main__':
    app.run(debug=True)
