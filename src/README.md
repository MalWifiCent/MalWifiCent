# Web Server
Install server requirements:  
`pip install -r ../requirements.txt`  

Start the server:  
`sudo python3 server.py`

![webserver.png](/img/webserver.png)
Open a browser and navigate to `http://127.0.0.1:5000/`, and you should be able to see a test page.


To add new views/pages, edit src/console/views.py  
HTML templates is located under src/console/templates  
Static files such as CSS and JS should go in the src/console/static folder.  
Then in the HTML template, add this to include it:  
`{{ url_for('static', filename='name-of-style-file.css') }}`