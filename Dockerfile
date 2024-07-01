FROM python:3.12-slim

WORKDIR /github/workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .

RUN echo "Contents of /github/workspace:" && ls -la /github/workspace
RUN echo "Python version:" && python --version

ENTRYPOINT ["sh", "-c", "echo 'Current directory:' && pwd && echo 'Directory contents:' && ls -la && python main.py"]
