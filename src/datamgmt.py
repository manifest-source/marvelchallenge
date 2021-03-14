import requests     # friendlier than urllib
import hashlib      # needed for Marvel API hashing
import time         # used for Marvel API time value
import sqlite3      # used for simple app -- would be more robust DB for shipping app
import os           # needed to retrieve keys from environment variables
import validators   # used for validating URLs before calling them

# In a full app, this would be broken down further in the configuration, 
# along with better handling of slashes, perhaps with urlunparse/urlparse
api_public_key = os.environ['AGENT_PUBLIC_KEY']
api_private_key = os.environ['AGENT_PRIVATE_KEY']


def api_key_and_params():
    """Prepares the parameters required for the Marvel API call, including timestamp, api key and hash."""
    # Prep for generating the API hash
    # Generate timestamp for the call and encode it
    ts = str(int(time.time()))
    ts_bytes = ts.encode('utf-8')
    private_key_bytes = api_private_key.encode('utf-8')
    public_key_bytes = api_public_key.encode('utf-8')
    # Generate hash according to Marvel API spec
    bytes_to_hash = (ts_bytes + private_key_bytes + public_key_bytes)
    h = hashlib.md5()
    h.update(bytes_to_hash)
    api_hash = h.hexdigest()
    # Prepare payload for GET call
    return {'ts': ts, 'apikey': api_public_key, 'hash': api_hash}


def get_character_from_api(character_name):
    """Retrieves a single character record from the Marvel API."""
    payload = api_key_and_params()
    payload['name'] = character_name

    # In a shipping app there would be far better error handling here. Logging, alerts and better failures are needed.
    # The API url would also be configuration-driven.
    api_char_url = 'https://gateway.marvel.com/v1/public/characters'

    # Make the API call
    response = requests.get(api_char_url, params=payload).json()

    # Make sure we got a good response
    if 'code' in response and response['code'] == requests.codes['ok']:
        # Look for the proper data within the response
        if 'data' in response and 'results' in response['data'] and len(response['data']['results']) > 0:
            # We're looking for a single character and will assume, for this small app, that the first result
            # is the one we want
            return response['data']['results'][0]
        else:
            # An "ok" response from the API with no results found is unusual. Print an alert for this small app
            # but for a shipping app we'd want better handling here.
            print(f'ERROR: Response was OK but no character data found. Raw response:\n{response}\n======')
            raise ValueError('No character data found for Spectrum')
    else:
        # We don't elegantly handle a non-ok code in this little app.
        # In a shipping app we may have better handling of other responses
        # including logging, alerting, retries, etc, depending on code.
        print('Fatal error encountered handling response from API\nResponse: {}'.format(response))
        raise ValueError('Unable to handle non OK response from API in this little app')


def get_comic_chars_from_api(comic_uri):
    payload = api_key_and_params()
    # Make the API call for the characters within the comic
    response = requests.get(comic_uri + '/characters', params=payload).json()
    # Make sure we got a good response
    if 'code' in response and response['code'] == requests.codes['ok']:
        # Look for the proper data within the response
        if 'data' in response and 'results' in response['data'] and len(response['data']['results']) > 0:
            # We're looking for one or more characters
            return response['data']['results']
        else:
            # An "ok" response from the API with no results found is unusual. Print an alert for this small app
            # but for a shipping app we'd want better handling here.
            print(f'ERROR: Response was OK but no character data found. Raw response:\n{response}\n======')
            return []
    else:
        # We don't elegantly handle a non-ok code in this little app.
        # In a shipping app we may have better handling of other responses
        # including logging, alerting, retries, etc, depending on code.
        print('Fatal error encountered handling response from API\nResponse: {}'.format(response))
        return []


def get_data_from_hq():
    """Contact Marvel API and pull Spectrum's records along with her associates and commit them to the database."""
    # In a full-fledged app I'd break down the calls into further pieces for API calls and database interactions.
    # In the spirit of not prematurely optimizing and also keeping things lightweight for the challenge, I've opted
    # not to do that.

    # Get Spectrum's character record
    char_spectrum = get_character_from_api('Spectrum')

    # Prepare a list of associates which we'll build and process later
    associates = []

    # Find out what comics she was in. We're ignoring stories, events and series because the challenge specifically
    # called out "Obtain the same information for all other characters she's worked with in other COMICS." (emphasis
    # added)

    # Iterate through the comics she was in which we'll query for associated characters
    for comic in char_spectrum['comics']['items']:
        # Get the URI of the individual comic
        comic_uri = comic['resourceURI']
        # Validate it
        if validators.url(comic_uri):
            # Add to our list for later processing
            associates.extend(get_comic_chars_from_api(comic_uri))
        else:
            # URI didn't validate. In a full app we'd do more than printing to stdout
            print(f'URI provided for comic ({comic_uri}) was not valid. Skipping.')

    # Save the data we've collected in the database
    # Connect to the database. Note that the DB should have already been created per the instructions in the readme.md
    con = sqlite3.connect('agent.db')
    cur = con.cursor()
    # Insert the record for Spectrum
    cur.execute('INSERT INTO characters VALUES (?, ?, ?, ?)', (char_spectrum['id'],
                                                               char_spectrum['name'],
                                                               char_spectrum['description'],
                                                               char_spectrum['thumbnail']['path'] + '.' +
                                                               char_spectrum['thumbnail']['extension']))
    # Iterate through her associates and add the values
    for associate in associates:
        # Using the "OR IGNORE" syntax to ignore unique constraint violations. In a full app this would be more robust.
        cur.execute('INSERT OR IGNORE INTO characters VALUES (?, ?, ?, ?)', (associate['id'],
                                                                             associate['name'],
                                                                             associate['description'],
                                                                             associate['thumbnail']['path'] + '.' +
                                                                             associate['thumbnail']['extension']))
    con.commit()


def get_characters_from_db():
    # In a shipping app this would be better contained -- perhaps in its own module
    characters = []
    con = sqlite3.connect('agent.db')
    cur = con.cursor()
    cur.execute("SELECT id, name, description, pictureurl FROM characters ORDER by name ASC")
    rows = cur.fetchall()
    for row in rows:
        # Create a character object and add it to the array of characters
        characters.append({'id': row[0], 'name': row[1], 'description': row[2], 'pictureurl': row[3]})

    return characters


def clear_database():
    con = sqlite3.connect('agent.db')
    cur = con.cursor()
    cur.execute("DELETE FROM characters")
    con.commit()
