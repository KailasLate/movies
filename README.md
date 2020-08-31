# movies

# clone the project using the 
	git clone https://github.com/KailasLate/movies.git/

# Create the enviroment using
	python3 -m venv envmovie

# activate the enviroment using
	source envmovie/bin/activate

# install all required packages
	pip install -r requirements.txt

# Do the migration 
	python manage.py makemigrations -- movies_app
	python manage.py migrate

# Now, create the super user
	python manage.py createsuperuser
	follow the instructions

# add the application using admin login
	127.0.0.1:8000/admin
	update the app key and secret key same like added in settings.py


# Login
		127.0.0.1:8000/api/v1/login

# Logout 
		127.0.0.1:8000/api/v1/logout

# Movies
	List:	127.0.0.1:8000/api/v1/movies/
	Retrive: 127.0.0.1:8000/api/v1/movies/1/
	Create: 127.0.0.1:8000/api/v1/movies/
	Update: 127.0.0.1:8000/api/v1/movies/1/
	DELETE: 127.0.0.1:8000/api/v1/movies/1/

