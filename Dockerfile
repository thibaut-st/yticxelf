FROM python:3.14-slim
WORKDIR /usr/local/app

# Install the application dependencies
COPY ./requirements.txt /usr/local/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY . /usr/local/app
EXPOSE 8000

RUN python -m data.load_sample_assets


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]