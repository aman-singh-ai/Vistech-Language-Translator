# VishTech AI Translator

![VishTech AI Logo](assets/logo.png)

## 1. Project Overview

VishTech AI Translator is a polished, user-friendly web application for fast, accurate multilingual translation. It combines text and voice I/O, exportable reports (TXT/PDF), and a modern responsive UI — built with Streamlit and Python.

## 2. Quick Description

1. Translate text between multiple languages (auto-detect supported).
2. Record voice input (Speech-to-Text) and hear translated text with character-style voices.
3. Download translations as `.txt` or `.pdf` reports.
4. Light/Dark themes, session history, and touch-friendly mobile UI.

## 3. Live Demo

1. Local (development): http://localhost:8501
2. Network (if running on your machine): http://<your-ip>:8501

> Tip: Start the app with:

```bash
c:/Users/Lenovo/Language-Translator/venv/Scripts/python.exe -m streamlit run app.py
```

## 4. Tech Stack

1. **Frontend / App Framework:** Streamlit
2. **Language Engine:** deep-translator (GoogleTranslator wrapper)
3. **Speech:** SpeechRecognition (STT), gTTS (TTS) — optional Google Cloud TTS integration supported
4. **PDF Export:** xhtml2pdf / pisa
5. **Language:** Python 3.10+ (tested on 3.13)
6. **Styling:** Custom `style.css` with responsive media queries

## 5. Features (Numbered)

1. Instant translation with history logging
2. Auto-detect source language
3. Voice input (microphone capture)
4. Selectable voice presets (local gTTS + optional Google Cloud TTS for character voices)
5. Download translation as `.TXT` and `.PDF`
6. Light/Dark theme toggle
7. Mobile responsive layout and touch-friendly controls

## 6. Screenshots & Visuals

Below is a simple architecture diagram (rendered with Mermaid):

```mermaid
flowchart LR
  A[User Browser] --> B[Streamlit App]
  B --> C[Translation Engine (deep-translator)]
  B --> D[Speech: STT / TTS]
  D --> E[gTTS or Google Cloud TTS]
  B --> F[Export: TXT / PDF]
```

![App Preview](assets/preview.png)

> If `assets/preview.png` or `assets/logo.png` are missing, replace them or add your own images to `assets/`.

## 7. How to Run (Local)

1. Create and activate a virtual environment (Windows PowerShell example):

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
& venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
c:/Users/Lenovo/Language-Translator/venv/Scripts/python.exe -m streamlit run app.py
```

4. Open http://localhost:8501 in your browser.

## 8. Google Cloud TTS (Optional)

1. Enable **Cloud Text-to-Speech** in your GCP project.
2. Create a service account and download the JSON key.
3. Set `GOOGLE_APPLICATION_CREDENTIALS` to that JSON file path.
4. Install client library: `pip install google-cloud-texttospeech`.
5. The app includes hooks to switch from local `gTTS` to Google Cloud TTS for character voices.

## 9. Contribution & Development

1. Fork the repo, create a feature branch, and open a PR.
2. Keep secrets out of source control; use environment variables or Streamlit secrets for deployment.

## 10. Made with ❤️ — Credits

1. **Made by Aman Singh**
2. If you liked the project, give it a star ⭐ and share feedback.

---

_Project generated and enhanced for clarity and mobile UX by Aman Singh._
