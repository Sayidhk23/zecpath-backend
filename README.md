# ZecPath Backend

Backend application for the ZecPath hiring and recruitment platform.

## Project Overview

ZecPath is a recruitment platform that manages the hiring workflow from job creation to candidate application and selection.

## Hiring Flow

Candidate → Job Application → ATS Screening → AI Call → Interview → Shortlisting → Offer

## Technology Stack

* Python
* Django
* Django REST Framework
* SQLite / PostgreSQL
* Git
* GitHub

## Main Modules

* User Management
* Employer Management
* Candidate Management
* Job Management
* Application Management
* ATS
* AI Screening
* Interview Management
* Offer Management

## Project Structure

```text
myproject/
├── apps/
├── services/
├── utils/
├── core/
├── myproject/
├── manage.py
├── .env
├── .gitignore
└── requirements.txt
```

## Installation

Clone the repository and create a virtual environment.

```bash
python -m venv venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure the required environment variables.

Run migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

## Environment Variables

The following values should be stored in `.env`:

```text
SECRET_KEY=
DEBUG=
```

The `.env` file is excluded from Git using `.gitignore`.

## Git Workflow

The project uses feature branches and meaningful commit messages.

Example:

```text
feature/job-api
fix/application-validation
refactor/job-service
```
