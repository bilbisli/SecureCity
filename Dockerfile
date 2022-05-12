FROM python:3.8-alpine
WORKDIR /SecureCity
ADD . /SecureCity

RUN apk --no-cache add musl-dev linux-headers g++
RUN apk update && apk gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev
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