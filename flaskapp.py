from flask import Flask, render_template, request, redirect, url_for
import pymysql
import creds
from dbCode import *

app = Flask(__name__)

def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country LIMIT 10;"
    return execute_query(query)

@app.route("/")
def index():
    countries = get_list_of_dictionaries()
    return render_template("index.html", results=countries)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
