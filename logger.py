from datetime import datetime

import CONFIG

class Logger:
    def log(self, component, *args, level="INFO", **kwargs):
        log_message = f"[{datetime.now().isoformat()}] [{level}] [{component}] -> "
        log_part = [str(arg) for arg in args] + [f"{key}: {value}" for key, value in kwargs.items()]
        log_message += " | ".join(log_part)
        
        print(log_message)


logger = Logger()