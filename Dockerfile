FROM python:3.7

WORKDIR /usr/src/app

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/*.py ./

CMD ["python3", "./a.py"]
