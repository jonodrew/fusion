FROM python:3.6
WORKDIR match-post-service
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN pip install -r requirements.txt
COPY app app
COPY migrations migrations
COPY config.py fusion.py deploy.sh ./
RUN chmod +x deploy.sh
ENV FLASK_APP fusion.py
EXPOSE 5000
ENTRYPOINT ["./deploy.sh"]