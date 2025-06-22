import logging
from pathlib import Path
from datetime import datetime

#create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

#define log file path
now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = log_dir / f"app_{now}.log"


#configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file,encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("flask_app_logger")

logger.info("Logger is setup and working!")

def user_test_reference(username, password, debug=False):
    if debug:
        out = Path("logs")/".user_test_reference.txt"
        with out.open("a", encoding="utf-8") as f:
            f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"✅ Registered user: {username}\n")
            f.write(f"🔐 Password: {password}\n")
            f.write("-" * 40 + "\n")
            