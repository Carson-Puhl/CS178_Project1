from flask import Flask, render_template, request, redirect, url_for
import pymysql
import creds
from dbCode import *
import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 
user_table = dynamodb.Table('Countries')

app = Flask(__name__)

def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country LIMIT 10;"
    return execute_query(query)

@app.route("/")
def index():
    countries = get_list_of_dictionaries()
    return render_template("index.html", results=countries)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        country = request.form.get("country")

        # Save only the User and Dream Vacation to DynamoDB
        user_table.put_item(Item={
            "User": username,
            "Dream Vacation": country
        })

        return redirect(url_for("signin"))
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")

        # Retrieve user info (Dream Vacation) from DynamoDB
        response = user_table.get_item(Key={"User": username})
        item = response.get("Item")

        if item:
            country = item["Dream Vacation"]

            # Query population from MySQL based on Dream Vacation
            query = "SELECT c.Population, cl.Language FROM country c JOIN countrylanguage cl ON c.Code = cl.CountryCode WHERE Name = %s AND cl.IsOfficial = 'T' LIMIT 1;"
            result = execute_query(query, (country,))
            if result:
                population = result[0]['Population']
                language = result[0]['Language']
                item["Population"] = population  # Add population to the user data
                item["Language"] = language  # Add official language to the user data

                return render_template("profile.html", user=item)
            else:
                return render_template("signin.html", country_error=True)

        else:
            return render_template("signin.html", error = True)

    return render_template("signin.html", error = False, country_error=False)

@app.route("/update_user", methods=["GET", "POST"])
def update_user():
    if request.method == "POST":
        username = request.form.get("username")
        new_country = request.form.get("country")

        # Update the Dream Vacation in DynamoDB
        user_table.update_item(
            Key={"User": username},
            UpdateExpression="SET #vacation = :new_country",
            ExpressionAttributeNames={"#vacation": "Dream Vacation"},
            ExpressionAttributeValues={":new_country": new_country}
        )

        # Optionally, update the population and language from MySQL (if needed)
        query = "SELECT c.Population, cl.Language FROM country c JOIN countrylanguage cl ON c.Code = cl.CountryCode WHERE Name = %s AND cl.IsOfficial = 'T' LIMIT 1;"
        result = execute_query(query, (new_country,))
        
        if result:
            population = result[0]['Population']
            language = result[0]['Language']

            # Fetch the user data again from DynamoDB to update it with population and language
            response = user_table.get_item(Key={"User": username})
            item = response.get("Item")
            
            if item:
                item["Population"] = population
                item["Language"] = language
                
                # Update the user's DynamoDB record with the new details
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

        return redirect(url_for("signin"))

    return render_template("update_user.html")

@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    if request.method == "POST":
        username = request.form.get("username")

        # Delete the user from DynamoDB
        response = user_table.delete_item(Key={"User": username})

        # Optionally, check if the user was successfully deleted
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            return redirect(url_for("index"))  # Redirect back to home after successful deletion
        else:
            return "Error deleting user."

    return render_template("delete_user.html")

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)