FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
# if you have issues installing packages use the command below instead
# RUN pip install -i https://package-mirror.liara.ir/repository/pypi/simple --upgrade pip
COPY backend/requirements.txt .

RUN pip install -r requirements.txt
# if you have issues installing packages use the command below instead
# RUN pip install -i https://package-mirror.liara.ir/repository/pypi/simple -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]