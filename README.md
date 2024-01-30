first clone this respository in your local

After that installation of modules like pip install flask,  pip install flask_sqlalchemy, 
pip install flask-migrate flask db init flask db migrate -m "message" flask db upgrade

then set up envirionment by command : python -m venv env

then the command to activate the virtual environment .\env\Scripts\activate

then setting the env variable set FLASK_APP=app.py set FLASK_ENV=development

then just run the application by command flask run
