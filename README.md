# Django React API Test Platform

This is a comprehensive API testing platform built with a Django backend and a React frontend. It allows users to define APIs, create test cases, build and execute test plans, and view detailed test reports.

## ✨ Features

- **API Definition**: Define API endpoints with methods, URLs, headers, and body.
- **Test Case Management**: Create detailed test cases with assertions and variable support.
- **Test Plan Orchestration**: Group test cases into executable test plans.
- **Automated Execution**: Run test plans and get immediate results.
- **Detailed Reporting**: View comprehensive reports with statistics and individual test results.
- **Mock Server**: Built-in mock server to simulate API responses for robust testing.
- **User Management**: Basic user authentication and management.

---

## 🛠️ Tech Stack

*   **Backend**: Django, Django REST Framework
*   **Frontend**: React, Vite, Ant Design
*   **Testing**: Pytest (Backend), Vitest (Frontend)
*   **Database**: SQLite (for development)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18.x or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yanjun1688/DjangoTestPlatform.git
cd DjangoTestPlatform
```

### 2. Backend Setup

```bash
# Navigate to the backend directory
cd blackend

# Create and activate a Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up the environment variables
# Copy the example file and fill in your secret key
cp .env.example .env

# Apply database migrations
python manage.py migrate
```

### 3. Frontend Setup

```bash
# Navigate to the frontend directory from the root
cd frontend

# Install dependencies
npm install
```

### 4. Running the Application

1.  **Start the Backend Server**:
    Open a terminal and run:
    ```bash
    # From the /blackend directory
    python manage.py runserver 8000
    ```
    The backend will be running at `http://localhost:8000`.

2.  **Start the Frontend Development Server**:
    Open a *new* terminal and run:
    ```bash
    # From the /frontend directory
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

---

## 🧪 Running Tests

This project has an automated test script to run both backend and frontend tests sequentially.

From the **root directory** of the project, run:

```bash
./run_tests.sh
```

This script will:
1.  Execute all Django backend tests using `manage.py test`.
2.  Execute all React frontend tests using `npm test`.

---

## 📁 Project Structure

```
DjangoTestPlatform/
├── _redundant_files_to_review/ # Old files saved for review
├── blackend/                   # Django backend source code
│   ├── api_test/               # Core API testing app
│   ├── mock_server/            # Mock server app
│   ├── reports/                # Test reporting app
│   ├── test_platform/          # Main Django project settings
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React frontend source code
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── README.md
└── run_tests.sh                # Automated test runner script
```
