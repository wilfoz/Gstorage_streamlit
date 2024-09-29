FROM python:3.10

EXPOSE 8080

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT [ "streamlit", "run", "streamlit_home.py", "--server.port=8080", "--server.address=0.0.0.0" ]
