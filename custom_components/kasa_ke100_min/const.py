from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

DOMAIN = "kasa_ke100_min"

MANUFACTURER = "TP-Link"
MODEL_KE100 = "KE100"
MODEL_KH100 = "KH100"
MODEL_T110 = "T110"

# Export der Keys, bequem für Imports in anderen Modulen
CONF_HOST = CONF_HOST
CONF_USERNAME = CONF_USERNAME
CONF_PASSWORD = CONF_PASSWORD

PLATFORMS = ["climate", "binary_sensor"]
