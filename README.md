# 📚 BookTrackerBot – Your Reading Companion on Discord

**BookTrackerBot** is a powerful and community-friendly Discord bot that helps individuals and groups log their reading progress, share what they’re reading, and stay consistent — all while keeping data safely backed up to Google Sheets!


[Join our discord server to use the bot](https://discord.gg/2vuRJcgpK7)

---

## 🚀 Features

### 📖 Reading Log
- **Add Books**: Log books you’re currently reading with title, author, total pages, and one or more genres.
- **Update Progress**: Use slash commands to update your current page with automatic time stamps.
- **Shelf/Unshelf**: Mark books as finished (shelved) or bring them back for rereading (unshelved).
- **Delete Books**: Remove books from your log if added by mistake.

### 📊 Visual Reports
- **Progress Embeds**: View detailed progress cards for each book.
- **Genre Summary Charts** *(coming soon)*: Visualize your reading preferences over time.

### 🔁 Weekly Automation
- **Daily Summary**: Notifies the group about who updated their progress today.
- **Weekly Summary**: Shares a recap of active readers every Sunday.
- **Weekly Reminder**: Pings users who haven’t updated by the end of the week.
- **Google Sheets Sync**: Automatically uploads the Excel data to a connected Google Sheet every weekend for backup.

### 🔐 Admin Features
- **Admin-Only Commands**: Certain commands (like syncing data or managing genres) are restricted to admins.
- **Locked Channels**: Sensitive commands are only permitted in a designated admin channel.
- **Genre Whitelisting**: Only approved genres are allowed. Users can request new genres to the admins.

### 🧠 Smart Integration
- **Excel & Google Sheets Backend**: All data is stored in an Excel file and automatically synced to Google Sheets.
- **Service Account Auth**: Secure integration with Google APIs using a service account – no public link sharing needed.

---

## 🛠️ Main Commands Overview

| Command                | Description                                      | Access    |
|------------------------|--------------------------------------------------|-----------|
| `/add_book`            | Add a new book to your reading list             | Everyone  |
| `/update_book`         | Update progress for a book                       | Everyone  |
| `/shelf_book`          | Mark a book as completed                         | Everyone  |
| `/unshelf_book`        | Bring a shelved book back to reading            | Everyone  |
| `/delete_book`         | Delete a book from your log                      | Everyone  |
| `/genres`              | List out all the available genres                   | Everyone  |
| `/help`                | Help message that explains all commands                | Everyone  |
| `/progress`            | Displays last `DATE_CUTOFF_DAYS` days of self progress| Everyone    |
| `/progress @user1@user2`| Displays last `DATE_CUTOFF_DAYS` days of tagged people's progress| Everyone |
| `/progress *`          | Displays last `DATE_CUTOFF_DAYS` days of everyone's progress| Admin |
| `/download_log`        | Download your reading data as Excel             | Everyone  |
| `/download_log @user`  | Download @user's reading data as Excel             | Admins  |
| `/download_log_all`  | Download everyone's reading data as Excel             | Admins  |
| `/gsheet_sync`         | Sync Excel to Google Sheet (manual trigger)     | Admins    |

---

## 📁 Data Structure

- **Excel File**: Primary data store.
- **Google Sheets**: Weekly backup target for cloud sync.
- **Genres Sheet**: A separate sheet for managing allowed genres.

---

## 🔧 Setup

1. **Clone the repository**
2. **Configure `.env`**
```
DISCORD_BOT_TOKEN=your-token-here
ALLOWED_GUILD_ID=your-server-id
LOG_CHANNEL_ID=preferably-admin-group-where-status-is-shown-text-channel-id
ALLOWED_TEXT_CHANNEL_ID=allowed-to-put-summary-and-remainders-text-channel-id
WELCOME_CHANNEL_ID=welcome-channel-id
EXCEL_FILE=path/to/data.xlsx
GOOGLE_SHEET_NAME=your-google-sheet-name
GOOGLE_SHEET_WORKSHEET=Sheet1
GOOGLE_SHEETS_CRED_PATH=path/to/service_account.json
DEBUG=False
```
Save the service account key as a .json file.

3. **Share your Google Sheet** with the service account:
```
sheet-bot@your-project-id.iam.gserviceaccount.com
```
Give **Editor access**.

4. **Install requirements**
```bash
pip install -r requirements.txt
```
5. Run the bot
```python
python bot.py
```
