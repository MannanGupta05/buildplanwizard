from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import io
from database import *
from analysis import analyze_map_with_ai
import threading
from datetime import datetime

def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return check_login

def payment_required(f):
    @wraps(f)
    def check_payment(*args, **kwargs):
        if 'current_map_id' not in session:
            flash('No map selected for analysis.', 'error')
            return redirect(url_for('upload_map'))
        
        map_id = session['current_map_id']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT payment_status FROM maps WHERE id = ? AND user_id = ?', 
                 (map_id, session['user_id']))
        result = c.fetchone()
        conn.close()
        
        if not result or result[0] != 'completed':
            flash('Payment required to proceed with analysis.', 'error')
            return redirect(url_for('payment', map_id=map_id))
        
        return f(*args, **kwargs)
    return check_payment

def register_routes(app):
    @app.route('/')
    def home():
        return redirect(url_for('welcome')) if 'user_id' in session else redirect(url_for('login'))
    
    @app.route('/welcome')
    @login_required
    def welcome():
        return render_template('welcome.html',
                               user_name=session.get('full_name', ''),
                               city=session.get('city', ''))
    
    @app.route('/change_city', methods=['GET', 'POST'])
    @login_required
    def change_city():
        if request.method == 'POST':
            new_city = request.form['city']

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('UPDATE users SET city = ? WHERE id = ?', (new_city, session['user_id']))
            conn.commit()
            conn.close()

            session['city'] = new_city
            flash(f'City changed to {new_city} successfully!', 'success')
            return redirect(url_for('welcome'))

        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad',
                'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore',
                'Thane', 'Bhopal', 'Ludhiana', 'Chandigarh', 'Amritsar', 'Patiala']
        current_city = session.get('city', '')
        return render_template('change_city.html', cities=cities, current_city=current_city)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            full_name = request.form['full_name']
            phone = request.form['phone']
            city = request.form['city']
        
            # Validation
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('register.html')
            
            # Create user
            hashed_password = generate_password_hash(password)
            user_id = create_user(username, email, hashed_password, full_name, phone, city)
            
            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                session['full_name'] = full_name
                session['city'] = city
                flash('Registration successful! Welcome to the platform.', 'success')
                return redirect(url_for('welcome'))
            else:
                flash('Username or email already exists. Please try different credentials.', 'error')
        
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad','Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal','Ludhiana', 'Chandigarh','Amritsar','Patiala']
        return render_template('register.html', cities=cities)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = verify_user(username, password)
            
            if user:
                session['user_id'] = user['id']
                session['username'] = username
                session['full_name'] = user['full_name']
                session['city'] = user['city']
                flash('Login successful! Welcome back.', 'success')
                return redirect(url_for('welcome'))
            else:
                flash('Invalid username/email or password. Please try again.', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/upload_map', methods=['GET', 'POST'])
    @login_required
    def upload_map():
        if request.method == 'POST':
            if 'map_file' not in request.files:
                flash('No file selected. Please choose a map file.', 'error')
                return redirect(request.url)
            
            file = request.files['map_file']
            if file.filename == '':
                flash('No file selected. Please choose a map file.', 'error')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload JPG, PNG, GIF, or PDF files only.', 'error')
                return redirect(request.url)
            
            # Check file size (additional check beyond Flask's MAX_CONTENT_LENGTH)
            file_size = get_file_size(file)
            if file_size > 16 * 1024 * 1024:  # 16MB
                flash('File too large. Please upload a file smaller than 16MB.', 'error')
                return redirect(request.url)
            
            if file_size == 0:
                flash('Empty file detected. Please upload a valid file.', 'error')
                return redirect(request.url)
            
            try:
                # Read file data
                file_data = file.read()
                filename = file.filename
                file_type = filename.rsplit('.', 1)[1].lower()
                
                # Insert map into database
                map_id = insert_map(session['user_id'], file_data, filename, file_type)
                session['current_map_id'] = map_id
                
                flash('Map uploaded successfully! Please proceed to payment.', 'success')
                return redirect(url_for('payment', map_id=map_id))
                
            except Exception as e:
                flash('Error uploading file. Please try again.', 'error')
                print(f"Upload error: {e}")  # Log the error
                return redirect(request.url)
        
        return render_template('upload_map.html')

    @app.route('/payment/<int:map_id>')
    @login_required
    def payment(map_id):
        # Verify map belongs to user
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, payment_status FROM maps WHERE id = ? AND user_id = ?', 
                (map_id, session['user_id']))
        map_data = c.fetchone()
        conn.close()
        
        if not map_data:
            flash('Map not found.', 'error')
            return redirect(url_for('upload_map'))
        
        if map_data[1] == 'completed':
            flash('Payment already completed for this map.', 'info')
            return redirect(url_for('check_map'))
        
        # Create payment record
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO payments (user_id, map_id, amount, status)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], map_id, 50.00, 'pending'))
        conn.commit()
        conn.close()
        
        return render_template('payment.html', map_id=map_id, amount=50.00)

    @app.route('/confirm_payment/<int:map_id>', methods=['POST'])
    @login_required
    def confirm_payment(map_id):
        transaction_id = request.form.get('transaction_id', '').strip()
    
        if not transaction_id:
            flash('Please enter the transaction ID from your payment.', 'error')
            return redirect(url_for('payment', map_id=map_id))
        
        # Update payment status
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Update payment record
        c.execute('''
            UPDATE payments SET status = 'completed', transaction_id = ?
            WHERE user_id = ? AND map_id = ? AND status = 'pending'
        ''', (transaction_id, session['user_id'], map_id))
        
        # Update map payment status
        c.execute('''
            UPDATE maps SET payment_status = 'completed'
            WHERE id = ? AND user_id = ?
        ''', (map_id, session['user_id']))
        
        conn.commit()
        conn.close()
        
        session['current_map_id'] = map_id

        # Start analysis in background thread
        def run_analysis_async(user_id, map_id):
            # Get map data
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('SELECT image, filename, file_type FROM maps WHERE id = ? AND user_id = ?', (map_id, user_id))
            map_data = c.fetchone()
            conn.close()
            if not map_data:
                return
            file_data, filename, file_type = map_data
            try:
                results, overall_status, raw_validation, validation_text = analyze_map_with_ai(file_data, filename, file_type)
                if overall_status == "error" or "error" in results:
                    error_message = results.get("error", {}).get("message", "Unknown error occurred")
                    error_report = f"Analysis Error: {error_message}\nPlease try uploading again or contact support."
                    update_map_analysis(map_id, error_report, 'error')
                else:
                    report = f"Map Analysis Report for {filename}\n"
                    report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    report += f"Overall Status: {overall_status.upper()}\n"
                    report += "\n"
                    
                    if results and any(k != "error" for k in results.keys()):
                        report += "RULE COMPLIANCE SUMMARY:\n"
                        report += "━" * 55 + "\n"
                        
                        # Define rule mapping for clean display
                        rule_mapping = {
                            'Habitable Room': 'Habitable Room (Bedroom & Drawing Room)',
                            'Bathroom': 'Bathroom',
                            'Store': 'Store Room',
                            # Add more mappings as needed for other rules
                        }
                        
                        # Counter for ordered numbering
                        rule_counter = 1
                        
                        for rule, result in results.items():
                            if rule != "error":
                                print(f"DEBUG - Rule: {rule}, Backend Result: {result['passed']}, Message: {result['message']}")
                                # Get clean rule name from mapping or use original
                                clean_rule_name = rule_mapping.get(rule, rule)
                                
                                # Extract just the pass/fail status
                                if result['passed']:
                                    status_symbol = "✅"  # Green check mark emoji
                                    status_text = "PASSED"
                                    status_display = f"  {status_symbol} {status_text}  "
                                else:
                                    status_symbol = "❌"  # Red X emoji
                                    status_text = "FAILED"
                                    status_display = f"  {status_symbol} {status_text}  "
                                
                                # Format the line cleanly
                                report += f"{rule_counter:2d}. {clean_rule_name:<40} {status_display}\n"
                                rule_counter += 1
                        report += "━" * 55 + "\n"

                    update_map_analysis(map_id, report, overall_status)
            except Exception as e:
                error_report = f"Analysis Error: {str(e)}\nPlease try uploading again or contact support."
                update_map_analysis(map_id, error_report, 'error')

        # Start thread
        thread = threading.Thread(target=run_analysis_async, args=(session['user_id'], map_id))
        thread.start()

        # Redirect to analysis progress page
        return redirect(url_for('analysis_progress', map_id=map_id))

    @app.route('/check_map')
    @login_required
    @payment_required
    def check_map():
        map_id = session['current_map_id']
    
        # Get map data
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT image, filename, file_type, status, analysis_status FROM maps WHERE id = ? AND user_id = ?', 
                (map_id, session['user_id']))
        map_data = c.fetchone()
        conn.close()
        
        if not map_data:
            flash('Map not found.', 'error')
            return redirect(url_for('upload_map'))
        
        file_data, filename, file_type, status, analysis_status = map_data
        
        # If analysis not done, perform it
        if analysis_status == 'pending':
            flash('Analysis in progress... This may take a few minutes.', 'info')
            
            try:
                # Perform actual AI analysis
                results, overall_status, raw_validation, validation_text = analyze_map_with_ai(file_data, filename, file_type)
                
                # Check if analysis failed
                if overall_status == "error" or "error" in results:
                    error_message = results.get("error", {}).get("message", "Unknown error occurred")
                    error_report = f"Analysis Error: {error_message}\nPlease try uploading again or contact support."
                    update_map_analysis(map_id, error_report, 'error')
                    status = 'error'
                    flash('Analysis failed. Please try again or contact support.', 'error')
                else:
                    # Generate report - analysis was successful
                    report = f"Map Analysis Report for {filename}\n"
                    report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    report += f"Overall Status: {overall_status.upper()}\n"
                    report += "\n"
                    
                    # Add summary if we have parsed results
                    if results and any(k != "error" for k in results.keys()):
                        report += "RULE COMPLIANCE SUMMARY:\n"
                        
                        # Define rule mapping for clean display
                        rule_mapping = {
                            'Habitable Room': 'Habitable Room (Bedroom & Drawing Room)',
                            'Bathroom': 'Bathroom',
                            'Store': 'Store Room',
                            # Add more mappings as needed for other rules
                        }
                        
                        # Counter for ordered numbering
                        rule_counter = 1
                        
                        for rule, result in results.items():
                            if rule != "error":
                                # Get clean rule name from mapping or use original
                                clean_rule_name = rule_mapping.get(rule, rule)
                                
                                # Extract just the pass/fail status
                                if result['passed']:
                                    status_symbol = "✅"  # Green check mark emoji
                                    status_text = "PASSED"
                                    status_display = f"  {status_symbol} {status_text}  "
                                else:
                                    status_symbol = "❌"  # Red X emoji
                                    status_text = "FAILED"
                                    status_display = f"  {status_symbol} {status_text}  "
                                
                                # Format the line cleanly
                                report += f"{rule_counter:2d}. {clean_rule_name:<40} {status_display}\n"
                                rule_counter += 1
                        report += "━" * 55 + "\n"
                    # Update database with successful analysis
                    update_map_analysis(map_id, report, overall_status)
                    status = overall_status
                    
                    flash(f'Analysis completed! Status: {overall_status.upper()}', 'success' if overall_status == 'approved' else 'warning')
                
            except Exception as e:
                print(f"Exception in analysis: {str(e)}")
                import traceback
                traceback.print_exc()
                error_report = f"Analysis Error: {str(e)}\nPlease try uploading again or contact support."
                update_map_analysis(map_id, error_report, 'error')
                status = 'error'
                flash('Analysis failed. Please try again or contact support.', 'error')
        
        return render_template('check_map.html', 
                            map_id=map_id, 
                            status=status,
                            analysis_completed=True)
    
    

    
    @app.route('/history')
    @login_required
    def history():
        maps = get_user_maps(session['user_id'])
        
        history_data = []
        for map_data in maps:
            history_data.append({
                'id': map_data[0],
                'status': map_data[1],
                'payment_status': map_data[2],
                'analysis_status': map_data[3],
                'created_at': map_data[4],
                'report': map_data[5],
                'filename': map_data[6]
            })
        
        return render_template('history.html', history=history_data)



    @app.route('/view_report/<int:map_id>')
    @login_required
    def view_report(map_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT report, status, filename FROM maps WHERE id = ? AND user_id = ?', 
                (map_id, session['user_id']))
        result = c.fetchone()
        conn.close()

        if not result:
            flash('Report not found.', 'error')
            return redirect(url_for('history'))

        report_text = result[0]
        status = result[1]
        filename = result[2]

        # ✅ Extract rules from the report text (basic pattern)
        rules = []
        for line in report_text.splitlines():
            line = line.strip()
            if line and any(x in line.lower() for x in ['passed', 'failed']):
                if '.' in line:
                    try:
                        _, rest = line.split('.', 1)
                        rule_name = rest.strip().rsplit(' ', 1)[0]
                        rule_status = 'Passed' if 'passed' in line.lower() else 'Failed'
                        rules.append({'name': rule_name, 'status': rule_status})
                    except ValueError:
                        continue

        return render_template('view_report.html', 
                            report=report_text, 
                            status=status,
                            filename=filename,
                            map_id=map_id,
                            rules=rules)  # ✅ pass this to the template
    
    @app.route('/submit_feedback', methods=['POST'])
    @login_required
    def submit_feedback():
        user_id = session['user_id']
        map_id = request.form['map_id']
        rule_name = request.form['rule_name']
        was_correct = bool(int(request.form['was_correct']))
        remark = request.form.get('remark', '')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO feedback (user_id, map_id, rule_name, was_correct, remark)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, map_id, rule_name, was_correct, remark))
        conn.commit()
        conn.close()

        flash(f"Feedback submitted for rule '{rule_name}'.", 'success')
        return redirect(request.referrer or url_for('view_report', map_id=map_id))

    @app.route('/view_feedback/<int:map_id>')
    @login_required
    def view_feedback(map_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            SELECT rule_name, was_correct, remark, created_at
            FROM feedback
            WHERE user_id = ? AND map_id = ?
            ORDER BY created_at DESC
        ''', (session['user_id'], map_id))
        feedbacks = c.fetchall()
        c.execute('SELECT file_type FROM maps WHERE id = ?', (map_id,))
        map_info = c.fetchone()
        conn.close()

        if not map_info:
            flash('Map not found.', 'error')
            return redirect(url_for('history'))

        return render_template('view_feedback.html',
            feedbacks=feedbacks,
            map_id=map_id,
            file_type=map_info[0])
    
    @app.route('/all_feedback')
    @login_required  # optionally add @admin_required
    def all_feedback():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            SELECT
                f.map_id,
                f.rule_name,
                f.was_correct,
                f.remark,
                f.created_at,
                u.full_name,
                u.email,
                m.file_type
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            JOIN maps m ON f.map_id = m.id
            ORDER BY f.created_at DESC
        ''')
        feedback_entries = c.fetchall()
        conn.close()

        return render_template('all_feedback.html', feedback_entries=feedback_entries)

    
        

    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def get_file_size(file):
        file.seek(0, 2)  # Move to end of file
        size = file.tell()
        file.seek(0)     # Reset to beginning
        return size

    @app.route('/analysis_progress/<int:map_id>')
    @login_required
    def analysis_progress(map_id):
        return render_template('analysis_progress.html', map_id=map_id)
    
    @app.route('/map_image/<int:map_id>')
    @login_required
    def map_image(map_id):
        import sqlite3
        import io
        import tempfile
        import os
        from flask import send_file
        from pdf2image import convert_from_path

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT image, file_type FROM maps WHERE id = ? AND user_id = ?', (map_id, session['user_id']))
        result = c.fetchone()
        conn.close()

        if not result:
            return 'File not found', 404

        file_data, file_type = result

        if file_type.lower() == 'pdf':
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(file_data)
                    temp_file_path = temp_file.name

                images = convert_from_path(temp_file_path, dpi=150)
                if images:
                    img_io = io.BytesIO()
                    images[0].save(img_io, 'PNG')
                    img_io.seek(0)
                    os.unlink(temp_file_path)
                    return send_file(img_io, mimetype='image/png')
                else:
                    os.unlink(temp_file_path)
                    return 'Could not convert PDF to image', 500

            except Exception as e:
                try: os.unlink(temp_file_path)
                except: pass
                print(f"PDF conversion error: {e}")
                return 'Error converting PDF', 500
        else:
            mime_type = f'image/{file_type.lower()}'
            if file_type.lower() == 'jpg':
                mime_type = 'image/jpeg'

            return send_file(
                io.BytesIO(file_data),
                mimetype=mime_type,
                as_attachment=False,
                download_name=f'map_image.{file_type}'
            )

    
    @app.route('/check_analysis_status/<int:map_id>')
    @login_required
    def check_analysis_status(map_id):
        import sqlite3
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT analysis_status FROM maps WHERE id = ? AND user_id = ?', (map_id, session['user_id']))
        result = c.fetchone()
        conn.close()

        analysis_completed = result and result[0] == 'completed'
        return jsonify({'analysis_completed': analysis_completed})




    @app.errorhandler(404)
    def not_found_error(error):
        flash('Page not found.', 'error')
        return redirect(url_for('home'))

    @app.errorhandler(413)
    def too_large_error(error):
        flash('File too large.', 'error')
        return redirect(url_for('upload_map'))

    @app.errorhandler(500)
    def internal_error(error):
        flash('Internal error occurred.', 'error')
        return redirect(url_for('home'))
