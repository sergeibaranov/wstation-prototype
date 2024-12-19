# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Install production dependencies.
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . ./

# Run start up script (initialize database and start server)
RUN chmod +x ./startup.sh
CMD ["./startup.sh"]
