FROM python:3.11.8

EXPOSE 8080
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "mortgage.py", "--server.port=8080", "--server.address=0.0.0.0"]