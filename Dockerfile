FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .

ENTRYPOINT ["python", "main.py"]
