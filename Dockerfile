FROM python:3.8-alpine
WORKDIR /SecureCity
ADD . /SecureCity


RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt
RUN pip3 install django-crispy-forms
RUN rm -f -r */migrations/0*
CMD ["python", "manage.py"]
RUN flush --no-input
RUN makemigrations
RUN migrate
RUN check


EXPOSE 5000