# Bulk Downloader for Reddit
#
# VERSION               0.0.1

FROM python:3.8-slim-buster
LABEL Description="This image enables running Buld Downloader for Reddit with in a container environment" Version="0.0.1"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8080
EXPOSE 7634

# Install dependencies for building Python packages
RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*
  
# Requirements are installed here to ensure they will be cached.
COPY requirements.txt /requirements.txt 
RUN pip install --no-cache-dir -r /requirements.txt \
    && rm -rf /requirements.txt

# Copy project files into container
COPY . /bdfr
WORKDIR /bdfr

# This is useful because the image name can double as a reference to the binary 
ENTRYPOINT ["python", "script.py"]
CMD ["--help"]
