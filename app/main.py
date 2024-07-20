from flask import Flask, render_template, request, session, redirect, url_for
from threading import Thread
import csv
import gunicorn
import os
import random
import pandas as pd

server = gunicorn.SERVER

RUNS = 3
LENGTH = 500
TREATMENT_MAP = {
    1: 'random_nudge',
    2: 'random_no_nudge',
    3: 'partial_nudge',
    4: 'partial_no_nudgeg',
    5: 'perfect_nudge',
    6: 'perfect_no_nudge',
    7: 'random_nudge',
    8: 'random_no_nudge',
    9: 'partial_nudge',
    10: 'partial_no_nudgeg',
    11: 'perfect_nudge',
    12: 'perfect_no_nudge',
    13: 'random_nudge',
    14: 'random_no_nudge',
    15: 'partial_nudge',
    16: 'partial_no_nudgeg',
    17: 'perfect_nudge',
    18: 'perfect_no_nudge',
    19: 'random_nudge',
    20: 'random_no_nudge',
    21: 'partial_nudge',
    22: 'partial_no_nudgeg',
    23: 'perfect_nudge',
    24: 'perfect_no_nudge',
    25: 'random_nudge',
    26: 'random_no_nudge',
    27: 'partial_nudge',
    28: 'partial_no_nudgeg',
    29: 'perfect_nudge',
    30: 'perfect_no_nudge',
}

def createApp():
    app = Flask(
        __name__,
        template_folder=r"templates",
        static_folder=r"static"
    )
    app.secret_key = os.urandom(24)  # Set a secret key for session management
    return app

app = createApp()

@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "./error.html",
        code=404,
        msg=f"Page not found. Make sure you typed it in correctly.",
        desc=f"{e}"
    )

@app.errorhandler(500)
def internal_error(e):
    return render_template(
        "./error.html",
        code=500,
        msg=f"Internal server error. Contact me about this.",
        desc=f"{e}"
    )

@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "./error.html",
        code=403,
        msg=f"Forbidden. We tried to fetch some data. You said no. That's ok. Consent is great.",
        desc=f"{e}"
    )

def load_data(filename):
    path = 'app/presets/' + filename
    df = pd.read_csv(path)
    df = df.round(2)
    return df.to_dict(orient='records')

@app.route('/')
def start_page():
    return render_template('startpage.html')

@app.route('/experiment', methods=['POST'])
def experiment():
    user_id = request.form['user_id']
    session['user_id'] = user_id

    session['run_numbers'] = list(range(1, 3))
    return redirect(url_for('run_experiment'))

@app.route('/run_experiment')
def run_experiment():
    user_id = session.get('user_id')

    if not session['run_numbers']:
        return redirect(url_for('end_page'))

    session['run_number'] = random.choice(session['run_numbers'])
    session['treatment'] = TREATMENT_MAP[session['run_number']]
    session['run_numbers'].remove(session['run_number'])
    treatment = session.get('treatment')
    run_number = session.get('run_number', 1)

    data = load_data(str(run_number) + ".csv")
    return render_template('experiment.html', user_id=user_id, treatment=treatment, data=data, run_number = run_number)

@app.route('/log_experiment_data', methods=['POST'])
def log_experiment_data():
    data = request.json
    user_id = data['user_id']
    treatment = data['treatment']
    viewed = data['viewed']
    selected = data['selected']
    runNumber = session.get('run_number')

    log_file = 'experiment_log.csv'
    file_exists = os.path.isfile(log_file)

    with open(log_file, 'a', newline='') as csvfile:
        fieldnames = ['User ID', 'Treatment', 'Run Number', 'Position Number', 'Selected (Y/N)', 'Viewed (Y/N)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        max_position = max(max(int(pos) for pos in viewed), max(int(pos) for pos in selected))
        for pos in range(max_position + 1):
            writer.writerow({
                'User ID': user_id,
                'Treatment': treatment,
                'Run Number': runNumber,
                'Position Number': pos + 1,
                'Selected (Y/N)': 1 if str(pos) in selected else 0,
                'Viewed (Y/N)': 1 if str(pos) in viewed else 0
            })
    # Log this data, save it to a database, or process it as needed
    print(f'User ID: {user_id}')
    print(f'Treatment: {treatment}')
    print(f'Viewed: {viewed}')
    print(f'Selected: {selected}')
    print(f'Run Number: {runNumber}')

    session['run_number'] = runNumber + 1  # Increment the run number

    return 'Data logged successfully', 200

@app.route('/end')
def end_page():
    return render_template('endpage.html', message="You're done!")

if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0', port=8080)
    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()
