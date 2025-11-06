# E-learning Path Recommender  
_A Graph and Tree Hybrid Traversal System_

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Repo](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/Pran-bot/E-learning-Path-Recommender-using-Graph-and-Tree-Hybrid-Traversal-Final)

## Overview

E-learning Path Recommender leverages hybrid graph and tree traversal algorithms to recommend personalized and optimized learning paths to users. This system is structured as a modern web application, featuring a Python-based backend and a separate frontend interface, designed to provide intelligent recommendations for educational content sequencing.

## Features

- **Personalized Learning Paths**: Recommends course sequences using advanced graph/tree hybrids.
- **Backend-Frontend Architecture**: Python-based backend (API), modern JavaScript-based frontend.
- **Extensible Data Models**: Easily adaptable to a variety of learning domains.
- **Separation of Concerns**: Organized codebase with clear separation between models, routes, schemas, and data access.

## Project Structure

```
.
├── backend
│   ├── .env              # Backend environment variables
│   ├── main.py           # Backend service entry point
│   ├── database/         # Data access and storage logic
│   ├── models/           # Data models and ORM schemas
│   ├── routes/           # API endpoints and route definitions
│   ├── schemas/          # Pydantic or equivalent data validation schemas
├── frontend              # Frontend source code (details below)
├── .gitignore
├── README.md
```

## Getting Started

### Prerequisites

- **Backend:** Python 3.8+, pip
- **Frontend:** Node.js & npm (details in `frontend/`)
- (Recommended) [virtualenv](https://virtualenv.pypa.io/en/latest/) for Python

### Setup

#### 1. Clone the repository

```bash
git clone https://github.com/Pran-bot/E-learning-Path-Recommender-using-Graph-and-Tree-Hybrid-Traversal-Final.git
cd E-learning-Path-Recommender-using-Graph-and-Tree-Hybrid-Traversal-Final
```

#### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Edit .env as needed
python main.py
```

#### 3. Frontend

```bash
cd ../frontend
npm install
npm start
```

Frontend serves on [http://localhost:8080/](http://localhost:8080/) by default.

### Environment Variables

Configure backend settings in `backend/.env`.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -am 'Add new feature'`).
4. Push to origin (`git push origin feature-name`).
5. Open a pull request.

## License

This repository is licensed under the MIT License.

---

**Made with by [Pran-bot](https://github.com/Pran-bot)**
