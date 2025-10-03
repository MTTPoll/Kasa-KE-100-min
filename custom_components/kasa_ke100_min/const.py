from datetime import timedelta

DOMAIN = "kasa_ke100_min"
PLATFORMS = ["climate", "binary_sensor"]

# Hersteller/Modelle (werden von climate.py/binary_sensor.py importiert)
MANUFACTURER = "TP-Link"
MODEL_KH100 = "KH100"
MODEL_KE100 = "KE100"
MODEL_T110 = "T110"

# Standard-Polling + Grenzen für Config-Flow
DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)
MIN_SCAN_INTERVAL_S = 3
MAX_SCAN_INTERVAL_S = 60
