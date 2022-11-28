FROM python:3.8-alpine3.14

COPY . /app/
WORKDIR /app
RUN pip install -r /app/requirements.txt
CMD ["python", "-u", "/app/hostess.py"]
