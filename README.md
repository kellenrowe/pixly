Welcome to Pixly - where you can upload and edit your photographs. 

This was a 3 day sprint in which I was primarily focused on learning to use AWS S3 for file storage. 
I love the way the design and functionality came out and will be adding funcionality to "undo" and "delete" photos. 

Please preview the demo at http://pixly.kellen-rowe.com or to run the code yourself, please read the following:

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

