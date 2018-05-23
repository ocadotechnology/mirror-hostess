FROM python:3.5-alpine

COPY . /app/
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python","/app/hostess.py"]
