# Country App README

This is a Flask-based web application where users can sign up, log in, and manage their dream vacation destinations. The app integrates **MySQL** for population and language data and **AWS DynamoDB** for user profile storage.

## Features

This website allows the user to sign in where the put their username and their dream country to vacation at. Once this is done they are able to Sign In with their new username. This will then pull up their chosen country, that countries population, and that countries primary language.

## How it Works

### Flaskapp.py
Flaskapp.py is the main backend for this website. It handles routing, database interactions, and rendering HTML templates.

### SignUp.html
SignUp.html is where the formatting for the signup page is handled and displays how the page will look.

### SignIn.html
SignIn.html is where the formatting for the signin page is handled and displays how the page will look.

### Profile.html
Profile.html handles the formatting of the information that appears on the persons given dream country to visit and displays how this page will look.

### update_user.html
update_user.html is where the formatting for the update user page is handled and displays how the page will look.

### delete_user.html
delete_user.html is where the formatting for the delete user page is handled and displays how the page will look.

## Future Improvements
- I would like to improve this website in the future by adding more joins to the database in order for more information on the countries to be given.
- I would also like to add a list of users so that people can see other peoples dream country vacations.

## Credits
I got support from ChatGPT in order to help assist with HTML structure and also with help designing my website.

## Contact
If there are any questions or comments on this website contact me at carson.puhl@drake.edu
