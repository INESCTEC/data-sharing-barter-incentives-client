FROM python:3.10

WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements
COPY requirements.txt requirements.txt

RUN export LD_LIBRARY_PATH=/usr/local/lib
RUN apt-get update && apt-get install -y build-essential

# Accept GITLAB_TOKEN as a build-time argument
ARG GITLAB_TOKEN

# Use the argument to set the Git configuration for HTTPS cloning
RUN git config --global url."https://oauth2:${GITLAB_TOKEN}@gitlab.inesctec.pt/".insteadOf "https://gitlab.inesctec.pt/"

# update PIP
RUN pip install --upgrade pip
# install required packages
RUN pip install -r requirements.txt

# copy project
# copy project
COPY . /app
# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]