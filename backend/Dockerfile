FROM python:3.13.4-slim-bullseye

RUN apt-get update && apt-get install -y curl

# Create python venv
RUN python -m venv /opt/venv/
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /app

COPY /requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src .

CMD ["python", "-m", "http.server", "8000"]