"""
Primary Flask app

"""
import os
from flask import Flask, render_template, request
from flask_cors import CORS

from PIL import Image 

from .api import api as api_blueprint
from .errors import add_error_handlers
from .utils import serve_pil_image

from .imaging.filters import filter_dict
from .imaging.enhance import enhance_dict
from .imaging.quantize import quantize_dict

def create_app():
    app = Flask(__name__, static_url_path='', 
        static_folder='web/static', template_folder='web/templates'
    )
    CORS(app, resources={r'/*': {'origins': '*'}})
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    add_error_handlers(app)
    return app

application = create_app()
application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@application.route("/")
@application.route("/index.html")
def index_page():
    return render_template('index.html')

@application.route("/stitch.html")
def stitch_page():
    return render_template('stitch.html')

@application.route("/uploadmultiple", methods=["GET", "POST"])
def recieve_multiple_files():
    """ Recieve uploaded files from client.

    Returns:
        Response consisting of the processed image file and status code.
    """
    
    uploaded_files = request.files.getlist('file')  # get list of files uploaded

    file_ordering = request.values.get('order').split(',')
    file_ordering = [int(x) for x in file_ordering]

    files = [uploaded_files[i] for i in file_ordering]

    img_file = files[0]
    file_extention = img_file.filename.split('.')[-1]  # get file extension
    print('File received', img_file.filename)
    print('File extension', file_extention)
    
    with Image.open(img_file.stream) as img:
        # process PIL image (plugin processing functions here)
        img = to_gray(img)
        
        return serve_pil_image(img, file_extention), 200

@application.route("/uploadsingle", methods=["GET", "POST"])
def recieve_single_file():
    """ Recieve single uploaded file from client

    Returns:
        Response consisting of the processed image file and status code.
    """
    
    print(request.files)
    uploaded_file = request.files.get('file')
    image_op = request.values.get('op')
    op_magnitude = request.values.get('mag')
    print(image_op, op_magnitude)
    if op_magnitude:
        op_magnitude = float(op_magnitude)
    file_extention = uploaded_file.filename.split('.')[-1]  # get file extension
    print('File received', uploaded_file.filename)
    print('File extension', file_extention)
    with Image.open(uploaded_file.stream) as img:
        # process PIL image (plugin processing functions here)
        if "filter" in image_op:
            f = filter_dict[image_op]
            img = f(img)
        elif "enhance" in image_op:
            f = enhance_dict[image_op]
            img = f(img, op_magnitude)
        elif "quantize" in image_op:
            f = quantize_dict[image_op]
            img = f(img, int(op_magnitude))
        
        return serve_pil_image(img, file_extention), 200