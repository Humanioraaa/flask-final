from flask import Flask, request, render_template, redirect, url_for, make_response
from werkzeug.utils import secure_filename
import os
import subprocess
import yaml
from flask import send_from_directory





app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './Upload'  # specify your upload directory

# Load drug information
cfg_model_path = "./runs/train/exp/weights/best.pt"
data_yaml_path = "./Frutyripe-4/data.yaml"



# Load class names from YAML
def load_class_names(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
        return data['names']

class_names = load_class_names(data_yaml_path)

# Get the latest directory
def get_latest_directory(base_path):
    exp_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('exp')]
    if not exp_dirs:
        return None
    return os.path.join(base_path, max(exp_dirs, key=lambda d: int(d[3:]) if d != 'exp' else 0))

# Run detection
def run_detection(image_path):
    if image_path is None:
        raise ValueError("image_path is None")
    output_base_dir = './runs/detect'
    # Ensure the output directory exists
    os.makedirs(output_base_dir, exist_ok=True)
    subprocess.run([
        'python', './detect.py',
        '--weights', cfg_model_path,
        '--data', data_yaml_path,
        '--img', '512',
        '--conf', '0.4',
        '--source', image_path,
        '--save-txt',
        '--save-conf',
    ])
    return get_latest_directory(output_base_dir)

def read_detected_classes(detected_image_dir, label_dir='labels'):
    detected_classes = set()
    label_path = os.path.join(detected_image_dir, label_dir)
    for file in os.listdir(label_path):
        if file.endswith('.txt'):
            with open(os.path.join(label_path, file), 'r') as f:
                lines = f.readlines()
                for line in lines:
                    class_id = int(line.split()[0])
                    detected_classes.add(class_names[class_id])
    return detected_classes


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/detections/<path:filename>')
def detected_file(filename):
    return send_from_directory('./runs/detect', filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            detected_image_dir = run_detection(imgpath)
            detected_classes = read_detected_classes(detected_image_dir)

            original_img_url = url_for('uploaded_file', filename=filename)
            # Asumsi bahwa gambar hasil deteksi disimpan dengan nama yang sama di direktori output
            detected_img_url = url_for('detected_file', filename=os.path.basename(detected_image_dir) + '/' + filename)

            # list_class = list(detected_classes)
            
            # data = {'detected_classes': list_class, 'original_img_url' : original_img_url, 'detected_img_url' : detected_img_url}
            # response = make_response(jsonify(data))
            # return response
            return render_template('index.html', detected_classes=detected_classes, original_img_url=original_img_url, detected_img_url=detected_img_url)
            return jsonify(detected_classes=detected_classes, original_img_url=original_img_url, detected_img_url=detected_img_url)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
