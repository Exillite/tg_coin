FROM python:3.11.7-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache gcc musl-dev linux-headers
RUN python3 -m pip install wheel
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install uvicorn[standard]

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY . .

EXPOSE 8000