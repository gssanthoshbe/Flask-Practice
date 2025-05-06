FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN flask db migrate 
RUN flask db upgrade   
CMD ["gunicorn", "--bind", "0.0.0.0:80","app:create_app()"]