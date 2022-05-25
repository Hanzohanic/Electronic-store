from flask import Flask, redirect, url_for, render_template

app = Flask(__name__, template_folder="templates/Main")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/offers")
def page():
    return render_template("storefront/offers.html")


if __name__ == "__main__":
    app.run()
