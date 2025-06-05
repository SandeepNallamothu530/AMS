FROM python:3.13
WORKDIR /app
COPY ./app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["streamlit", "run", "app.py", "--server.port", "8000", "--server.address", "0.0.0.0"]