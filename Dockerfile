FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

COPY requirements.txt /
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir /app
COPY src/ app/

ARG VERSION=0.0.1
ENV VERSION=${VERSION}
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
