# CONTRIBUTING

## How to run the docker locally

 docker run -dp 5000:5000 -w /app -v "$(pwd):/app" flask-practice sh -c "flask run"