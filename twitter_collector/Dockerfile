FROM python:3.6-slim
WORKDIR /app
ADD . /app
ADD requirements.txt /app
ADD credentials.py /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["python", "get_tweets.py"]
