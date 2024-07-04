FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PRODUCTION=True

EXPOSE 5000

CMD ["python", "run.py"]
