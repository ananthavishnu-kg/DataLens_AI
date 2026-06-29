# 🔭 DataLens AI

> **Interactive Data Analysis & Insight Generation Platform**  
> Upload a spreadsheet → profile it → clean it → see auto-dashboards → run analytics → ask questions in plain English → export an executive PDF.


## ✨ Features

| | |
|---|---|
| 📤 **Upload** | CSV · XLSX · XLS — auto-classifies dataset type (Sales, HR, Finance, Marketing, Customer, Job Market) |
| 🔬 **Profiling** | Rows, columns, missing %, duplicates, memory, **0–100 health score**, type distribution, missing-value heatmap |
| 🧹 **Cleaning** | Fill missing (mean/median/mode/zero/unknown), drop rows or columns, remove duplicates, convert dtypes, IQR outlier detection — with toast notifications on every action |
| 📊 **Dashboard** | Auto-generated KPI tiles + interactive Plotly charts: Bar, Pie, Histogram, Scatter, Line, Box · with date / category / numeric range filters |
| 🧪 **Analytics** | Correlation matrix & strong-correlation finder, IQR + Z-score outliers, growth/decline/seasonality trend analysis, distribution stats — color-coded insight cards |
| 🤖 **Analyst Assistant** | Streaming natural-language Q&A with typing indicator, chat bubbles, conversation memory, casual chat support — powered by Groq (llama-3.3-70b-versatile) or offline rule-based mode |
| 📑 **Reports** | One-click executive PDF — Executive Summary · Dataset Overview · KPI Summary · Key Findings · Recommendations · Appendix |

### 🔒 Privacy-safe AI mode
DataLens AI **never sends your raw dataframe**. It builds a compressed JSON context (shape, summary stats, top categories, correlations, trends) and sends only that to Groq.

---

## 🚀 Setup (first time)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/DataLens_AI.git
cd DataLens_AI

# 2. Create and activate virtual environment
python -m venv .venv

# Mac/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key to .env
# Edit .env and add your key (get one free at console.groq.com)

# 5. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## ▶️ Run (after setup)

```bash
# Windows
.venv\Scripts\activate
streamlit run app.py

# Mac/Linux
source .venv/bin/activate
streamlit run app.py
```

---

## 🤖 Groq AI Setup

1. Go to https://console.groq.com and sign up (free)
2. Create an API key
3. Paste it in the `.env` file:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
4. Restart Streamlit
5. Enable **AI Analysis** toggle in the sidebar or directly on the Assistant page

The assistant uses **llama-3.3-70b-versatile** — fast, free, and streams responses word by word.

---

## 📁 Project Structure

```
DataLens_AI/
├── app.py                           # Home / landing page
├── pages/
│   ├── 1_Upload_Data.py             # File upload + dataset preview
│   ├── 2_Data_Profiling.py          # Health score, stats, heatmap
│   ├── 3_Data_Cleaning.py           # Interactive cleaning with notifications
│   ├── 4_Dashboard.py               # Auto KPI cards + 6 Plotly charts
│   ├── 5_Analytics.py               # Correlations, outliers, trends
│   ├── 6_Data_Analyst_Assistant.py  # Streaming AI chat interface
│   └── 7_Report_Generator.py        # Executive PDF export
├── modules/
│   ├── loader.py                    # File IO + dataset intelligence
│   ├── profiler.py                  # Health score, summaries
│   ├── cleaner.py                   # Missing / dtypes / duplicates / outliers
│   ├── dashboard.py                 # Plotly figures
│   ├── analytics.py                 # Correlations, trends, distributions
│   ├── insights.py                  # Smart insight engine
│   ├── assistant.py                 # Rule-based + Groq-powered Q&A
│   └── reporting.py                 # PDF executive report (ReportLab)
├── assets/
│   └── styles.css                   # Distinctive dark theme
├── data/
│   └── sample_sales.csv             # Sample dataset for quick start
├── .streamlit/
│   └── config.toml                  # Theme + server config
├── .env                             # API keys (never committed)
├── .gitignore
├── LICENSE
└── requirements.txt
```

---

## ⚡ Performance

- Handles **100,000+ rows** comfortably
- Streamlit caching for expensive computations
- Heatmaps & previews sampled for snappy UI
- Pandas vectorised — no Python loops over rows
- Groq streaming for real-time AI responses

---

## 🛣️ Roadmap

- 🎞️ **PowerPoint export** (alongside PDF)
- 💬 **Natural-language chart generation**
- 🗂️ **Multi-file analysis** (joins & relationship detection)
- 🗃️ **SQL database connections** (Postgres / MySQL / Snowflake)
- 🪧 **Data versioning** (track cleaning history)
- 🔐 **User authentication & workspaces**
- ☁️ **One-click cloud deployment**

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.