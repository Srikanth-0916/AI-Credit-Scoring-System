FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train model at build time if not already present
RUN python data/generate_data.py && \
    cd model && python train.py && cd ..

EXPOSE 5000

CMD ["python", "api/app.py"]
