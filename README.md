# KASA KE100 Thermostat – HA Integration

Dieses Projekt integriert das **TP-Link Kasa KE100 Thermostat** (über den KH100 Hub) sowie unterstützende Geräte (z. B. Tapo T110 Tür-/Fenstersensor) in **Home Assistant**.

---

## ✨ Features
- **Climate-Entity** für KE100 Heizkörperthermostat:
  - Ist-Temperatur (°C)
  - Soll-Temperatur setzen (5–30 °C, Ganzzahl)
  - Heizmodus: `heat` / `off`
  - HVAC-Action: `heating` / `idle` / `off`
- **Binary Sensor** für Tapo T110 (Tür/Fenster):
  - Gerät wird als `binary_sensor` mit `device_class: door` eingebunden
- **Diagnostics**:
  - Diagnosedaten anonymisiert abrufbar
- **Config Flow**:
  - Einrichtung über Home Assistant UI (IP-Adresse des KH100)
  - Optionen: Poll-Intervall einstellen
- **HACS Support**

---

## 📦 Installation
### Über HACS
1. In HACS → Integrationen → „Benutzerdefiniertes Repository“ hinzufügen: `https://github.com/MTTPoll/Kasa-KE-100-min`
2. Typ: **Integration** auswählen.
3. Integration installieren und Home Assistant neu starten.

### Manuell
1. Repository clonen oder ZIP herunterladen.
2. Inhalt in den Ordner `custom_components/kasa_ke100_min` kopieren.
3. Home Assistant neu starten.

---

## ⚙️ Einrichtung
1. In Home Assistant → Einstellungen → Geräte & Dienste → Integration hinzufügen.
2. „**KASA KE100 Thermostat – HA Integration**“ auswählen.
3. IP-Adresse des KH100-Hubs eintragen.
4. Nach erfolgreichem Setup erscheinen Thermostat, Sensoren und ggf. Tapo T110 als Entities.

---

## 🚀 Nutzung
- In der **HA-Oberfläche** kann die Soll-Temperatur gesetzt werden → der KH100/KE100 übernimmt den Wert.
- Status (aktuelle Temperatur, Ventilstellung) wird regelmäßig per Poll aktualisiert.
- Binary-Sensor (z. B. Türkontakt) kann in Automationen eingebunden werden (z. B. Fenster auf → Heizung absenken).

---

## 🔧 Bekannte Einschränkungen
- Kommunikation aktuell über **lokales Polling** – Push-Events sind noch nicht implementiert.
- HVAC-Action kann je nach Firmware ungenau sein (z. B. idle vs. heating).
- Nur Ganzzahl-Sollwerte (°C).

---

## 🛣️ Roadmap
- [ ] Batterie-Status als eigener Sensor

---

## 🤝 Mitmachen
Pull Requests, Issues und Ideen sind willkommen! 🙌

Repo: [GitHub – MTTPoll/Kasa-KE-100-min](https://github.com/MTTPoll/Kasa-KE-100-min)

---

## 📜 Lizenz
MIT License – frei nutzbar, Modifikationen und Weitergabe erlaubt.
