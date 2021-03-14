# Marvel Impossible Travel Challenge

## Disclaimer
This code was created by Matt Kaufman as a part of the Marvel Impossible Travel Challenge. 

In the interest of time and simplicity, some concessions were made. More modular functionality would be preferable to 
the current state, and there are many locations where error handling would have to be significantly improved if this 
were a production app.

Additionally, the use of a Flask dev server would never be done in a production scenario, of course.

## Components

This app uses Docker, Python 3.9, Flask, Requests, Sqlite3 and the Validators library. These were chosen as one 
possible approach, though the approach to exfiltration could have been handled in a wide variety of ways.

## Setting Things Up

### Step 1: Create an Environment File
Create an environment file containing your API keys with any name and in any safe location of your choosing. 

The file should be in the below format, with "publickey" being replaced by your Marvel Developer API public key and 
"privatekey" being replaced by your private key. 

DO NOT share this file with others. DO NOT check it in to a repository. Using environment variables was specifically
chosen as a "cheap" way to protect these values for this exercise. In a full production system even further care would 
be given in handling the API keys, likely using a secrets manager.

```
AGENT_PUBLIC_KEY=publickey
AGENT_PRIVATE_KEY=privatekey
```

### Step 2: Build the Image

From the root of this project type the following to create an image:

```
docker build -t agentportal:1 .
```

### Step 3: Run the App

Execute this command, replacing env.list with the full path to your environment file created above.

```
docker run -p 5000:5000 --env-file env.list -t agentportal:1 --name agentportal
```

### Step 4: Navigate to the Running App

Open your browser and go to http://localhost:5000/ 

---
# Other Info

## Database
An initial, empty agent database is provided for deployment. To create a new, empty version of the database for any 
reason you can run this command:

```
python init_agentdb.py
```