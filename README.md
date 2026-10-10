# Quantum Supply Chain Optimizer

A simple college-hackathon web application demonstrating supply-chain optimization using quantum-computing concepts.

## Main features
- Login page
- Dashboard
- Warehouse management
- Store management
- Demo transportation costs
- Classical greedy optimization
- QUBO-style route model
- QAOA-style local quantum simulation
- Classical vs quantum cost comparison
- Allocation result table
- Optimization history
- Charts
- About page

## Demo login
Username: `admin`
Password: `admin123`

## Requirements
- Windows 10/11
- Python 3.11
- Internet connection for first-time package installation and Chart.js CDN

## Windows setup
Open PowerShell in this project folder:

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\Activate.ps1
```

Then open:

http://127.0.0.1:5000

## Important quantum note
The project is designed as a reliable educational hackathon demonstration. It shows binary route variables, a QUBO-style formulation and a QAOA-style quantum workflow, but the included local result calculation is deterministic so the application remains stable across different Qiskit environments. Do not claim quantum speedup or quantum advantage from this demo.

## Demo data
Warehouses:
- W1: 100 units
- W2: 150 units
- W3: 120 units

Stores:
- S1: 80 units
- S2: 100 units
- S3: 70 units
- S4: 60 units

Transportation cost matrix:

| | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|
| W1 | 10 | 15 | 20 | 12 |
| W2 | 14 | 9 | 16 | 18 |
| W3 | 11 | 13 | 8 | 15 |

## Project structure

```text
Quantum_Supply_Chain_Optimizer/
├── app.py
├── requirements.txt
├── README.md
├── run_project.bat
├── .gitignore
├── database/
│   └── database.py
├── quantum/
│   ├── __init__.py
│   ├── optimization_model.py
│   └── quantum_optimizer.py
├── classical/
│   ├── __init__.py
│   └── classical_optimizer.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── warehouses.html
│   ├── stores.html
│   ├── optimization.html
│   ├── history.html
│   └── about.html
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       ├── dashboard.js
│       └── optimization.js
└── data/demo_data.json
```

## Hackathon explanation
The problem is to decide how limited warehouse supply should be sent to stores with different demand while considering route costs. The project compares a classical baseline with a quantum-computing-inspired workflow.
