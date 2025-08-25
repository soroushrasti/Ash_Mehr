FROM python:3.12-slim

COPY . /app
WORKDIR /app
RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "src/main.py"]
EXPOSE 8080
