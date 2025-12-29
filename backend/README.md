---
title: HSE Plan Management System
emoji: 🦺
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
license: mit
---

# HSE Plan Management System

A comprehensive HSE (Health, Safety, and Environment) Plan Management application for HSE Managers to track and manage HSE programs including Leading and Lagging Indicators.

## Features

- **HSE Programs Management**: Create, track, and manage HSE programs
- **Leading Indicators**: HSE Training, Emergency Drills, Observation Cards (RADAR)
- **Lagging Indicators**: Safe Manhours, LTI, MTC, TRIR, MVIR
- **Email Reminders**: Automated reminders 1 month and 2 weeks before program dates
- **Dashboard**: Real-time statistics and program status overview

## API Endpoints

- `GET /` - Main application
- `GET /programs` - List all programs
- `POST /programs` - Create new program
- `GET /statistics` - Dashboard statistics
- `POST /test-reminder` - Test email reminder system

## Environment Variables

- `RESEND_API_KEY` - API key for email notifications (optional)
