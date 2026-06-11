# Telegram Bot: Google Apps Script + Google Sheets

A simple Telegram bot built with **Google Apps Script (GAS)** that logs user input and chat messages to **Google Sheets**. It provides an interactive menu with features like saving, viewing, and deleting personal data (NIP and phone number), and tracks chat logs.

## 🚀 Features
- Save user data (NIP, phone number) via Telegram
- Interactive menu with inline reply options
- Store messages into Google Sheets for logging
- Simple status check (saved / deleted)
- Logging system for every action
- No server needed — deploy directly with Apps Script Web App

## 📂 Sheets Structure
- `Data Anggota`: stores user data
- `Log`: stores logs of activity
- `Data Chat`: stores user chat logs

## 🛠 Tech Stack
- Google Apps Script
- Telegram Bot API
- Google Sheets

## 🔧 Setup Instructions
1. Open [script.google.com](https://script.google.com) and create a new Apps Script project
2. Paste the contents of `Code.gs` into the project
3. Set project as a Web App:
    - Deploy → Manage Deployments → New Deployment
    - Type: Web App
    - Execute as: Me
    - Who has access: Anyone
4. Set the webhook in Telegram:

5. Create 3 sheets inside your Google Spreadsheet:
- Data Anggota
- Log
- Data Chat

## 📄 Example Command

## 📬 Author
**Irgi Ahmad Alfarizi**  
[GitHub](https://github.com/irgiahmd)
---

## 📃 License
MIT License
