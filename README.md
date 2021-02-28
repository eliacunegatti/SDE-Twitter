# SDE-Twitter
This is a simple service developed in Flask using Python which allows fetching data from the official Twitter's API.

## Features
- Search User
- Fetch user's tweets
- Fetch twitter before and after a specified date
- Fetch in which hour and in which days a user published more tweets
- Retrieve like and tweets distributed over a timespan
- Get frequent words used in tweets
- Get a friend list of a user

## Installation and setup
First of all clone the repo.
Be sure to have Python already installed in your laptop, if not install it.
After that check to have all the packages used for this project.
If you are missing some packages here are available all the bash command in order to be sure you will install everything needed to run the code.

```bash
pip install pandas
pip install flask
pip install tweepy
pip install ntlk
pip install jsonschema
```

And then you must set up the ENV variables.
After all the setup simply run the code using the command 
```bash
flask run
```
## Api Documentation
You can find the full API documentation [here](https://gammamangolytica.docs.apiary.io/#reference/0/get-friends-of-user/display-basic-tweets-data).
