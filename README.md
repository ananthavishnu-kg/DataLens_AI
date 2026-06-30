<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0,0A0F1E,0B1020,22d3ee&height=200&section=header&text=DataLens%20AI&fontSize=55&fontColor=fff&animation=fadeIn&fontAlignY=36&desc=Interactive%20Data%20Analysis%20%7C%20Streamlit%20%7C%20Groq%20%7C%20Plotly&descAlignY=58&descSize=16" width="100%"/>
</div>

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-ananthavishnu--kg-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ananthavishnu-kg)
[![Repo](https://img.shields.io/badge/🔭_DataLens_AI-View_Repository-22d3ee?style=for-the-badge&logoColor=white)](https://github.com/ananthavishnu-kg/DataLens_AI)

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-F55036?style=flat-square&logo=groq&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=flat-square&logo=pandas&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Export-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## 📌 Overview

**DataLens AI** is an interactive data analysis workspace that turns raw spreadsheets into clean dashboards, statistical insights, and executive reports — without writing a single line of code.

Upload a CSV or Excel file, explore it visually, ask questions in plain English, and export a board-ready PDF — all in one seamless 7-step workflow.

> 🔭 *"See what your data is trying to tell you."*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **Smart Upload** | CSV · XLSX · XLS — auto-classifies dataset type (Sales, HR, Finance, Marketing, Customer, Job Market) |
| 🔬 **Data Profiling** | Rows, columns, missing %, duplicates, memory, **0–100 health score**, type distribution, missing-value heatmap |
| 🧹 **Data Cleaning** | Fill missing values, drop duplicates, convert dtypes, IQR outlier detection — with toast notifications on every action |
| 📊 **Auto Dashboard** | KPI tiles + 6 interactive Plotly charts (Bar, Pie, Histogram, Scatter, Line, Box) with live filters |
| 🧪 **Analytics** | Correlation matrix, outlier detection (IQR + Z-score), trend analysis, distribution stats — color-coded insight cards |
| 🤖 **AI Assistant** | Streaming natural-language Q&A with typing indicator, chat bubbles, conversation memory, and casual chat support |
| 📑 **PDF Reports** | One-click executive PDF with Executive Summary, KPI tables, Key Findings, Recommendations, and Appendix |

### 🔒 Privacy-safe AI
DataLens AI **never sends your raw data** to the AI. It builds a compressed JSON context (shape, stats, correlations) and sends only that — your data stays local.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        DataLens AI                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Streamlit Frontend (7 Pages)            │   │
│  │   Upload → Profile → Clean → Dashboard →            │   │
│  │   Analytics → Assistant → Report                    │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Module Layer                        │   │
│  │                                                     │   │
│  │   loader.py  →  profiler.py  →  cleaner.py          │   │
│  │   dashboard.py  →  analytics.py  →  insights.py     │   │
│  │   assistant.py  →  reporting.py                     │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   AI Layer                           │   │
│  │                                                     │   │
│  │   Compressed JSON context (never raw data)          │   │
│  │   Groq API → llama-3.3-70b-versatile                │   │
│  │   Fallback → Rule-based offline engine              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.58 | Multi-page interactive UI with dark theme |
| **Data** | Pandas · NumPy | Data loading, cleaning, transformation |
| **Visuals** | Plotly | Interactive charts and correlation heatmaps |
| **Analytics** | SciPy | Statistical analysis, skewness, kurtosis |
| **AI Layer** | Groq API · Llama 3.3 70B | Streaming natural-language Q&A |
| **Reporting** | ReportLab | A4 PDF executive reports |
| **Storage** | Local filesystem | Uploads, reports, exports |
| **Environment** | python-dotenv | Secure API key management |

</div>

---

## 📁 Project Structure

```
DataLens_AI/
│
├── 📄 app.py                            → Home / landing page
├── 📁 pages/
│   ├── 📄 1_Upload_Data.py              → File upload + dataset preview
│   ├── 📄 2_Data_Profiling.py           → Health score, stats, heatmap
│   ├── 📄 3_Data_Cleaning.py            → Interactive cleaning with notifications
│   ├── 📄 4_Dashboard.py               → Auto KPI cards + 6 Plotly charts
│   ├── 📄 5_Analytics.py               → Correlations, outliers, trends
│   ├── 📄 6_Data_Analyst_Assistant.py  → Streaming AI chat interface
│   └── 📄 7_Report_Generator.py        → Executive PDF export
│
├── 📁 modules/
│   ├── 📄 loader.py                    → File IO + dataset intelligence
│   ├── 📄 profiler.py                  → Health score, summaries
│   ├── 📄 cleaner.py                   → Missing / dtypes / duplicates / outliers
│   ├── 📄 dashboard.py                 → Plotly figures
│   ├── 📄 analytics.py                 → Correlations, trends, distributions
│   ├── 📄 insights.py                  → Smart insight engine
│   ├── 📄 assistant.py                 → Rule-based + Groq-powered Q&A
│   └── 📄 reporting.py                 → PDF executive report
│
├── 📁 assets/
│   └── 📄 styles.css                   → Distinctive dark theme
├── 📁 data/
│   └── 📄 sample_sales.csv             → Sample dataset for quick start
├── 📁 .streamlit/
│   └── 📄 config.toml                  → Theme + server config
│
├── 📄 .env                             → API keys (never committed)
├── 📄 .gitignore
├── 📄 LICENSE
└── 📄 requirements.txt
```

---

## 🤖 How the AI Assistant Works

```
You type:  "which category performs best?"
              │
              ▼
         DataLens AI builds compressed context:
         { rows, columns, numeric_stats, top_categories,
           correlations, trends } — NO raw data sent
              │
              ▼
         Groq Llama 3.3 70B reasons over context
              │
              ▼
         Streams response word by word with typing indicator
              │
              ▼
         "🏆 Top Category by Sales:
          • Technology: $961,432
          • Furniture: $728,659
          Want me to compare these against the average?"
              │
              ▼
         Dynamic follow-up suggestions update based on answer ✅
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+ installed
- A free Groq API key from [console.groq.com](https://console.groq.com)

### Setup

```bash
# Clone the repository
git clone https://github.com/ananthavishnu-kg/DataLens_AI.git
cd DataLens_AI

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key to .env
GROQ_API_KEY=gsk_your_key_here

# Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 💬 Example Questions for the Assistant

| What you ask | What DataLens AI does |
|---|---|
| `hi` | Greets you warmly and introduces itself |
| `what are the key insights?` | Surfaces 6 automated findings from your data |
| `which category performs best?` | Shows top categories ranked by primary metric |
| `show me strong correlations` | Lists all column pairs with \|r\| ≥ 0.5 |
| `are there any outliers?` | IQR detection across top numeric columns |
| `what's the trend over time?` | Growth/decline analysis with % change |
| `tell me about Sales` | Full stats: mean, median, min, max, missing |

---

## 🔮 Roadmap

- [ ] **PowerPoint export** alongside PDF
- [ ] **Natural-language chart generation** ("show revenue by region as a bar chart")
- [ ] **Multi-file analysis** (joins & relationship detection)
- [ ] **SQL database connections** (Postgres / MySQL / Snowflake)
- [ ] **Data versioning** (track cleaning history with diffs)
- [ ] **User authentication & workspaces**
- [ ] **One-click cloud deployment**

---

## 👨‍💻 Developer

<div align="center">

**Ananthavishnu KG** — AI & Full Stack Developer

[![GitHub](https://img.shields.io/badge/GitHub-ananthavishnu--kg-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ananthavishnu-kg)

</div>

---

<div align="center">

*Built with ❤️ using Streamlit · Groq · Plotly · Pandas · ReportLab*

<img src="https://capsule-render.vercel.app/api?type=waving&color=0,22d3ee,0B1020,0A0F1E&height=130&section=footer&animation=fadeIn" width="100%"/>

</div>
