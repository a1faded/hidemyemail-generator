<p align="center"><img width=60% src="docs/header.png"></p>

<p align="center">
  <strong>Automated bulk generation of Apple's iCloud Hide My Email addresses</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
</p>

---

## ✨ Features

- 🔄 **Automatic Rate Limit Handling** - Queue any number of emails and let the script handle Apple's limits
- ⏱️ **Smart Batch Processing** - Generates 5 emails per batch with intelligent 45-minute cooldowns
- 💾 **Incremental Saves** - Progress saved after each batch (never lose your work!)
- 📊 **Live Progress Tracking** - Real-time countdown timers and batch status
- 🎯 **Retry Logic** - Automatically retries failed batches without losing count
- 🎨 **Beautiful CLI** - Rich terminal UI with color-coded messages

<p align="center"><img src="docs/example.png"></p>

---

## 📋 Requirements

- **Python 3.12+** required
- **iCloud+ subscription** - You need an active subscription to use Hide My Email
- **Rate Limits** - Apple allows 5 emails per family member every ~30 minutes
- **Total Cap** - Approximately 700 total Hide My Email addresses per account

---

## 🚀 Quick Start

### Option 1: Pre-built Binaries (Easiest)
Download ready-to-use binaries for Windows & ARM Macs from the [releases page](https://github.com/rtunazzz/hidemyemail-generator/releases).

### Option 2: Run from Source

**1. Clone the repository**
```bash
git clone https://github.com/a1faded/hidemyemail-generator
cd hidemyemail-generator
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up your iCloud cookie** (see [Cookie Setup Guide](#-cookie-setup-guide) below)

**4. Run the generator**
```bash
# macOS/Linux
python3 main.py

# Windows
python main.py
```

**5. Enter the number of emails you want**
```
How many iCloud emails you want to generate?: 100
```

The script will automatically:
- Generate emails in batches of 5
- Wait 45 minutes between batches
- Save progress after each batch to `emails.txt`
- Retry failed batches automatically

---

## 🍪 Cookie Setup Guide

> **Note:** You only need to do this once!

### Step 1: Install EditThisCookie Extension
Download [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) for Chrome/Edge

### Step 2: Configure Export Format
1. Go to [EditThisCookie settings](chrome-extension://fngmhnnpilhplaeedifhccceomclgfbg/options_pages/user_preferences.html)
2. Set **Preferred Export Format** to: `Semicolon separated name=value pairs`

<p align="center"><img src="docs/cookie-settings.png" width=70%></p>

### Step 3: Export Your Cookies
1. Navigate to [iCloud settings](https://www.icloud.com/settings/) and log in
2. Click the EditThisCookie extension icon
3. Click "Export" to copy your cookies

<p align="center"><img src="docs/export-cookies.png" width=70%></p>

### Step 4: Save Cookie File
1. Create a file named `cookie.txt` in the project directory
2. Paste your exported cookies into the file
3. Save and close

✅ You're all set! The script will use this cookie for authentication.

---

## 📖 How It Works

1. **Batch Processing** - Generates emails in batches of 5 to respect Apple's rate limits
2. **Automatic Waiting** - Waits 45 minutes between batches with a live countdown
3. **Smart Retries** - If a batch fails due to rate limiting, it waits and retries
4. **Incremental Saves** - Each successful batch is immediately saved to `emails.txt`
5. **Progress Tracking** - Shows real-time progress (e.g., "Batch 3/20 - 15/100 emails generated")

### Example Output
```
Batch 1/20 - Generating 5 email(s)...
✓ "example1@icloud.com" - Successfully reserved
✓ "example2@icloud.com" - Successfully reserved
...
✓ Batch 1 complete. 5/100 emails generated so far.
⏳ Rate limit reached. Waiting 44:59 before next batch...
```

---

## ⚠️ Important Notes

- **Cookie Expiration** - Your iCloud session will eventually expire. If you get unauthorized errors, export a fresh cookie
- **Rate Limits** - Apple enforces strict rate limits. The script handles these automatically
- **Family Sharing** - If you have iCloud Family Sharing, you can generate 5 emails × number of family members per batch
- **Internet Connection** - Keep your connection stable during long generation sessions

---

## 📝 Output

All generated emails are saved to `emails.txt` in the format:
```
your-email-1@icloud.com
your-email-2@icloud.com
your-email-3@icloud.com
...
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 📄 License

Licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 👨‍💻 Credits

**Original Author:** [rtuna](https://twitter.com/rtunazzz)  
**Enhanced By:** [A1FADED](https://github.com/a1faded)

---

<p align="center">Made with ❤️ for the privacy-conscious</p>
