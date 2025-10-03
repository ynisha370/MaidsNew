#!/usr/bin/env python3
"""
Automated Email Reminders Runner
This script can be run as a cron job to send automated email reminders
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.automated_reminders import run_scheduled_reminders
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_reminders.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """
    Main function to run automated reminders
    """
    try:
        logger.info("Starting automated reminder process...")
        
        # Run the scheduled reminders
        results = await run_scheduled_reminders()
        
        if "error" in results:
            logger.error(f"Automated reminders failed: {results['error']}")
            sys.exit(1)
        else:
            logger.info(f"Automated reminders completed successfully: {results}")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Unexpected error in automated reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
