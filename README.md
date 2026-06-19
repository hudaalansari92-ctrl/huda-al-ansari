# Medical Dialog System | نظام الحوار الطبي الذكي

> An intelligent, bilingual (**Arabic / English**) medical dialog system for **cardiovascular risk assessment**.
> Combines self-reasoning conversation, domain rule engines, ML prediction, and **Groq AI** interpretation.

> نظام حوار طبي ذكي ثنائي اللغة (**العربية / الإنجليزية**) لتقييم مخاطر أمراض القلب،
> يجمع بين المحادثة ذاتية الاستدلال، محرك القواعد الطبية، التنبؤ بالتعلم الآلي، والتفسير عبر **Groq AI**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55+-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange.svg)](https://groq.com/)

---

## Table of Contents | الفهرس

- [Features](#features--المميزات)
- [User Roles](#user-roles--أدوار-المستخدمين)
- [Architecture](#architecture--بنية-النظام)
- [Quick Start](#quick-start--البدء-السريع)
- [Run on GitHub Codespaces](#run-on-github-codespaces--التشغيل-على-codespaces)
- [Default Credentials](#default-credentials--بيانات-الدخول-الافتراضية)
- [Project Structure](#project-structure--هيكل-المشروع)
- [Medical Fields](#medical-fields-collected--الحقول-الطبية)
- [Tech Stack](#tech-stack--التقنيات)
- [Security](#security--الأمان)
- [Author](#author--المؤلف)

---

## Features | المميزات

### English
- **Multi-user authentication** with SHA-256 password hashing + salt
- **Two user roles** — Patient (chat only) and Admin (full dashboard)
- **Smart conversation mode** powered by Groq LLMs
- **48 medical domain rules** for cardiovascular risk reasoning
- **Decision tree visualization** for interpretable decisions
- **ML predictor** trained with scikit-learn for risk classification
- **Voice input** via Groq Whisper (Speech-to-Text)
- **Text-to-speech** for doctor responses (gTTS)
- **Comprehensive assessment** — combines rules + ML + AI interpretation
- **Patient report generation** with instant alerts
- **Session persistence** — each conversation saved as JSON
- **Full Arabic/English UI** with RTL/LTR support
- **GitHub Codespaces ready** — open in browser, no install required

### العربية
- **نظام مصادقة متعدد المستخدمين** بتشفير SHA-256 مع salt
- **نوعا مستخدم** — مريض (محادثة فقط) ومسؤول (لوحة تحكم كاملة)
- **وضع محادثة ذكي** مدعوم بنماذج Groq
- **48 قاعدة طبية** للاستدلال على مخاطر القلب
- **عرض شجرة القرار** لقرارات قابلة للتفسير
- **نموذج تنبؤ بالتعلم الآلي** مدرّب بـ scikit-learn
- **إدخال صوتي** عبر Groq Whisper
- **تحويل النص إلى كلام** لردود الطبيب (gTTS)
- **تقييم شامل** — يدمج القواعد + ML + تفسير الذكاء الاصطناعي
- **توليد تقارير للمريض** مع تنبيهات فورية
- **حفظ الجلسات** — كل محادثة تُحفظ بصيغة JSON
- **واجهة عربية/إنجليزية** كاملة مع دعم RTL/LTR
- **جاهز لـ GitHub Codespaces** — افتح في المتصفح بدون تثبيت

---

## User Roles | أدوار المستخدمين

### Patient | مريض

The patient sees a **clean, focused chat interface** — just the doctor conversation and nothing else.

يرى المريض **واجهة محادثة بسيطة ومركّزة** — فقط محادثة الطبيب لا أكثر.

**Patient view contains:**
- Chat with AI doctor (smart or classic mode)
- Voice input button
- Simple progress bar
- Logout button

---

### Admin | مسؤول

The admin gets the **full system dashboard** with all advanced features.

يحصل المسؤول على **لوحة تحكم كاملة** بكل المميزات المتقدمة.

**Admin view contains:**
- Full chat interface
- Risk gauge + facts table (live updates)
- Previous sessions browser
- Decision tree visualization (3 tabs: Tree / Rules / Flow)
- ML model prediction + probability
- Groq AI interpretation + personalized recommendations
- System comparison page
- Architecture diagram
- Live demo page
- User management

---

## Architecture | بنية النظام

```
+--------------------------------------------------+
|              Streamlit Web UI                     |
|        (Arabic / English, RTL / LTR)              |
+--------------------+-----------------------------+
                     |
        +------------+------------+
        |                         |
   +----v-----+              +----v------+
   |  Auth    |              |  Chatbot  |
   |  Module  |              |  Core     |
   +----------+              +----+------+
                                  |
        +-------------------------+------------------+
        |                         |                  |
   +----v------+         +--------v--------+   +-----v-----+
   |  Domain   |         |  ML Predictor   |   |  Groq AI  |
   |  Rules    |         |  (scikit-learn) |   |  LLM      |
   |  (48)     |         +-----------------+   +-----------+
   +----+------+
        |
   +----v------------+
   | Final Decision  |
   | Engine          |
   | (combines all)  |
   +-----------------+
```

---

## Quick Start | البدء السريع

### Option 1 — Local Installation | التثبيت المحلي

**1. Clone the repository:**
```bash
git clone https://github.com/hudaalansari92-ctrl/huda-al-ansari.git
cd huda-al-ansari
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. (Optional) Configure Groq API for Smart Mode:**

Create a `.env` file in the project root:
```ini
GROQ_API_KEY=gsk_your_key_here
```

Get a free API key at: **https://console.groq.com**

> Without a Groq key, the app runs in **Classic Mode** (rule-based extraction only).

**4. Run the app:**

```bash
streamlit run app.py
```

On Windows you can use:
```bash
run.bat
```

**5. Open in browser:** http://localhost:8501

---

## Run on GitHub Codespaces | التشغيل على Codespaces

This repo includes a pre-configured `.devcontainer` — you can run the app **directly in your browser** with one click:

1. Go to https://github.com/hudaalansari92-ctrl/huda-al-ansari
2. Click the green **`Code`** button → **`Codespaces`** → **`Create codespace on main`**
3. Wait ~1 minute for setup
4. The app launches automatically on port 8501 — preview opens in browser

> No local Python installation needed.

---

## Default Credentials | بيانات الدخول الافتراضية

The system creates two default accounts on first run:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Patient | `patient` | `patient123` |

> **Change these immediately in production!** The admin can add/delete users and change passwords from the dashboard.
>
> **غيّر هذه فوراً عند النشر!** يمكن للمسؤول إضافة/حذف المستخدمين وتغيير كلمات المرور من لوحة التحكم.

**Password storage:**
- SHA-256 with a unique 32-character salt per user
- Stored in `auth/users.json` (gitignored — never committed)
- Constant-time comparison via `secrets.compare_digest`

---

## Project Structure | هيكل المشروع

```
huda-al-ansari/
|
|-- app.py                       # Main Streamlit entry point
|-- requirements.txt
|-- domain_rules.json            # 48 medical rules
|-- run.bat                      # Windows launcher
|-- .gitignore
|
|-- auth/                        # Authentication system
|   |-- auth_manager.py          # SHA-256 password handling
|   |-- login_ui.py              # Login & user management UI
|   |-- users.json               # User database (gitignored)
|
|-- config/                      # Configuration & translations
|   |-- translations.py          # AR/EN UI strings
|   |-- question_examples.py
|   |-- field_definitions.py
|
|-- core/                        # Self-reasoning chatbot core
|   |-- integrated_chatbot.py    # Main chatbot orchestrator
|   |-- dynamic_question_selector.py
|   |-- priority_scorer.py       # Question priority logic
|   |-- self_dialog_manager.py   # Internal dialog management
|   |-- history_tracker.py       # Field history + thresholds
|
|-- engine/                      # Reasoning + ML engines
|   |-- domain_rules_engine.py   # 48-rule reasoner
|   |-- advanced_features.py     # Feature engineering
|   |-- ml_predictor.py          # scikit-learn predictor
|   |-- final_decision_engine.py # Decision aggregator
|
|-- groq_api/                    # Groq LLM integration
|   |-- groq_client.py           # Groq API wrapper
|   |-- groq_ner.py              # Named-entity recognition via Groq
|   |-- conversation_manager.py  # Smart conversation flow
|   |-- result_interpreter.py    # AI interpretation of results
|   |-- recommendation_engine.py # Personalized recommendations
|
|-- nlp/                         # NLP utilities
|   |-- biobert_ner.py           # BioBERT fallback NER
|
|-- ui/                          # Streamlit UI components
|   |-- conversation_display.py  # Chat bubble rendering
|   |-- decision_tree_viz.py     # Plotly decision tree
|   |-- enhanced_styles.py       # Custom CSS
|   |-- comparison_page.py       # System comparison
|   |-- architecture_page.py     # Architecture diagram
|   |-- live_demo_page.py        # Interactive demo
|   |-- patient_report.py        # Patient report generator
|
|-- data/                        # Datasets
|-- models/                      # Trained ML models
|-- tests/                       # Unit tests
|-- .devcontainer/               # GitHub Codespaces config
    |-- devcontainer.json
```

---

## Medical Fields Collected | الحقول الطبية

The system gathers **11 clinical features** to predict cardiovascular risk:

| # | Field | الحقل | Description |
|---|-------|-------|-------------|
| 1 | Age | العمر | Patient age in years |
| 2 | Sex | الجنس | Male / Female |
| 3 | ChestPain | ألم الصدر | Type of chest pain |
| 4 | BloodPressure | ضغط الدم | Resting blood pressure (mmHg) |
| 5 | Cholesterol | الكوليسترول | Serum cholesterol (mg/dl) |
| 6 | FastingBS | سكر الصائم | Fasting blood sugar > 120 mg/dl |
| 7 | RestingECG | تخطيط القلب | Resting electrocardiogram |
| 8 | MaxHR | معدل النبض الأقصى | Maximum heart rate achieved |
| 9 | ExerciseAngina | ألم مع المجهود | Exercise-induced angina |
| 10 | Oldpeak | انخفاض ST | ST depression from exercise |
| 11 | ST_Slope | ميل ST | Slope of peak exercise ST segment |

### Risk Levels | مستويات الخطر

| Level | Meaning |
|-------|---------|
| **LOW** | No immediate concern |
| **MODERATE** | Follow up recommended |
| **HIGH** | Medical consultation needed |
| **CRITICAL** | Urgent attention required |

---

## Tech Stack | التقنيات

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit + custom CSS |
| **LLM** | Groq API (Llama / Mixtral models) |
| **NER** | BioBERT + Groq NER |
| **ML** | scikit-learn + joblib |
| **Visualization** | Plotly + Graphviz |
| **Speech-to-Text** | Groq Whisper |
| **Text-to-Speech** | gTTS (Google) |
| **Authentication** | SHA-256 + salt + secrets module |
| **Storage** | JSON files (sessions + users) |
| **Language** | Python 3.10+ |
| **Deployment** | GitHub Codespaces / Local |

---

## Security | الأمان

### What is protected | ما هو محمي

| File / Folder | Status | Reason |
|---------------|--------|--------|
| `.env` | Gitignored | Contains Groq API key |
| `auth/users.json` | Gitignored | User passwords (hashed) |
| `sessions/` | Gitignored | Patient medical data |
| `.streamlit/secrets.toml` | Gitignored | Streamlit secrets |
| `__pycache__/` | Gitignored | Python cache |

### Password security | أمان كلمات المرور

- Salted hashing (SHA-256 + 32-char random salt)
- Constant-time comparison (prevents timing attacks)
- Passwords never logged or displayed
- Each user gets a unique salt

### Best practices for production | أفضل الممارسات للنشر

1. **Change default credentials** (`admin/admin123` and `patient/patient123`)
2. **Use environment variables** for Groq API key, not hardcoded
3. **Enable HTTPS** when deploying
4. **Restrict CORS** in production (currently disabled for Codespaces dev)
5. **Regular backups** of `auth/users.json` and `sessions/`

---

## Testing | الاختبارات

```bash
python -m pytest tests/
```

---

## License | الترخيص

This project is developed for **educational and research purposes**.

هذا المشروع طُوّر **لأغراض تعليمية وبحثية**.

---

## Author | المؤلف

**Huda Al-Ansari**

GitHub: [@hudaalansari92-ctrl](https://github.com/hudaalansari92-ctrl)

Repository: [huda-al-ansari](https://github.com/hudaalansari92-ctrl/huda-al-ansari)

---

## Contributing | المساهمة

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

<div align="center">

**Made for medical AI research**

</div>
