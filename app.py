from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
import yaml
from flask import send_from_directory
import requests
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import uuid




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './Upload'  # specify your upload directory

# Load drug information
cfg_model_path = "./runs/train/exp/weights/best.pt"
data_yaml_path = "./Frutyripe-4/data.yaml"


sa_dict = {
  "type": "service_account",
  "project_id": "frutyripe",
  "private_key_id": "6cbadb798c8c61b12e128cca8a79b0b8df8dc543",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCPqZOTii3jK9IP\nP/3y9h2YeHB0kS0oVBj7K9yoBaY7y3GWvWVXCjGcP1gwiT1Sm/LkAUsjAwj/I4ei\nu7+dLtWUJfs20QlOAtj7RETlA31L0OXYgOKFnA7Am0/3Qgr9OEONoYFojTN3WW3F\nvys0mjQikFW85ez/RwAcm5QVn5tOdtRu/hM58oQjFSud4nJLX9IF1nX/JpCUSpRy\nQU2dOWmxlCL82Jk2XGi9tEPGgnpo77uwSt1mhx0gfuyA3hUzqxvBv3hr7vWsP2JP\nd6OLX5NVYEjxt3R1APNUZ2XDyEeAMi2mJjfQktfGJMOM1j4ICyABYALcVnZ1g7tV\ngCCu9lnXAgMBAAECggEAGXZNPS+W7XYFT4WgfVDosu7Zw5c9gTHSkaXXAIKr0VpA\nAh8EWJZqb458k3GniD4yoP2nswdlL089SXbsQbAc05qduTv4Yba4fWQ+r7ZcHTVj\nn2lMfLDJnpKIbELszq+LrY0L8htgnU0g2xUEU9jm159sSsQXqrELUIa0itaUgKXk\nCq+r0Su0nCP+4NDvT3tF9BRdGYnASK8VewxTRHMawC47h8JyShO+rx2g/yZNpujE\n3YZ4oyYjNqOiZJX4ImEa5n8SquyXZPSjAaofnuIOv39mhdFoJoC9pfMMWYj4gCKT\nKSHkEp3Z+rAdocmusT5n+JWPyPn3Dnz2lo4yhqd10QKBgQDBBgAz7xSoNs5atE7T\nxyTVClIQnTG3gyRQliRgFJgm22W4MzErXydmCgiwZaSaKTw+NW5IiPvdXTYANlpg\nb8LZGBu+Xg9kSvG0Q9As4GDLstJodbb0XvSXAKdhnKAyh19y6NR5eOdhIWhpItHE\nKgG01WY1ryv/5vNWcK1eL4TpEQKBgQC+iMSaPDAVEybp19875w3DuiFE9CMGTfWb\n9bopblnCrn0PfTuFw5dVh4d49TgWjK0GymfmldUSzqCmjZ3n/9xJamAu3Rrsn2Yq\npnqYiBHXU23XjbZWiyst+U577MRO6VmJ5TiA9lV8NSXIfhxP7YGg4d4AYmhnibnW\ndorSK9NUZwKBgQCUnKQnWBnVcWzrVQuj7h2jkPCiLgULP4MEMLUM7I5AzIbCjVd8\nByT0YSFTfs5+iuUBGG4ylpUkWBGtlCt9OE8SiodByHWdSD5UBioPgynDa4ioOImG\nGF3ErRIyCz8j6CpK9Iwygi3TEL+swswydg0eR3cMOjRsMEqF8PbqHzf7oQKBgQC7\nqW+izec5yqxIJAPON0u6XMhJ5v/cRMrFOqiKCBNGiZ/Jsrn+jN+wMRXAkB4XL6V4\nC8F8PlUn+fYHNXKyv7ITaT+kyMetCW6SUXhsZZDU+Wo1pXFTGi2EUYn4ywGrC3DS\nPb+CXZ1jAeHd8EAohTBo6i5DSKm2WNN+JTGjweCavwKBgQC4+qnBekVsm11BMwIp\nJ4WM34zyZDPpyROoJLJAj49HZyByt0lBBKh9H6lv5a+lvEhGGIsWPd+IvyilTBhh\nOx6bUpI+rZh8qokHqP0gq+OOio3jVEuhbrW10aOGxCOoTF/97UQoC90bHmb3d/sl\nk183Nj5gopWoy52+UQ0UR5t37g==\n-----END PRIVATE KEY-----\n",
  "client_email": "fruityripe-storage@frutyripe.iam.gserviceaccount.com",
  "client_id": "104640580056319826912",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fruityripe-storage%40frutyripe.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
# service_account_info = json.load(open('frutyripe-6cbadb798c8c.json'))

# asd = ServiceAccountCredentials.from_json_keyfile_name('frutyripe-6cbadb798c8c.json')
credentials = service_account.Credentials.from_service_account_file(
    './frutyripe-6cbadb798c8c.json'
)

client = storage.Client(credentials=credentials, project='frutyripe')
bucket = client.get_bucket('frutyripe.appspot.com')

bucket_name = 'frutyripe.appspot.com'
file_path = './app.py'  # Ganti dengan lokasi file lokal
destination_blob_name = './files/detect'  # Ganti dengan nama folder di Google Cloud Storage
# storage_client = storage.Client.from_service_account_json('./frutyripe-6cbadb798c8c.json')

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

# Upload To GCS
def upload_to_gcs(source_file_path, destination_blob_name):
    # storage_client = storage.Client()
    # bucket = storage_client.bucket(bucket_name)


    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to {destination_blob_name}.")

file_url = upload_to_gcs(file_path, destination_blob_name)




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

            return render_template('index.html', detected_classes=detected_classes, original_img_url=original_img_url, detected_img_url=detected_img_url)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
