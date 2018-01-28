FROM python:3.6
COPY . ./webapp
WORKDIR webapp
RUN pip install -r requirements.txt
RUN pwd
RUN ls
ENTRYPOINT python main.py