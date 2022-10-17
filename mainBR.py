from pathlib import Path
import os
from flask import Flask,  request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from natsort import natsorted
from BRopenCV import  pdfconvert
import shutil

app = Flask(__name__)
ALLOWED_EXTENSIONS_PDF = {'pdf'}
app.config['UPLOAD_FOLDER'] = str(Path(__file__).parent)

def allowed_file_pdf(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PDF

@app.route('/', methods=("POST", "GET"))
def index():
    return redirect("./doccheck", code=302)

@app.route('/doccheck', methods=['GET', 'POST'])
def doccheck():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file_pdf(file.filename):
            try:
                shutil.rmtree(str(Path(__file__).parent) + '\\static\\Tempimgstore\\')
            except:
                print('No Tempimgstore')
            try:
                os.mkdir(str(Path(__file__).parent) + '\\static\\Tempimgstore\\')
            except:
                print('Tempimgstore exist')
            filename = secure_filename(file.filename)
            file.save(str(Path(__file__).parent) + '\\PDFUpload\\' + filename)
            app.logger.info('Start BR checker on '+ filename)
            try:
                pdfconvert(filename)
            except Exception as Argument:
                app.logger.info(str(Argument))

            return redirect(url_for('docdisplay', name=filename))
    return render_template('doccheck.html')

@app.route('/docdisplay', methods=['GET', 'POST'])
def docdisplay():
    if request.method == 'GET':
        image_names = os.listdir(str(Path(__file__).parent) + '\\static\\Tempimgstore\\')
        image_names = natsorted(image_names)
        return render_template('docdisplay.html', image_names=image_names)


if __name__ == '__main__':
    app.run()
