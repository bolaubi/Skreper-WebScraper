from scraper import app, dbs, dir, mail
from scraper.forms import RegisterForm, LoginForm
from scraper.models import User
from scraper.scraping import nike_func, nike_sale_func, tokopedia_func
from flask import render_template, redirect, url_for, flash, abort, send_from_directory, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
import os


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html', title='home')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        dbs.session.add(user_to_create)
        dbs.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was an error with creating a user: {err_msg}", category="danger")
    return render_template('register.html', form=form, title='register')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f"Success! You are logged in as: {attempted_user.username}", category='success')
            return redirect(url_for('home_page'))
        else:
            flash("Username and password are not match! Please try again", category='danger')
    return render_template('login.html', login_form=form, title='sign in')


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category="info")
    return redirect(url_for('home_page'))

########################
### FUNCTION CONTROL ###
########################
user_files_dict = {}

def csv_path_retriever(c_page, c_username, c_timestamp):
    csv_filename = f'{c_page}-{c_username}-{c_timestamp}.csv'
    create_csv_dir = f'static\\client\\{c_username}\\csv'
    create_csv_dir_path = os.path.join(dir, create_csv_dir)
    create_csv_dir_path_tocsv = os.path.join(create_csv_dir_path, csv_filename)
    return csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv

def csv_path_maker(c_page, c_username):
    now = datetime.now()
    now_timestamp = datetime.timestamp(now)

    if user_files_dict == {}:
        user_files_dict[f'{c_username}'] = {'csv': []}
        user_files_dict[f'{c_username}']['csv'].append(now_timestamp)
    elif c_username not in list(user_files_dict.keys()):
        user_files_dict[f'{c_username}'] = {'csv': []}
        user_files_dict[f'{c_username}']['csv'].append(now_timestamp)

    csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv = csv_path_retriever(c_page, c_username, now_timestamp)
    if not os.path.exists(create_csv_dir_path):
        os.makedirs(create_csv_dir_path)
    else:
        pass
    return create_csv_dir_path_tocsv, now_timestamp

def mail_the_user(c_page, c_username, c_user_email, now_timestamp):
    csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv = csv_path_retriever(c_page, c_username, now_timestamp)
    msg = Message(
        subject=f"Skreper - {c_username} CSV File",
        recipients=[f"{c_user_email}"],
        body="Thank you for using Skreper! Here's your CSV, have a nice day!",
    )
    with app.open_resource(create_csv_dir_path_tocsv) as csv:
        msg.attach(create_csv_dir_path_tocsv, 'text/csv', csv.read())
    mail.send(msg)
    flash("Your CSV file has been successfully sent to your email address!", category="success")
    os.remove(create_csv_dir_path_tocsv)
    return redirect(url_for(c_page))

###########################
### ENDFUNCTION CONTROL ###
###########################

@app.route('/nike')
@login_required
def nike():
    return render_template('nike.html', title='Nike Page')


@app.route('/nike/scraped-data-nike', methods=['POST', 'GET'])
def scraped_data_nike():
    if request.method =='POST':
        input_form = request.form
        try:
            current_df_scraped = nike_func(input_form['nikePage'])
        except:
            current_df_scraped = nike_func()
        if len(current_df_scraped) == 0:
            flash('Invalid Link', category='danger')
            return redirect(url_for('nike'))
        else:
            current_df_html_send = current_df_scraped.to_html(float_format=lambda x: 'IDR {:,}'.format(x), classes='table table-striped table-sm table-responsive table-responsive-xl-8 table-responsive-col-lg-4', table_id='nike_table', border=0, render_links=True)

    create_csv_dir_path_tocsv, now_timestamp = csv_path_maker('nike', current_user.username)
    current_df_scraped.to_csv(create_csv_dir_path_tocsv, index=False)
    return render_template('scraped_data_nike.html', title='Scraped Nike Page', table=current_df_html_send, now_timestamp=now_timestamp)


@app.route('/nike/download-scraped-data-nike/<current_username>', methods=['POST', 'GET'])
def download_scraped_data_nike(current_username):
    if request.method == 'POST':
        input_form = request.form
        csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv = csv_path_retriever('nike', current_username,input_form['nike_csv_download'])
        try:
            return send_from_directory(create_csv_dir_path, create_csv_dir_path_tocsv, filename=csv_filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Nike Page', category='danger')
        return redirect(url_for('nike'))


@app.route('/nike/email-scraped-data-nike/<current_username>', methods=['POST', 'GET'])
def email_scraped_data_nike(current_username):
    if request.method == 'POST':
        input_form = request.form
        try:
            return mail_the_user('nike', current_username, current_user.email, input_form['nike_csv_email'])
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Nike Page', category='danger')
        return redirect(url_for('nike'))


@app.route('/nikeSales')
@login_required
def nikeSales():
    return render_template('nikeSales.html', title='Nike Sales Page')


@app.route('/nikeSales/scraped-data-nikeSales', methods=['POST', 'GET'])
def scraped_data_nikeSales():
    if request.method == 'POST':
        input_form = request.form
        current_df_scraped = nike_sale_func(input_form['nikeSales-dropdown'])
        current_df_html_send = current_df_scraped.to_html(float_format=lambda x: 'IDR {:,}'.format(x), classes='table table-striped table-sm table-responsive table-responsive-xl-8 table-responsive-col-lg-4', table_id='nikeSales_table', border=0, render_links=True)

    create_csv_dir_path_tocsv, now_timestamp = csv_path_maker('nikeSales', current_user.username)
    current_df_scraped.to_csv(create_csv_dir_path_tocsv, index=False)
    return render_template('scraped_data_nikeSales.html', title='Scraped Nike Sales Page', table=current_df_html_send, now_timestamp=now_timestamp)


@app.route('/nikeSales/download-scraped-data-nikeSales/<current_username>', methods=['POST', 'GET'])
def download_scraped_data_nikeSales(current_username):
    if request.method == 'POST':
        input_form = request.form
        csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv = csv_path_retriever('nikeSales', current_username,input_form['nikeSales_csv_download'])
        try:
            return send_from_directory(create_csv_dir_path, create_csv_dir_path_tocsv, filename=csv_filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Nike Sales Page', category='danger')
        return redirect(url_for('nikeSales'))


@app.route('/nikeSales/email-scraped-data-nikeSales/<current_username>', methods=['POST', 'GET'])
def email_scraped_data_nikeSales(current_username):
    if request.method == 'POST':
        input_form = request.form
        try:
            return mail_the_user('nikeSales', current_username, current_user.email, input_form['nikeSales_csv_email'])
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Nike Sales Page', category='danger')
        return redirect(url_for('nikeSales'))


@app.route('/tokopedia')
@login_required
def tokopedia():
    return render_template('tokopedia.html', title='Tokopedia Page')


@app.route('/tokopedia/scraped-data-tokopedia', methods=['POST', 'GET'])
def scraped_data_tokopedia():
    if request.method == 'POST':
        input_form = request.form
        current_df_scraped = tokopedia_func(input_form['tokopediaPage'])

        if len(current_df_scraped) == 0:
            flash('Invalid Link', category='danger')
            return redirect(url_for('tokopedia'))
        else:
            current_df_html_send = current_df_scraped.to_html(float_format=lambda x: 'IDR {:,}'.format(x),
                                                              classes='table table-striped table-sm table-responsive table-responsive-xl-8 table-responsive-col-lg-4',
                                                              table_id='tokopedia_table', border=0, render_links=True)

    create_csv_dir_path_tocsv, now_timestamp = csv_path_maker('tokopedia', current_user.username)
    current_df_scraped.to_csv(create_csv_dir_path_tocsv, index=False)
    return render_template('scraped_data_tokopedia.html', title='Scraped Tokopedia Page', table=current_df_html_send, now_timestamp=now_timestamp)


@app.route('/tokopedia/download-scraped-data-tokopedia/<current_username>', methods=['POST', 'GET'])
def download_scraped_data_tokopedia(current_username):
    if request.method == 'POST':
        input_form = request.form
        csv_filename, create_csv_dir_path, create_csv_dir_path_tocsv = csv_path_retriever('tokopedia', current_username, input_form['tokopedia_csv_download'])
        try:
            return send_from_directory(create_csv_dir_path, create_csv_dir_path_tocsv, filename=csv_filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Tokopedia Page', category='danger')
        return redirect(url_for('tokopedia'))


@app.route('/tokopedia/email-scraped-data-tokopedia/<current_username>', methods=['POST', 'GET'])
def email_scraped_data_tokopedia(current_username):
    if request.method == 'POST':
        input_form = request.form
        try:
            return mail_the_user('tokopedia', current_username, current_user.email, input_form['tokopedia_csv_email'])
        except FileNotFoundError:
            abort(404)
    else:
        flash('There is an error, returning to Tokopedia Page', category='danger')
        return redirect(url_for('tokopedia'))



















