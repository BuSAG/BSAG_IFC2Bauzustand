# Use Case Dokumentation

**Titel DE:** Modellbasierte Darstellung Bauzustand\
**Titel EN:** Modelbased visualization of construction stages

**Kurztext DE:**\
Der Use Case ermöglicht die Darstellung von Bauzuständen in IFC-Modellen
basierend auf Eigenschaften und unter Verwendung etablierter
Darstellungslogiken für Bauphasenpläne.  

### Zusammenfassung
Der Use Case ermöglicht die Visualisierung geplanter Bauzustände anhand
von modellinternen Eigenschaften. Die Modelle müssen im IFC-Format
(IFC2x3, IFC4 oder IFC4.3) vorliegen. Die Methode benötigt keine
gesonderten Teilmodelle oder Simulationen und basiert auf regelbasierten
Klassifikationen.
Ein bereitgestelltes Tool erzeugt SmartViews für BIMcollab ZOOM, welche
als BCF oder Screenshots weiterverwendet werden können. Ziel ist es, die
Planung, Kommunikation und Mengenermittlung je Bauphase zu optimieren.

### Beschreibung
Der Use Case ist im Hoch- und Infrastrukturbau einsetzbar. Grundlage
sind zwei Eigenschaften:

-   **CH_Ing_Uebergeordnet.Bauphase** (Dezimalzahl, \>= 0)\
-   **CH_Ing_Uebergeordnet.Rueckbauphase** (Dezimalzahl, \>= 0)

Daraus wird pro Phase der Status der Bauteile bestimmt, z. B.:
- Bestand --> Grau 
- In Erstellung --> Rot 
- In Vorphasen erstellt --> Schwarz 
- Abbruch  --> Gelb

Die Visualisierung erfolgt über gängige Farbkonventionen.

Nicht informierte Elemente bleiben unverändert sichtbar.

### Lieferleistung / Output
-   SmartView-Sets (\*.bcsv) für BIMcollab ZOOM\
-   SmartViews pro Phase\
-   Exportierbare BCF-Dateien zur Kommunikation oder Dokumentation

### Input
-   OpenBIM-konformes IFC-Modell\
-   Sämtliche relevanten Bauteile müssen die beiden Eigenschaften
    enthalten\
-   Keine besonderen Anforderungen an IFC-Struktur oder LOD

### BIM Ziele / Nutzen
-   Verständnis für Bauabläufe verbessern\
-   Mengen und Kosten je Phase ableiten\
-   Effiziente Erstellung von Bauphasenplänen

### Abgrenzung
Der Use Case dient **nicht** der Ist-Fortschrittskontrolle oder
Soll-Ist-Abgleichen.

### Voraussetzungen
-   IFC-Modell mit korrekt ausgefüllten Eigenschaften Bau- und
    Rückbauphase\
-   Fach-, Teil- oder Koordinationsmodelle sind möglich

## Prozess
### Allgemeine Beschreibung
Standardisierte Darstellung von Bau- und Rückbauzuständen anhand von
Eigenschaften.

### Geometrische Informationen
Alle Bauteile müssen im Modell vorhanden und korrekt verortet sein.

### Alphanumerische Informationen
Die Eigenschaften Bauphase und Rückbauphase steuern die Darstellung.

### Dokumentationen
Screenshots und BCF-Dateien können optional erstellt und verteilt werden.

### Betriebliche Anforderungen
Keine besonderen Anforderungen; Fokus liegt auf Planung und Ausführung.

### Informationseinschränkungen
Nicht informierte Bauteile werden nicht eingefärbt.

### Prüfoptionen
IDS-Dateien können zur Modellprüfung genutzt werden.

## Informationsanforderungen
### Notwendige Eigenschaften

  -----------------------------------------------------------------------------------------
  Property                             Datentyp              Beschreibung
  ------------------------------------ --------------------- ------------------------------
  CH_Ing_Uebergeordnet.Bauphase        Dezimalzahl (\>= 0)   Erstellphase
------------------------------------ --------------------- ------------------------------
  CH_Ing_Uebergeordnet.Rueckbauphase        Dezimalzahl (\>= 0)   Rückbauphase

