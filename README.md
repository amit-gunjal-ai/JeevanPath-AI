# SIH26097 - AI-Driven Livelihood Assistant

## Problem Statement

AI-Driven Voice Assistant for Livelihood Mapping and NSQF-Aligned
Skilling Recommendations for SC Communities under the GIA component of PM-AJAY.

## Team

- Amit - ML + Integration
- Priya - ML
- Janhavi - NLP
- Prathmesh - Backend
- Tanvi - Frontend
- Vaishavnvi - Research + QA + Presentation

## Project Pipeline

Voice Input
→ Speech-to-Text
→ NLP
→ Beneficiary Profile
→ Skill Gap Analysis
→ Recommendation Engine
→ Personalized Roadmap
→ Frontend

## Current Status

Project setup in progress.

## Setup
1. `python -m venv venv` then activate it
2. `pip install -r requirements.txt`
3. Install ffmpeg separately (required for voice/Whisper): `winget install ffmpeg` (Windows) — required for speech-to-text to work
4. Copy `.env.example` to `backend/.env` and fill in your own DB credentials + API keys (never commit `.env`)