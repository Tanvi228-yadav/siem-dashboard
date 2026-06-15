FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "3", "app:app"]
