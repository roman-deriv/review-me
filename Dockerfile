FROM python:3.12-slim

WORKDIR /github/workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .

ENTRYPOINT ["python", "main.py"]
