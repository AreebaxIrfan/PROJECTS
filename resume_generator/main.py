from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'linkedin': request.form['linkedin'],
            'website': request.form['website'],
            'intro': request.form['intro'],  # New intro field
            'education': request.form.getlist('education[]'),
            'experience': request.form.getlist('experience[]'),
            'skills': request.form.getlist('skills[]'),
            'languages': request.form.getlist('languages[]'),
            'image': None
        }

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                data['image'] = filename

        return render_template('resume.html', data=data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)