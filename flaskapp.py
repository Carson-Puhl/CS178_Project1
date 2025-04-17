from flask import Flask, render_template, request, redirect, url_for
import pymysql
import creds
from dbCode import *  # Helper functions for MySQL queries
import boto3

# Connect to DynamoDB in the us-east-1 region
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 
user_table = dynamodb.Table('Countries')  # Reference to the DynamoDB table

app = Flask(__name__)

# Helper function to query the first 10 countries from MySQL
def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country LIMIT 10;"
    return execute_query(query)

# Home page route
@app.route("/")
def index():
    countries = get_list_of_dictionaries()  # Get list of countries and populations
    return render_template("index.html", results=countries)

# Sign-up route for adding a user to DynamoDB
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        country = request.form.get("country")

        # Save user and their dream vacation country to DynamoDB
        user_table.put_item(Item={
            "User": username,
            "Dream Vacation": country
        })

        return redirect(url_for("signin"))  # Redirect to sign-in after signup

    return render_template("signup.html")  # Show signup form

# Sign-in route to view a user's profile based on their dream vacation
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")

        # Retrieve user info (Dream Vacation) from DynamoDB
        response = user_table.get_item(Key={"User": username})
        item = response.get("Item")

        if item:
            country = item["Dream Vacation"]

            # Look up population and language of the dream vacation country from MySQL
            query = """
                SELECT c.Population, cl.Language
                FROM country c
                JOIN countrylanguage cl ON c.Code = cl.CountryCode
                WHERE Name = %s AND cl.IsOfficial = 'T'
                LIMIT 1;
            """
            result = execute_query(query, (country,))
            if result:
                population = result[0]['Population']
                language = result[0]['Language']

                # Add data to user dictionary
                item["Population"] = population
                item["Language"] = language

                return render_template("profile.html", user=item)  # Show user profile
            else:
                # Country not found in MySQL
                return render_template("signin.html", country_error=True)

        else:
            # User not found in DynamoDB
            return render_template("signin.html", error=True)

    # Initial GET request to show the sign-in form
    return render_template("signin.html", error=False, country_error=False)

# Route to update a user's dream vacation
@app.route("/update_user", methods=["GET", "POST"])
def update_user():
    if request.method == "POST":
        username = request.form.get("username")
        new_country = request.form.get("country")

        # First, update only the dream vacation country in DynamoDB
        user_table.update_item(
            Key={"User": username},
            UpdateExpression="SET #vacation = :new_country",
            ExpressionAttributeNames={"#vacation": "Dream Vacation"},
            ExpressionAttributeValues={":new_country": new_country}
        )

        # Then, get updated population/language from MySQL
        query = """
            SELECT c.Population, cl.Language
            FROM country c
            JOIN countrylanguage cl ON c.Code = cl.CountryCode
            WHERE Name = %s AND cl.IsOfficial = 'T'
            LIMIT 1;
        """
        result = execute_query(query, (new_country,))
        
        if result:
            population = result[0]['Population']
            language = result[0]['Language']

            # Get the user again to attach this new info
            response = user_table.get_item(Key={"User": username})
            item = response.get("Item")
            
            if item:
                item["Population"] = population
                item["Language"] = language

                # Update the user item again with population and language
                user_table.update_item(
                    Key={"User": username},
                    UpdateExpression="SET #vacation = :new_country, #pop = :population, #lang = :language",
                    ExpressionAttributeNames={
                        "#vacation": "Dream Vacation",
                        "#pop": "Population",
                        "#lang": "Language"
                    },
                    ExpressionAttributeValues={
                        ":new_country": new_country,
                        ":population": population,
                        ":language": language
                    }
                )

        return redirect(url_for("signin"))  # Redirect to sign-in after updating

    return render_template("update_user.html")  # Show update form

# Route to delete a user from DynamoDB
@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    if request.method == "POST":
        username = request.form.get("username")

        # Delete the user record from DynamoDB
        response = user_table.delete_item(Key={"User": username})

        # If delete was successful, redirect to home page
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            return redirect(url_for("index"))
        else:
            return "Error deleting user."

    return render_template("delete_user.html")  # Show delete form

# Always keep this at the end of the file to run your Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
