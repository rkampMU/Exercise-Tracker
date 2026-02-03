from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash
import bcrypt
import qrcode
import io
import base64
from datetime import datetime
import secrets
import os
import csv
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Only print debug info in development
if os.getenv('FLASK_ENV') != 'production':
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'*' * 20 if SUPABASE_KEY else 'NOT SET'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    error_msg = "❌ ERROR: Missing Supabase credentials!"
    print(error_msg)
    if os.getenv('FLASK_ENV') != 'production':
        exit(1)

try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    if os.getenv('FLASK_ENV') != 'production':
        print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Supabase: {e}")
    if os.getenv('FLASK_ENV') != 'production':
        exit(1)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login')
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Check admin credentials from Supabase
        response = supabase.table('admin').select('*').eq('username', username).execute()
        
        if response.data and len(response.data) > 0:
            admin = response.data[0]
            # Use bcrypt to verify password
            password_hash = admin['password_hash']
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            if isinstance(password, str):
                password = password.encode('utf-8')
            
            if bcrypt.checkpw(password, password_hash):
                session['admin_id'] = admin['id']
                print(f"✅ Admin login successful: {username}")
                return jsonify({'success': True})
        
        print(f"❌ Login failed for user: {username}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('admin_id', None)
    return jsonify({'success': True})

@app.route('/api/classes', methods=['GET', 'POST'])
def api_classes():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Creating class: {data['name']} - {data['code']}")
            
            response = supabase.table('class').insert({
                'name': data['name'],
                'code': data['code'],
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            if response.data and len(response.data) > 0:
                class_data = response.data[0]
                print(f"✅ Class created with ID: {class_data['id']}")
                return jsonify({
                    'id': class_data['id'],
                    'name': class_data['name'],
                    'code': class_data['code'],
                    'student_count': 0
                }), 200
            else:
                print(f"❌ No data returned from insert")
                return jsonify({'error': 'Failed to create class'}), 400
        except Exception as e:
            print(f"❌ Error creating class: {e}")
            return jsonify({'error': str(e)}), 400
    
    try:
        # GET - retrieve all classes
        response = supabase.table('class').select('*').execute()
        classes_list = []
        
        if response.data:
            for c in response.data:
                # Count students
                students_response = supabase.table('student').select('*', count='exact').eq('class_id', c['id']).execute()
                student_count = len(students_response.data) if students_response.data else 0
                
                classes_list.append({
                    'id': c['id'],
                    'name': c['name'],
                    'code': c['code'],
                    'student_count': student_count
                })
        
        print(f"✅ Retrieved {len(classes_list)} classes")
        return jsonify(classes_list), 200
    except Exception as e:
        print(f"❌ Error retrieving classes: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/classes/<int:class_id>', methods=['GET', 'PUT', 'DELETE'])
def class_detail(class_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if request.method == 'GET':
            response = supabase.table('class').select('*').eq('id', class_id).execute()
            if response.data and len(response.data) > 0:
                c = response.data[0]
                students_response = supabase.table('student').select('*').eq('class_id', class_id).execute()
                student_count = len(students_response.data) if students_response.data else 0
                return jsonify({
                    'id': c['id'],
                    'name': c['name'],
                    'code': c['code'],
                    'student_count': student_count
                }), 200
            return jsonify({'error': 'Class not found'}), 404
        
        elif request.method == 'PUT':
            data = request.get_json()
            print(f"Updating class {class_id}: {data['name']} - {data['code']}")
            
            response = supabase.table('class').update({
                'name': data.get('name'),
                'code': data.get('code')
            }).eq('id', class_id).execute()
            
            if response.data:
                c = response.data[0]
                print(f"✅ Class updated: {class_id}")
                return jsonify({
                    'id': c['id'],
                    'name': c['name'],
                    'code': c['code']
                }), 200
            return jsonify({'error': 'Failed to update class'}), 400
        
        elif request.method == 'DELETE':
            print(f"Deleting class {class_id}")
            supabase.table('student').delete().eq('class_id', class_id).execute()
            supabase.table('exercise').delete().eq('class_id', class_id).execute()
            supabase.table('class').delete().eq('id', class_id).execute()
            print(f"✅ Class deleted: {class_id}")
            return jsonify({'success': True}), 200
    
    except Exception as e:
        print(f"❌ Error in class_detail: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/classes/<int:class_id>/students', methods=['GET', 'POST'])
def api_students(class_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if request.method == 'POST':
            data = request.get_json()
            print(f"Creating student: {data['name']} ({data['email']}) for class {class_id}")
            
            response = supabase.table('student').insert({
                'email': data['email'],
                'name': data['name'],
                'class_id': class_id
            }).execute()
            
            if response.data and len(response.data) > 0:
                s = response.data[0]
                print(f"✅ Student created with ID: {s['id']}")
                return jsonify({
                    'id': s['id'],
                    'email': s['email'],
                    'name': s['name']
                }), 200
            return jsonify({'error': 'Failed to create student'}), 400
        
        # GET - retrieve all students in class
        response = supabase.table('student').select('*').eq('class_id', class_id).execute()
        students_list = response.data if response.data else []
        print(f"✅ Retrieved {len(students_list)} students for class {class_id}")
        return jsonify(students_list), 200
    
    except Exception as e:
        print(f"❌ Error in api_students: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        print(f"Deleting student {student_id}")
        supabase.table('student').delete().eq('id', student_id).execute()
        print(f"✅ Student deleted: {student_id}")
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"❌ Error deleting student: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/classes/<int:class_id>/exercises', methods=['GET', 'POST'])
def api_exercises(class_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if request.method == 'POST':
            data = request.get_json()
            qr_token = secrets.token_urlsafe(32)
            print(f"Creating exercise: {data['name']} for class {class_id}")
            
            response = supabase.table('exercise').insert({
                'name': data['name'],
                'class_id': class_id,
                'qr_token': qr_token,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            if response.data and len(response.data) > 0:
                e = response.data[0]
                print(f"✅ Exercise created with ID: {e['id']}")
                
                # Generate QR code
                qr_url = request.host_url + f'complete/{qr_token}'
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                qr_base64 = base64.b64encode(buf.getvalue()).decode()
                
                return jsonify({
                    'id': e['id'],
                    'name': e['name'],
                    'qr_code': qr_base64,
                    'qr_url': qr_url,
                    'created_at': e['created_at'],
                    'completion_count': 0
                }), 200
            return jsonify({'error': 'Failed to create exercise'}), 400
        
        # GET - retrieve all exercises for class
        response = supabase.table('exercise').select('*').eq('class_id', class_id).execute()
        result = []
        
        if response.data:
            for e in response.data:
                completions_response = supabase.table('completion').select('*').eq('exercise_id', e['id']).execute()
                completion_count = len(completions_response.data) if completions_response.data else 0
                
                result.append({
                    'id': e['id'],
                    'name': e['name'],
                    'created_at': e['created_at'],
                    'completion_count': completion_count
                })
        
        print(f"✅ Retrieved {len(result)} exercises for class {class_id}")
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ Error in api_exercises: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/exercises/<int:exercise_id>', methods=['GET', 'DELETE'])
def exercise_detail(exercise_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if request.method == 'GET':
            # Get exercise details and regenerate QR code
            print(f"Getting QR code for exercise {exercise_id}")
            response = supabase.table('exercise').select('*').eq('id', exercise_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Exercise not found'}), 404
            
            exercise = response.data[0]
            
            # Generate QR code
            qr_url = request.host_url + f'complete/{exercise["qr_token"]}'
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            qr_base64 = base64.b64encode(buf.getvalue()).decode()
            
            print(f"✅ QR code generated for exercise {exercise_id}")
            return jsonify({
                'id': exercise['id'],
                'name': exercise['name'],
                'qr_code': qr_base64,
                'qr_url': qr_url,
                'created_at': exercise['created_at']
            }), 200
        
        elif request.method == 'DELETE':
            print(f"Deleting exercise {exercise_id}")
            supabase.table('completion').delete().eq('exercise_id', exercise_id).execute()
            supabase.table('exercise').delete().eq('id', exercise_id).execute()
            print(f"✅ Exercise deleted: {exercise_id}")
            return jsonify({'success': True}), 200
    except Exception as e:
        print(f"❌ Error in exercise_detail: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/exercises/<int:exercise_id>/completions', methods=['GET'])
def get_completions(exercise_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        response = supabase.table('completion').select('*').eq('exercise_id', exercise_id).execute()
        result = []
        
        if response.data:
            for c in response.data:
                student_response = supabase.table('student').select('*').eq('id', c['student_id']).execute()
                student_name = student_response.data[0]['name'] if student_response.data else 'Unknown'
                
                result.append({
                    'id': c['id'],
                    'student_email': c['student_email'],
                    'student_name': student_name,
                    'completed_at': c['completed_at']
                })
        
        print(f"✅ Retrieved {len(result)} completions for exercise {exercise_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Error getting completions: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/exercises/<int:exercise_id>/export', methods=['GET'])
def export_exercise(exercise_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        print(f"Exporting exercise {exercise_id}")
        
        exercise_response = supabase.table('exercise').select('*').eq('id', exercise_id).execute()
        if not exercise_response.data:
            return jsonify({'error': 'Exercise not found'}), 404
        
        exercise = exercise_response.data[0]
        completions_response = supabase.table('completion').select('*').eq('exercise_id', exercise_id).execute()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student Name', 'Email', 'Completed At'])
        
        if completions_response.data:
            for c in completions_response.data:
                student_response = supabase.table('student').select('*').eq('id', c['student_id']).execute()
                student_name = student_response.data[0]['name'] if student_response.data else 'Unknown'
                
                writer.writerow([
                    student_name,
                    c['student_email'],
                    c['completed_at']
                ])
        
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        print(f"✅ Exported exercise {exercise_id}")
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{exercise['name']}_completions.csv"
        )
    except Exception as e:
        print(f"❌ Error exporting exercise: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/classes/<int:class_id>/export', methods=['GET'])
def export_class_comprehensive(class_id):
    """Export all exercises for a class in a single comprehensive CSV"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        print(f"Exporting comprehensive CSV for class {class_id}")
        
        # Get class info
        class_response = supabase.table('class').select('*').eq('id', class_id).execute()
        if not class_response.data:
            return jsonify({'error': 'Class not found'}), 404
        
        class_info = class_response.data[0]
        
        # Get all students in class
        students_response = supabase.table('student').select('*').eq('class_id', class_id).execute()
        students = {s['id']: s for s in students_response.data} if students_response.data else {}
        
        # Get all exercises for class
        exercises_response = supabase.table('exercise').select('*').eq('class_id', class_id).execute()
        exercises = exercises_response.data if exercises_response.data else []
        
        if not exercises:
            return jsonify({'error': 'No exercises found for this class'}), 404
        
        # Build comprehensive data structure
        # Key: student_id, Value: dict with student info and completion dates
        student_data = {}
        
        for student_id, student in students.items():
            student_data[student_id] = {
                'name': student['name'],
                'email': student['email'],
                'completions': {}
            }
        
        # Get completions for each exercise
        for exercise in exercises:
            completions_response = supabase.table('completion').select('*').eq('exercise_id', exercise['id']).execute()
            
            if completions_response.data:
                for completion in completions_response.data:
                    student_id = completion.get('student_id')
                    if student_id and student_id in student_data:
                        student_data[student_id]['completions'][exercise['name']] = completion['completed_at']
        
        # Create CSV with dynamic columns
        output = StringIO()
        writer = csv.writer(output)
        
        # Header row: Student Name, Email, then each exercise name
        exercise_names = [ex['name'] for ex in exercises]
        header = ['Student Name', 'Email'] + exercise_names + ['Total Completed', 'Completion Rate']
        writer.writerow(header)
        
        # Data rows
        for student_id, data in student_data.items():
            row = [data['name'], data['email']]
            
            completed_count = 0
            for exercise_name in exercise_names:
                completion_date = data['completions'].get(exercise_name, '')
                if completion_date:
                    # Format date nicely
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                        row.append(formatted_date)
                        completed_count += 1
                    except:
                        row.append(completion_date)
                        completed_count += 1
                else:
                    row.append('')
            
            # Add totals
            total_exercises = len(exercise_names)
            completion_rate = f"{(completed_count / total_exercises * 100):.1f}%" if total_exercises > 0 else "0%"
            row.append(f"{completed_count}/{total_exercises}")
            row.append(completion_rate)
            
            writer.writerow(row)
        
        # Add summary row
        writer.writerow([])
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Total Students', len(student_data)])
        writer.writerow(['Total Exercises', len(exercises)])
        
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        print(f"✅ Exported comprehensive CSV for class {class_id}")
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{class_info['name']}_all_exercises.csv"
        )
    except Exception as e:
        print(f"❌ Error exporting class: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/complete/<token>')
def complete_page(token):
    try:
        response = supabase.table('exercise').select('*').eq('qr_token', token).execute()
        
        if not response.data:
            return "Exercise not found", 404
        
        exercise = response.data[0]
        class_response = supabase.table('class').select('*').eq('id', exercise['class_id']).execute()
        class_info = class_response.data[0] if class_response.data else None
        
        return render_template('complete.html', exercise=exercise, class_info=class_info)
    except Exception as e:
        print(f"❌ Error in complete_page: {e}")
        return f"Error: {str(e)}", 500

@app.route('/api/complete/<token>', methods=['POST'])
def api_complete(token):
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        print(f"Processing completion for email: {email}, token: {token[:20]}...")
        
        # Find exercise with this token
        exercise_response = supabase.table('exercise').select('*').eq('qr_token', token).execute()
        if not exercise_response.data:
            print(f"❌ Exercise not found for token: {token}")
            return jsonify({'error': 'Exercise not found'}), 404
        
        exercise = exercise_response.data[0]
        print(f"✅ Found exercise: {exercise['name']}")
        
        # Find student with this email in this class
        student_response = supabase.table('student').select('*').eq('class_id', exercise['class_id']).eq('email', email).execute()
        if not student_response.data:
            print(f"❌ Student not found for email: {email} in class {exercise['class_id']}")
            return jsonify({'error': 'Email not found in this class'}), 404
        
        student = student_response.data[0]
        print(f"✅ Found student: {student['name']}")
        
        # Check if already completed
        existing_response = supabase.table('completion').select('*').eq('student_id', student['id']).eq('exercise_id', exercise['id']).execute()
        if existing_response.data:
            print(f"❌ Student already completed this exercise")
            return jsonify({'error': 'You have already completed this exercise'}), 400
        
        # Add completion
        completion_response = supabase.table('completion').insert({
            'student_id': student['id'],
            'exercise_id': exercise['id'],
            'student_email': email,
            'completed_at': datetime.utcnow().isoformat()
        }).execute()
        
        if completion_response.data:
            print(f"✅ Completion recorded for student {student['id']}")
            return jsonify({
                'success': True,
                'student_name': student['name'],
                'exercise_name': exercise['name']
            }), 200
        else:
            print(f"❌ Failed to record completion")
            return jsonify({'error': 'Failed to record completion'}), 400
    
    except Exception as e:
        print(f"❌ Error in api_complete: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    if os.getenv('FLASK_ENV') != 'production':
        print("\n" + "="*50)
        print("🚀 ClassTracker - Supabase Edition")
        print("="*50)
        print(f"Supabase URL: {SUPABASE_URL}")
        print("="*50 + "\n")
    
    app.run(debug=os.getenv('FLASK_ENV') != 'production', host='127.0.0.1', port=5001)
