from flask import Flask
from flask import render_template
import datamgmt

app = Flask(__name__)


@app.route('/')
def agent_portal():
    return render_template('index.html')


@app.route('/retrieve')
def retrieve_data():
    # Retrieve data from Marvel API into memory
    datamgmt.get_data_from_hq()
    return '<p>Data retrieved.</p><p><a href="/">Return to Agent Portal</a>'


@app.route('/self-destruct')
def self_destruct():
    datamgmt.clear_database()
    return '<p>Data purged from database.</p><p><a href="/">Return to Agent Portal</a>'


@app.route('/exfiltrate')
def exfiltrate_data():
    all_chars = datamgmt.get_characters_from_db()
    return render_template('exfiltration.html', chars=all_chars)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
