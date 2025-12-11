# Use Python 3.12 slim
FROM python:3.12-slim

# Set timezone to Asia/Tokyo
ENV TZ=Asia/Tokyo
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/data/screener_results

# Setup cron job
COPY cron/marketalgox /etc/cron.d/marketalgox
RUN chmod 0644 /etc/cron.d/marketalgox && \
    crontab /etc/cron.d/marketalgox

# Make startup script executable
COPY scripts/startup.sh /app/scripts/startup.sh
RUN chmod +x /app/scripts/startup.sh

# Start cron and keep container running
CMD ["/app/scripts/startup.sh"]