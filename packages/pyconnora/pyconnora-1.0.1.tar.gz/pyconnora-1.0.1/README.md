# Oracle Database Connection Utility

A lightweight Python utility class for connecting to **Oracle databases** using `cx_Oracle`, with built-in support for environment variables and `.env` configuration.

---

## 📘 Overview

The `Connect` class provides a simple interface to:
- Establish a connection to an Oracle database.
- Execute parameterized queries securely.
- Fetch data from specific tables or columns.
- Automatically load credentials from a `.env` file or environment variables.

This helps you avoid hardcoding credentials and ensures safer, cleaner database access in Python.

---

## ⚙️ Features

- ✅ Automatic `.env` file loading based on OS (Windows/Linux).  
- ✅ Fallback to environment variables (`ORA_HOST`, `ORA_USER`, etc.).  
- ✅ Secure parameter binding (prevents SQL injection).  
- ✅ Simple API for fetching data (WIP).  
- ✅ Easy cleanup with `close()`.

---

## 📦 Requirements

- **Python** 3.10 or later  
- **Oracle Instant Client** installed and accessible  
- **cx_Oracle** Python package  
- **python-dotenv** for `.env` management

