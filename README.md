# 🎞️ MediaFetcher — Python Desktop Media Downloader (Research & Learning Project)

**A lightweight, open-source desktop app for saving openly-licensed media to your computer.**
Created by Kaustubh Bhattacharya (https://github.com/kaustubhbhattacharya)

MediaFetcher is a simple Windows GUI built on top of [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) and [`gallery-dl`](https://github.com/mikf/gallery-dl) that lets you paste a link from a supported open-access or Creative Commons platform and save the video, image, or gallery locally — with a clean interface, a download history, and dark mode.

---

## ✨ Features

- **One-click downloads** — paste a URL, pick a folder, done.
- **Dual-engine backend** — tries `yt-dlp` first for video; automatically falls back to `gallery-dl` for image posts and galleries.
- **Domain allow-list built in** — only accepts links from a fixed set of open-access / Creative Commons sources (see below), rejecting anything else before a request is even made.
- **Download history** — every download is logged locally (SQLite) with type, file name, and timestamp, so you can revisit or clear it anytime.
- **Live progress bar** — real-time percentage tracking for video downloads.
- **Light / dark / system theme** toggle.
- **Friendly error handling** — rate limits, 403s, and 404s are translated into plain-English messages instead of raw stack traces.

### Currently supported sources

| Platform | Type |
|---|---|
| [Wikimedia Commons](https://commons.wikimedia.org) | Public domain / CC media |
| [Internet Archive](https://archive.org) | Public domain / CC media |
| [Pexels](https://pexels.com) | Free-to-use stock media |
| [Pixabay](https://pixabay.com) | Free-to-use stock media |
| [Unsplash](https://unsplash.com) | Free-to-use stock photos |
| [Flickr](https://flickr.com) | Mixed license — verify per image |
| [X / Twitter](https://x.com) | Publicly posted media |

> The list lives in `config.py` (`SUPPORTED_DOMAINS`) and can be extended if you fork the project — see [Configuration](#️-configuration) below.

---

## 📋 Prerequisites

- **Windows 10/11** (the app uses `customtkinter` and expects a Windows-style user data folder under `%APPDATA%`)
- **Python 3.10+** if running from source
- [`gallery-dl`](https://github.com/mikf/gallery-dl) — either on your system `PATH`, or as a bundled `gallery-dl.exe` sitting next to the app (already included in this repo for convenience)

---

## 🚀 Installation

### Option A — Run from source

```bash
# 1. Clone the repository
git clone https://github.com/kaustubhbhattacharya/MediaFetcher.git
cd MediaFetcher

# 2. (Recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
python main.py
```

### Option B — Build a standalone .exe

MediaFetcher ships with a PyInstaller spec file, so you can build a single portable executable:

```bash
pip install -r build-requirements.txt
pyinstaller MediaFetcher.spec
```

The built executable will appear in the `dist/` folder. Keep `gallery-dl.exe` in the same folder as the built app so the image/gallery fallback works correctly.

---

## 🖱️ Usage

1. Launch `MediaFetcher.exe` (or `python main.py` from source).
2. Paste a URL from one of the [supported sources](#currently-supported-sources) into the input field.
3. Click **Download Media** and choose a destination folder when prompted.
4. Watch the progress bar — you'll get a success state when the file lands, or a plain-English error if something went wrong.
5. Click **Previous Downloads** at any time to view, or clear, your local download history.

There are currently no command-line flags — MediaFetcher is a GUI-first tool by design.

---

## ⚙️ Configuration

A few things you can tweak directly in `config.py`:

| Setting | What it does |
|---|---|
| `SUPPORTED_DOMAINS` | The allow-list of hostnames MediaFetcher will accept. Add or remove entries here. |
| `DEFAULT_DOWNLOAD_PATH` | Where downloads land by default (`%APPDATA%\MediaFetcher\MediaFetcher Assets\Downloads` on Windows). |
| `GALLERY_DL_PATH` | Resolved automatically — prefers a bundled `gallery-dl.exe`, falls back to whatever `gallery-dl` resolves to on `PATH`. |
| `COLORS` | Light/dark theme palette. |

Download history is stored in a local SQLite database (`download_history.db`) — no data ever leaves your machine.

---

## 🗺️ Roadmap

- [ ] Cross-platform builds (macOS / Linux)
- [ ] Batch URL downloads
- [ ] User-editable domain allow-list from within the UI
- [ ] Audio-only extraction option
- [ ] Optional download-speed / rate limiting controls

Contributions and PRs welcome — feel free to open an issue to discuss a feature before diving in.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-idea`)
3. Commit your changes
4. Open a pull request

---

## 📜 License & Disclaimer

See [DISCLAIMER.md](./DISCLAIMER.md) for the full terms of use, liability, and copyright disclaimer that governs this project. **By downloading, building, or using MediaFetcher, you agree to those terms.**
