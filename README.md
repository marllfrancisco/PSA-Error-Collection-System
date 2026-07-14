# PSA Error Collection System
[![DOI](https://zenodo.org/badge/1253352528.svg)](https://doi.org/10.5281/zenodo.21358094)

A desktop-based database management system designed to streamline the identification, correction, and auditing of discrepancies in Philippine Statistics Authority (PSA) civil registry records.

---

## 📖 About the Project

The PSA Error Collection System is a database-driven application developed to assist PSA offices in managing discrepancies found between physical certificates and digital records.

Instead of recording corrections manually in spreadsheets, the system centralizes discrepancy reports, records every modification through an audit log, and maintains historical records for accountability.

This project was developed as a partial course requirement for COMP 20093 - Infomation Management at Polytechnic University
of the Philippines - Sta. Mesa.

---

## 🎯 Objectives

- Eliminate manual Excel-based error tracking.
- Centralize discrepancy reports.
- Record every modification made to registry records.
- Improve traceability through audit logging.
- Reduce communication delays between satellite offices and the central office.

---

## ✨ Features

### User Management
- Employee login
- Password authentication
- Role-based access (admin, regular employee)
- Password reset via OTP
- Employee account management (create, update)
- Employee activity logging
- Account creation (admin only)

### Discrepancy Management
- Create discrepancy reports
- Update report status
- View pending and resolved reports

### Audit Logging
- Record original values
- Record revised values
- Record modified field
- Record employee responsible
- Record modification timestamp

### Certificate Management
- Birth Certificates
- Marriage Certificates
- Death Certificates

### Database Features
- MySQL relational database
- Foreign key constraints
- Audit log implementation

### Accesibility Settings
- Font size adjustment
- Light, dark, and slate high contrast mode themes
- Tabular rows font size adjustment

---

## 🖥 Technologies Used

### Programming Language
- Python 3

### GUI
- Tkinter
- ttkbootstrap

### Database
- MySQL

### IDE
- Visual Studio Code

### Version Control
- Git
- GitHub

---

## 📂 Project Structure

```
PSA-Error-Collection-System/
│
├── SourceCodes/
│   ├── images/
│   ├── Ecorrect.sql
│   ├── ErrorCollectionCSV.py
│   ├── employee_data.csv
│   ├── employee_logs.json
│   └── accounts.json
│
├── README.md
└── LICENSE
```

---

## 🗃 Database Design

Main Entities

- Person
- Employee_Account
- Employee_Account_Logs
- Registry Number
- Birth_Certificate
- Marriage_Certificate
- Death_Certificate
- Discrepancy_Report
- Discrepancy_Report_Audit

The database follows Third Normal Form (3NF) and enforces referential integrity using foreign keys.

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/<username>/PSA-Error-Collection-System.git
```

### Install dependencies

```bash
pip install ttkbootstrap mysql-connector-python
```

### Import the database

Open MySQL Workbench and execute

```
Ecorrect.sql
```

---

## ▶ Running the Program

```bash
python ErrorCollectionCSV.py
```

---

## 📸 Screenshots

### Login

![login](/Screenshots/login.png)

### Register

![register](/Screenshots/register.png)

### OTP Verification

![otp_verification](/Screenshots/otp.png)

### Dashboard

#### Admin Dashboard

![admin_dashboard](/Screenshots/adminhome.png)

#### Employee Dashboard

![employee_dashboard](/Screenshots/emphome.png)

### Discrepancy Desk

![discrepancy_desk](/Screenshots/entry.png)

### Discrepancy Details

![discrepancy_details](/Screenshots/entrydeets.png)

### Audit Logs

![audit_logs](/Screenshots/auditlog.png)

### Employee Activity Logs

![employee_activity_logs](/Screenshots/employeelogs.png)

### Token Request

![token_request](/Screenshots/tokenrequests.png)

### Settings

![settings](/Screenshots/settings.png)

---

## 👥 Authors

Biando, Sofia Ela

Concepcion, Ramcel Aaron

Daitol, Michael Angelo

Francisco, Marl Louie T.

Pangilinan, Ezekiel

---

## 📄 License

This project is intended for academic purposes only.

Consented data is used throughout the repository. No actual PSA records are included.
