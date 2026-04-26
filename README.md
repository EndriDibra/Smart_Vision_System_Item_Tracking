# Smart Vision Item Tracking System
A computer vision and voice-enabled smart item tracking system developed as a **3-day challenge** for a company interview. The system detects QR codes, barcodes, and text using OpenCV and pyzbar, stores item data in CSV, provides a web dashboard, and supports natural voice interaction for querying item status and location.

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Project Structure](#project-structure)
6. [How It Works](#how-it-works)
7. [Voice Interaction](#voice-interaction)
8. [Web Dashboard](#web-dashboard)
9. [Useful Commands](#useful-commands)
10. [Troubleshooting](#troubleshooting)
---

## Overview
This project combines **Computer Vision**, **Data Management**, and **Voice Technology** into an intelligent item tracking system. It scans items in real-time using a camera, extracts information from QR/barcodes and text via OCR, stores everything in a CSV dataset, and allows users to interact with the system through voice commands or a simple web interface.

The system demonstrates practical use of OpenCV for vision tasks, Pandas for data handling, Flask for the UI, and speech libraries to enhance Human-Computer Interaction (HCI).

---

## Features
- Real-time QR code and barcode detection with visual feedback
- OCR text extraction from images using Tesseract
- Automatic data storage in CSV with timestamp and location
- Duplicate prevention when scanning the same item
- Voice assistant for querying item status and location
- Web-based dashboard for viewing and searching tracked items
- Multi-threaded support for running scanner, voice, and UI simultaneously

---

## Prerequisites
### Required
1. **Python 3.8 or higher**
2. **Webcam** (for real-time scanning)
3. **Microphone** (for voice commands)
4. **Tesseract OCR** installed and added to system PATH
   - Download from: https://github.com/UB-Mannheim/tesseract/releases

### Python Dependencies
All required packages are listed in the `requirements.txt` file.

---

## Quick Start
```bash
# 1. Clone the repository
git clone <your-repository-url>
cd Smart_Vision_System_Item_Tracking

# 2. (Recommended) Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
