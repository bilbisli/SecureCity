#FROM python:3.9.7-alpine
#WORKDIR /SecureCity
#ADD . /SecureCity
#
##ADD repositories apk/repositories
##RUN apk --no-cache add musl-dev linux-headers g++
##RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
##RUN apk add --update python python-dev gfortran py-pip build-base py-numpy@community
##
##RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev
##RUN python3 -m pip install --upgrade pip setuptools wheel
#RUN pip install -r requirements.txt
#RUN pip install django-crispy-forms
##RUN pip install pandas
##RUN pip install wheel
##setuptools==62.1.0
#RUN rm -f -r */migrations/0*
#CMD ["python", "SecureCity/manage.py","flush","--no-input"]
#CMD ["python", "SecureCity/manage.py","makemigrations"]
#CMD ["python", "SecureCity/manage.py","migrate"]
##RUN python ../manage.py flush --no-input
##RUN python ./manage.py makemigrations
##RUN python ./manage.py migrate
#CMD ["python", "SecureCity/manage.py","runserver"]
#
#
#EXPOSE 5000

######
FROM python:3.9.7-alpine
WORKDIR /SecureCity
ADD . /SecureCity

RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev
RUN pip install --upgrade cython
RUN pip install --upgrade pip


ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install django-crispy-forms
#CMD gunicorn --bind 0.0.0.0:$PORT SecureCity.SecureCity.wsgi


#RUN pip install pandas
#RUN pip install wheel
#RUN rm -f -r */migrations/0*
#CMD ["python", "SecureCity/manage.py","flush","--no-input"]
#CMD ["python", "SecureCity/manage.py","makemigrations"]
#CMD ["python", "SecureCity/manage.py","migrate"]
#WORKDIR /SecureCity/SecureCity
#RUN gunicorn SecureCity.wsgi

#EXPOSE 5000