from flask import Flask, render_template, request, session, redirect, url_for
from threading import Thread
import csv
import gunicorn
import os
import random
import pandas as pd

server = gunicorn.SERVER

CHECKING_IP = False
RUNS = 3
LENGTH = 500
TREATMENT_MAP = {
    1: 'random',
    2: 'random',
    3: 'partial',
    4: 'partial',
    5: 'perfect',
    6: 'perfect',
    7: 'random',
    8: 'random',
    9: 'partial',
    10: 'partial',
    11: 'perfect',
    12: 'perfect',
    13: 'random',
    14: 'random',
    15: 'partial',
    16: 'partial',
    17: 'perfect',
    18: 'perfect',
    19: 'random',
    20: 'random',
    21: 'partial',
    22: 'partial',
    23: 'perfect',
    24: 'perfect',
    25: 'random',
    26: 'random',
    27: 'partial',
    28: 'partial',
    29: 'perfect',
    30: 'perfect',
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
    session['ip'] = request.environ['REMOTE_ADDR']
    experiment_log = pd.read_csv('experiment_log.csv')
    print(experiment_log)

    if CHECKING_IP and request.environ['REMOTE_ADDR'] in experiment_log['ip'].values:
        return render_template('done.html')

    session['run_numbers'] = list(range(1, 3))
    return redirect(url_for('run_experiment'))

@app.route('/run_experiment')
def run_experiment():

    user_id = session.get('user_id')
    ip = session.get('ip')
    print(session)

    if not session['run_numbers']:
        return redirect(url_for('end_page'))

    session['run_number'] = random.choice(session['run_numbers'])
    session['treatment'] = TREATMENT_MAP[session['run_number']]
    session['run_numbers'].remove(session['run_number'])
    treatment = session.get('treatment')
    run_number = session.get('run_number', 1)

    data = load_data(str(run_number) + ".csv")
    return render_template('experiment.html', user_id=user_id, ip= ip, treatment=treatment, data=data, run_number = run_number)

@app.route('/log_experiment_data', methods=['POST'])
def log_experiment_data():
    data = request.json
    user_id = data['user_id']
    ip = data['ip']
    treatment = data['treatment']
    viewed = data['viewed']
    selected = data['selected']
    view_times = data['view_times']
    runNumber = session.get('run_number')

    log_file = 'experiment_log.csv'
    file_exists = os.path.isfile(log_file)

    with open(log_file, 'a', newline='') as csvfile:
        fieldnames = ['User ID', 'IP', 'Treatment', 'Run Number', 'Position Number', 'Selected (Y/N)', 'Viewed (Y/N)', 'View Time (s)', 'Selection Time (s)', 'Correct (Y/N)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        max_position = max(max(int(pos) for pos in viewed), max(int(pos) for pos in selected))
        for pos in range(max_position + 1):
            position_str = str(pos)
            writer.writerow({
                'User ID': user_id,
                'IP': ip,
                'Treatment': treatment,
                'Run Number': runNumber,
                'Position Number': pos + 1,
                'Selected (Y/N)': 1 if position_str in selected else 0,
                'Viewed (Y/N)': 1 if position_str in viewed else 0,
                'View Time (s)': view_times[position_str].get('viewedAt') if position_str in view_times else None,
                'Selection Time (s)': view_times[position_str].get('selectedAt') if position_str in view_times else None,
                'Correct (Y/N)': 1 if view_times.get(position_str, {}).get('correct') else 0
            })

    # Log this data, save it to a database, or process it as needed
    print(f'User ID: {user_id}')
    print(f'IP: {ip}')
    print(f'Treatment: {treatment}')
    print(f'Viewed: {viewed}')
    print(f'Selected: {selected}')
    print(f'View Times: {view_times}')
    print(f'Run Number: {runNumber}')

    session['run_number'] = runNumber + 1  # Increment the run number

    return 'Data logged successfully', 200

@app.route('/end')
def end_page():
    # Read the CSV file
    log = pd.read_csv('experiment_log.csv')
    
    # Get the current session's UserID and IP
    user_id = session.get('user_id')
    ip = session.get('ip')
    
    # Filter the log for rows that match the current session's UserID and IP
    matching_rows = log[(log['UserID'] == user_id) & (log['ip'] == ip)]
    
    # Count the total number of correct selections
    total_correct = matching_rows['correct'].sum()
    
    return render_template('endpage.html', message="You're done!", total_correct=total_correct)








if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0', port=8080)
    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()
