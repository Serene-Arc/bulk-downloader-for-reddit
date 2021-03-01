FROM python:3.9
LABEL Description="This image enables running Buld Downloader for Reddit with in a container environment" Version="0.0.1"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8080
EXPOSE 7634

# Install dependencies
RUN apt-get update \
 && apt-get install -y build-essential \
 && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
 && rm -rf /var/lib/apt/lists/*
  
# Python requirements
COPY requirements.txt /requirements.txt 
RUN pip install --no-cache-dir -r /requirements.txt \
 && rm -rf /requirements.txt

# Copy over project files
COPY . /bdfr
WORKDIR /bdfr

# Useful so the image doubles as reference to the binary 
ENTRYPOINT ["python", "script.py"]
CMD ["python", "script.py", "-d", "downloads"]
