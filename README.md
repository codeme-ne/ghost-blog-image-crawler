# Ghost Blog Media Crawler

Dieses Script crawlt alle **Bilder und Videos** von www.produktiv.me mit der Firecrawl API und speichert sie **sortiert nach Artikel-Slug** für einfache Migration.

## 🎯 Ziel

Alle Medien (Bilder + Videos) vor der Ghost.org Pro Kündigung herunterladen und **nach Artikel organisieren** für Self-Hosting Migration.

## 📋 Voraussetzungen

- Python 3.8+
- Firecrawl API Key (von [firecrawl.dev](https://firecrawl.dev))

## 🚀 Setup

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. API Key konfigurieren

Erstelle eine `.env` Datei im Projektordner:

```bash
FIRECRAWL_API_KEY=fc-dein-api-key-hier
```

**WICHTIG:** Die `.env` Datei ist in `.gitignore` und wird NICHT committed!

## 💻 Usage

### Dry-Run Test (empfohlen zuerst!)

Zeigt nur gefundene Bild-URLs an, lädt nichts herunter:

```bash
python crawl_images.py --limit 10 --dry-run
```

### Test-Download (10 Seiten)

Crawlt 10 Seiten und lädt gefundene Bilder herunter:

```bash
python crawl_images.py --limit 10
```

### Production (alle Bilder)

Crawlt die komplette Website:

```bash
python crawl_images.py --limit 1000
```

### Alle Optionen

```bash
python crawl_images.py --help

Options:
  --url URL             Blog URL (default: https://www.produktiv.me)
  --limit N             Max Seiten zu crawlen (default: 100)
  --dry-run             Nur URLs anzeigen, nicht downloaden
  --output-dir PATH     Output-Verzeichnis (default: ./images)
```

## 📁 Output-Struktur

Medien werden **nach Artikel-Slug** organisiert für einfache Migration:

```
images/
├── artikel-slug-1/
│   ├── header-image.jpg
│   ├── content-image-1.png
│   └── video.mp4              # 🎬 Videos werden auch heruntergeladen!
├── rezensionen/
│   ├── testimonial.jpg
│   ├── demo-video.mp4         # 🎬 Videos
│   └── demo-video_thumb.jpg   # 📸 Automatisch extrahierte Thumbnails
├── _homepage/
│   └── logo.png
└── _shared/
    └── shared-media.png       # Medien die auf mehreren Seiten erscheinen
```

**Vorteile:**

- ✅ Einfache Zuordnung: Jeder Ordner = ein Artikel
- ✅ Direkte Migration: Medien können direkt in den entsprechenden Artikel eingefügt werden
- ✅ Übersichtlich: Keine Datums-basierte Suche mehr nötig
- ✅ Automatische Erkennung von geteilten Medien (z.B. Logos, Icons)
- ✅ **Videos werden mitgeladen**: Alle `.mp4`, `.webm`, `.mov` Videos werden heruntergeladen
- ✅ **Thumbnails extrahiert**: Video-Thumbnails aus `style` Attributen werden automatisch gespeichert

## ✨ Features

- ✅ **Parallele Downloads** - 10 gleichzeitige Downloads für Geschwindigkeit
- ✅ **Resume-Fähigkeit** - Überspringt bereits heruntergeladene Medien
- ✅ **Robustes Error Handling** - Einzelne Fehler stoppen nicht den Prozess
- ✅ **Streaming Downloads** - Speichereffizient auch für große Videos
- ✅ **Video Support** - Automatische Erkennung von `.mp4`, `.webm`, `.mov` Videos
- ✅ **Thumbnail Extraktion** - Video-Thumbnails werden aus HTML `style` Attributen extrahiert
- ✅ **Logging** - Detaillierte Logs über erfolgreiche/fehlgeschlagene Downloads
- ✅ **Slug-basiert** - Medien nach Artikel organisiert statt nach Datum

## 🧪 Empfohlener Test-Ablauf

1. **Dry-Run** - URLs validieren:
   ```bash
   python crawl_images.py --limit 10 --dry-run
   ```

2. **Test-Download** - 10 Bilder testen:
   ```bash
   python crawl_images.py --limit 10
   ```

3. **Validierung** - Prüfe `images/` Ordner

4. **Production** - Alle Bilder:
   ```bash
   python crawl_images.py --limit 1000
   ```

## 🛠️ Technische Details

- **Firecrawl API v2** mit HTML-Format für Bild-Extraktion
- **BeautifulSoup4** für robustes HTML-Parsing
- **ThreadPoolExecutor** für parallele Downloads
- **Streaming Downloads** mit `requests` Library
- **OpenBSD-Style** - Minimalistisch, unter 20 Zeilen pro Funktion

## 📝 Logs

Logs werden in der Console ausgegeben:

```
2025-10-08 10:30:15 - INFO - Starting crawl of https://www.produktiv.me with limit=10
2025-10-08 10:30:45 - INFO - Crawl completed. Found 10 pages
2025-10-08 10:30:46 - INFO - Extracted 23 unique image URLs
2025-10-08 10:30:46 - INFO - Starting download of 23 images to ./images
2025-10-08 10:30:47 - INFO - Downloaded: image-6.png
...
```

## 🔒 Sicherheit

- API Keys werden in `.env` gespeichert (nicht in Git)
- User-Agent Header verhindert Bot-Blockierung
- Timeout verhindert hängende Requests

## 📄 Lizenz

Utility-Script für persönlichen Gebrauch.
