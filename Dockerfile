FROM python:3.8-alpine
WORKDIR /SecureCity
ADD . /SecureCity

RUN pip install -r requirements.txt
#RUN python3 -m pip install --upgrade pip setuptools wheel
#RUN pip3 install -r requirements.txt
#RUN pip3 install django-crispy-forms
#RUN rm -f -r */migrations/0*
#RUN python manage.py flush --no-input
CMD ["python", "manage.py"]
#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py check


EXPOSE 5000