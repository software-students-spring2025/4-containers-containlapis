# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

# 🎙️ Interview Answer Coaching System

[![Lint & Format](https://github.com/software-students-spring2025/4-containers-containlapis/actions/workflows/lint.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-containlapis/actions/workflows/lint.yml)
[![ML/Web CI](https://github.com/software-students-spring2025/4-containers-containlapis/actions/workflows/tests.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-containlapis/actions/workflows/tests.yml)

---

**Interview Answer Coaching System** is a containerized full-stack application that helps users practice spoken responses to interview questions and get AI-generated feedback.

**System Components:**
- 🧠 **ML Client**: Captures audio, transcribes using OpenAI, and provides AI feedback.
- 🌐 **Web App**: A Flask dashboard to interactively record and submit answers.
- 🗄️ **MongoDB**: A shared database for storing transcripts and feedback.


---

## 🚀 How to Run the Project

### ✅ Prerequisites

- Docker & Docker Compose
- OpenAI API Key (for transcription and feedback)

---

### 🛠 Setup Instructions

#### 1. Clone the repository

```bash
git clone https://github.com/software-students-spring2025/4-containers-containlapis.git
cd 4-containers-containlapis
```

#### 2. Configure environment variables

##### Create `.env` files:

```bash
cp machine-learning-client/.env.example machine-learning-client/.env
cp web-app/.env.example web-app/.env
```

##### Then edit and fill them in:

**machine-learning-client/.env**
```env
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=mongodb://mongodb:27017
```

**web-app/.env**
```env
MONGO_URI=mongodb://mongodb:27017
```

---

### 🐳 Start with Docker Compose

```bash
docker-compose up --build
```

📍 Visit your app at [http://localhost:5000](http://localhost:5000)

---

## 🧪 Running Tests

Tests use `pytest`, `coverage`, and `pytest-flask`.

```bash
# ML Client
cd machine-learning-client
pipenv install --dev
pipenv run pytest --cov=ml_client

# Web App
cd ../web-app
pipenv install --dev
pipenv run pytest --cov=web_app
```

✅ Code coverage must meet or exceed **80%**

---

## 🧰 Developer Workflow

- ✅ All changes via feature branches
- ✅ Code is linted and formatted using `pylint` and `black`
- ✅ CI pipeline runs tests and formatting checks on every PR

---

## 📦 Linting and Formatting

Manually check formatting with:

```bash
pipenv run black . --check
pipenv run pylint ml_client/
```

CI will automatically run these during pull requests.

---

## 👥 Team Members

| Name           | GitHub Profile                                     |
|----------------|----------------------------------------------------|
| **Yang Hu**    | [@younghu312](https://github.com/younghu312)       |
| **Ziqi Huang** | [@RyanH0417](https://github.com/RyanH0417)         |
| **Zirui Han**  | [@ZiruiHan](https://github.com/ZiruiHan)           |
| **Zichao Jin** | [@ZichaoJin](https://github.com/ZichaoJin)         |

---

## 📜 License

Developed as part of NYU’s Software Engineering course, Spring 2025. Not licensed for commercial use.

---
