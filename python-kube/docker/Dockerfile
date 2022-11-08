FROM python:3.9.7

# Create a user
RUN adduser app

WORKDIR /app
COPY --chown=app ../pykube/requirements.txt requirements.txt
COPY --chown=app ../pykube/pykube .

USER app
RUN pip install -r requirements.txt

EXPOSE 5050/tcp

ENV APP_ENV=${APP_ENV}

ENTRYPOINT ["python", "main.py"]