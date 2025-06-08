# 🔥 PulseCheck - Team Collaboration & Wellbeing Dashboard

**PulseCheck** is a full-stack web application that helps software development teams log daily progress, track blockers, and monitor team morale using real-time charts and summaries.

It’s designed to boost team visibility, emotional awareness, and accountability — all in a single, intuitive dashboard.

---

## ✨ Features

### ✅ Daily Tracker
Team members can log:
- 📝 **Work updates** (commits, messages, PRs, blockers)
- 🧠 **Blockers** with optional tags (`backend`, `testing`, etc.)
- 😄 **Mood for the day** (emoji-based)

### 📊 Dashboard Analytics
- Activity trends (Commits, Messages, Blockers)
- **Mood trends line chart** (average team mood over the week)
- **Heatmap** of daily participation (who submitted on which day)
- **Member Overview Cards**:
  - Initial-based avatar
  - Weekly commits/messages/PRs/blockers
  - Participation score
  - Mini bar chart of member activity breakdown

### 🚧 Blocker & Morale Insights
- Blockers are categorized and logged per member
- Moods are collected and visualized over the week
- Helps detect team-wide blockers or emotional drops

### 📈 Team Summary Page
- 📌 **Total members**
- 📅 **Active days this week**
- 🔥 **Peak day** (highest number of entries)
- 🧑‍💻 **Most active member**
- Card-based summary view with clean design

---

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-Login, SQLAlchemy
- **Frontend**: Jinja2, Bootstrap 5, Chart.js
- **Database**: SQLite
- **Charts**: Chart.js (line, bar, heatmap)

---

## 🚀 How To Run This Project

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/pulsecheck.git
cd pulsecheck


python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate


pip install -r requirements.txt


flask run
```

| Dashboard                               | Team Summary                             |
| --------------------------------------- | ---------------------------------------- |
| ![Dashboard](screenshots/dashboard.png) | ![Team Summary](screenshots/summary.png) |




## 📌 Folder Structure
```
pulsecheck/
│
├── templates/
│   ├── layout.html
│   ├── dashboard.html
│   ├── tracker.html
│   └── team_summary.html
│
├── static/
│   ├── style.css
│   └── (Chart.js via CDN in layout)
│
├── models.py
├── app.py
├── requirements.txt
└── README.md
```



## 👥 Creator & Credits
💻 Human developer: Saksham Singh

🤖 Pair-programmed with: ChatGPT-4o (OpenAI)

We worked together as a team to plan, code, fix bugs, and deliver this real-world full-stack project from scratch.


```
Made with ❤️ using Flask, Python & curiosity
Built in 2025
```
