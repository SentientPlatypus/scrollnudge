from flask import Flask, render_template, request, session, redirect, url_for
from threading import Thread
import csv
import gunicorn
import os
import random
import pandas as pd
import datetime

server = gunicorn.SERVER

CHECKING_IP = False
RUNS = 3
LENGTH = 500
TREATMENT_MAP = {
    1: 'random',
    2: 'random',
    3: 'random',
    4: 'perfect',
    5: 'perfect',
    6: 'perfect',
    7: 'partial',
    8: 'partial',
    9: 'partial',
}


def calculateReward(ncorrect:int):
    """Calculates the amount of money we give them for the number of correct selection"""
    return 2 + .2 * ncorrect if ncorrect > 0 else 0


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

@app.route('/assessment', methods=['POST'])
def assessment():
    user_id = request.form['user_id']
    session['user_id'] = user_id

    email_id = request.form['email_id']
    session['email_id'] = email_id

    session['ip'] = request.environ['REMOTE_ADDR']
    session['run_numbers'] = list(range(1, 10))
    experiment_log = pd.read_csv('experiment_log.csv')
    print(experiment_log)

    if CHECKING_IP and request.environ['REMOTE_ADDR'] in experiment_log['ip'].values:
        return render_template('done.html')
    
    return render_template('assessment.html')

@app.route('/submit-assessment', methods=['POST'])
def submitAssessment():
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')
    q4 = request.form.get('q4')

    if q1 == "75" and q2 == "yes" and q3 == "descending" and q4 == "30":
        print("assessment passed. redirecting to experiment")
        return redirect(url_for('run_experiment'))
    return render_template('failed.html')

@app.route('/run_experiment')
def run_experiment():

    user_id = session.get('user_id')
    email_id = session.get('email_id')
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
    return render_template('experiment.html', user_id=user_id, email_id = email_id, ip= ip, treatment=treatment, data=data, run_number = run_number)

@app.route('/log_experiment_data', methods=['POST'])
def log_experiment_data():
    data = request.json
    user_id = data['user_id']
    email_id = data['email_id']
    ip = data['ip']
    treatment = data['treatment']
    viewed = data['viewed']
    selected = data['selected']
    view_times = data['view_times']
    runNumber = session.get('run_number') 

    log_file = 'experiment_log.csv'
    file_exists = os.path.isfile(log_file)

    with open(log_file, 'a', newline='') as csvfile:
        fieldnames = ['User ID', 'Email ID', 'IP', 'Treatment', 'Run Number', 'Position Number', 'Selected (Y/N)', 'Viewed (Y/N)', 'View Time (s)', 'Selection Time (s)', 'Correct (Y/N)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        max_position = max(max(int(pos) for pos in viewed), max(int(pos) for pos in selected))
        for pos in range(max_position + 1):
            position_str = str(pos)
            writer.writerow({
                'User ID': user_id,
                'Email ID': email_id,
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
    total_payout = calculateReward(total_correct)

    with open('payout.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['prolificID','email','datecompleted','payout'])
        writer.writerow({
            'prolificID': user_id,
            'email': session.get('email_id'),
            'datecompleted': datetime.date.today().strftime('%Y-%m-%d'),
            'payout': total_payout
        })

    
    return render_template('endpage.html', message="You're done!", total_correct=total_correct, total_payout=total_payout)








if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0', port=8080)
    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()
