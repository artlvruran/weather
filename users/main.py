import os
import sys

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def general():


@app.route("/login")
def login():


@app.route("/sign_up")
def signup():


@app.route("/news")
def news():


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')