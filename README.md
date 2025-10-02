# KASA KE100 Thermostat – HA Integration

Dieses Projekt integriert das **TP-Link Kasa KE100 Thermostat** (über den KH100 Hub) in **Home Assistant**. 
Die Integration arbeitet als **Matter-Proxy**: Sie koppelt sich an bereits in Home Assistant eingebundene **Matter-Entities** (KH100/KE100, optional Tür-/Fenstersensoren) und spiegelt deren Status pushend in eigene Entities. Setpoints werden über HA-Services direkt an die Matter-Entities geschrieben.

---

## ✨ Features
- **Climate-Entity** für KE100 Heizkörperthermostat:
  - Ist-Temperatur (°C)
  - Soll-Temperatur setzen (5–30 °C, Ganzzahl)
  - Heizmodus: `heat` / `off`
  - HVAC-Action: `heating` / `idle` / `off`
- **Binary Sensor** (optional) für Tür-/Fenstersensoren:
  - Einbindung als `binary_sensor` mit `device_class: door`
- **Config Flow** (UI):
  - Zuordnung der **Matter-Climate-Entity-ID**
  - Optional: CSV-Liste von Contact-Sensor-Entity-IDs
- **Push-Updates** über die bestehende HA-Matter-Integration (keine eigene Matter-Stack-Implementierung nötig)

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
1. **KH100/KE100 per Matter in Home Assistant einbinden.**
2. In Home Assistant → Einstellungen → Geräte & Dienste → Integration hinzufügen → **KASA KE100 (Matter Proxy)**.
3. **Entity-ID** des Matter-Thermostats eintragen (z. B. `climate.kh100_radiator`). Optional: CSV der Tür-/Fenstersensoren (z. B. `binary_sensor.bad_fenster,binary_sensor.balkon_tuer`).
4. Fertig. Änderungen an Thermostat/Sensoren kommen **sofort** in der Integration an; Setpoints aus der Integration werden direkt übernommen.

---

## 🚀 Nutzung
- In der **HA-Oberfläche** die Soll-Temperatur setzen → wird an die Matter-Climate-Entity übergeben.
- Status (aktuelle Temperatur, HVAC-Action, Türkontakt) wird **pushend** aktualisiert.
- Automationen können auf den gespiegelt sichtbaren Entities erstellt werden.

---

## 🔧 Bekannte Hinweise
- Die Integration spiegelt Matter. Bitte stelle sicher, dass die entsprechenden **Matter-Entities** in Home Assistant vorhanden sind.
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
