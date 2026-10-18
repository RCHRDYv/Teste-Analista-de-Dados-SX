# Imagem única da aplicação: ETL (pandas), job PySpark, QA e notebook.
FROM python:3.11-slim-bookworm

# O PySpark roda sobre a JVM, por isso o Java 17 headless
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dados brutos e intermediários ficam num volume montado em /data
ENV DATA_DIR=/data \
    PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.etl.main"]
