FROM python:3.6
COPY . ./webapp
WORKDIR webapp
RUN pip install -r requirements.txt
RUN pwd
RUN ls
ENV FLASK_APP fusion.py
CMD ["flask", "run", "--host=0.0.0.0"]