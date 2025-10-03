from datetime import timedelta

DOMAIN = "kasa_ke100_min"
PLATFORMS = ["climate", "binary_sensor"]

DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)
MIN_SCAN_INTERVAL_S = 3
MAX_SCAN_INTERVAL_S = 60
