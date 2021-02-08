There is a compatibility issue with current versions of Werkzeug and flask_upload
to fix: 
 - pip3 install -r requirements.txt
 - python3 -m venv venv
 - source venv/bin/activate
 - in file-directory go to venv -> lib/python3.9/site... -> flask_uploads.py
 - on line 26 +/- locate the following 
    - from werkzeug import secure_filename, FileStorage
 - and replace with: 
    - from werkzeug.utils import secure_filename
    - from werkzeug.datastructures import  FileStorage

 - before typing flask run into your CLI
    - source .env

