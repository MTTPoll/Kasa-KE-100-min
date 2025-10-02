DOMAIN = "kasa_ke100_min"

# Wir spiegeln Matter-Entities, daher ist Polling optional – behalten aber ein Intervall bei
DEFAULT_POLL_INTERVAL = 30

MANUFACTURER = "TP-Link"
MODEL_KE100 = "KE100"
MODEL_KH100 = "KH100"
MODEL_T110 = "T110"

PLATFORMS = ["climate", "binary_sensor"]
# Konfigurations-Schlüssel
CONF_CLIMATE = "matter_climate_entity_id"
CONF_CONTACTS = "matter_contact_entity_ids"
