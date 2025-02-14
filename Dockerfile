FROM python:alpine

RUN apk add --no-cache tini

ADD requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm -rf /tmp/requirements.txt

ADD metrics.py /app/metrics.py

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "/app/metrics.py"]