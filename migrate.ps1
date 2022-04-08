& ./env/Scripts/activate.ps1
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations users
python manage.py migrate users