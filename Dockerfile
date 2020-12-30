FROM python:3.8.6-slim
#RUN apk add gcc
WORKDIR /app
COPY . /app
RUN python3 -m pip install -r requirements.txt > /dev/null
CMD ["python3","-u","main.py"]
