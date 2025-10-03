#!/bin/bash

# Setup Automated Email Reminders
# This script sets up cron jobs for automated email reminders

echo "🔧 Setting up Automated Email Reminders..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Make the reminder script executable
chmod +x "$BACKEND_DIR/run_automated_reminders.py"

echo "✅ Made reminder script executable"

# Create cron job entries
echo "📅 Setting up cron jobs..."

# Add cron jobs (run daily at 9 AM and 6 PM)
(crontab -l 2>/dev/null; echo "0 9 * * * cd $BACKEND_DIR && python3 run_automated_reminders.py >> automated_reminders.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 18 * * * cd $BACKEND_DIR && python3 run_automated_reminders.py >> automated_reminders.log 2>&1") | crontab -

echo "✅ Added cron jobs for automated reminders"
echo "   - Daily at 9:00 AM"
echo "   - Daily at 6:00 PM"

# Create log file
touch "$BACKEND_DIR/automated_reminders.log"
echo "✅ Created log file: $BACKEND_DIR/automated_reminders.log"

# Test the script
echo "🧪 Testing the reminder script..."
cd "$BACKEND_DIR"
python3 run_automated_reminders.py

if [ $? -eq 0 ]; then
    echo "✅ Test run successful!"
else
    echo "❌ Test run failed. Check the logs for errors."
fi

echo ""
echo "🎉 Automated Email Reminders Setup Complete!"
echo ""
echo "📋 What was set up:"
echo "   - Cron jobs for daily reminders (9 AM & 6 PM)"
echo "   - Log file for tracking reminder activity"
echo "   - Executable reminder script"
echo ""
echo "📝 To manage cron jobs:"
echo "   - View: crontab -l"
echo "   - Edit: crontab -e"
echo "   - Remove: crontab -r"
echo ""
echo "📊 To monitor reminders:"
echo "   - Check logs: tail -f $BACKEND_DIR/automated_reminders.log"
echo "   - Manual run: cd $BACKEND_DIR && python3 run_automated_reminders.py"
echo ""
echo "⚠️  Make sure your AWS SES credentials are configured in the .env file!"
