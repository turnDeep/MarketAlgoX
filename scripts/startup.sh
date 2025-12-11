#!/bin/bash

# MarketAlgoX Startup Script

echo "Starting MarketAlgoX..."
echo "Timezone: $TZ"
echo "Current time: $(date)"

# Create log files if they don't exist
touch /app/logs/cron.log
touch /app/logs/error.log
touch /app/logs/app.log

# Start cron service
echo "Starting cron service..."
service cron start

# Verify cron is running
if pgrep cron > /dev/null; then
    echo "Cron service started successfully"
else
    echo "ERROR: Cron service failed to start"
    exit 1
fi

# Display cron jobs
echo "Active cron jobs:"
crontab -l

# Tail logs to keep container running
echo "Tailing logs..."
tail -f /app/logs/cron.log /app/logs/error.log
