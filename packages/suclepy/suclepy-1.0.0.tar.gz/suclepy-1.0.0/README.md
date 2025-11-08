# 🧹 SUCLEPY — Smart Universal Cleaner Library for Python

![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)

---

## ✨ Overview

**SUCLEPY** is your **one-stop Python library for smart data cleaning**!  
Clean data, fill missing values, remove duplicates, validate emails, normalize text, parse dates, and generate **beautiful cleaning reports** — all in seconds.


---

## 🚀 Features

- 🧹 Automatic Data Cleaning
- 🔁 Duplicate Detection & Removal
- 💧 Missing Value Handling
- 📧 Email Validation
- 📅 Date Parsing & Standardization
- ✍️ Text Normalization
- 📊 Detailed Cleaning Report
- 💾 Export Cleaned Data to CSV

---

## ⚙️ Installation

```bash
pip install suclepy
```

---

## 🧑‍💻 Usage Example

```python
import suclepy as sp
import pandas as pd

# Create a dirty dataset
df = pd.DataFrame({
    "Name": ["Subodh", "Amit", "Amit", "Riya", None],
    "Age": [21, None, 22, 20, 21],
    "Join_Date": ["2024/05/10", "10-05-2024", None, "2024-05-11", "May 12, 2024"],
    "Email": ["subodh@", "amit@example.com", "amit@example.com", None, "riya@gmail.com"]
})

# Clean the dataset automatically
report = sp.auto_clean(df)

# View summary
print(report.summary())

# View cleaned data
print(report.head())

# Save cleaned data
report.to_csv("cleaned_dataset.csv")
```

---

## 📝 Cleaning Report Example

```
SUCLEPY CLEANING REPORT

Total Rows (Before): 5  
Rows After Cleaning: 5  
Duplicates Removed: 1  
Missing Values Filled: 1  
Invalid Emails Found: 1  
Standardized Columns: 4  
Status: SUCCESS ✅
```

---

## 📁 Features in Detail

| Feature | Description |
|----------|-------------|
| **Automatic Cleaning** | Cleans the dataset intelligently with default strategies. |
| **Duplicate Removal** | Removes repeated rows to avoid redundancy. |
| **Missing Value Handling** | Fills missing numeric data with mean/median, categorical with mode, or drops rows. |
| **Email Validation** | Detects invalid email addresses. |
| **Date Parsing** | Converts dates to a standard `YYYY-MM-DD` format. |
| **Text Normalization** | Capitalizes and strips unnecessary spaces. |
| **CSV Export** | Saves your cleaned data easily. |
| **Cleaning Report** | Generates a clear and printable cleaning report. |

---

## 💡 Why SUCLEPY?

- 🧠 Friendly and easy-to-use API  
- ⚡ Minimal coding required to clean messy data  
- 📂 Works with any CSV or pandas DataFrame  
- 📈 Generates actionable insights and visual reports  

---

## 🔧 Configuration

You can configure global cleaning rules easily:

```python
import suclepy as sp

sp.config({
    "fill_missing_strategy": "mean",
    "validate_email": True,
    "drop_duplicates": True
})
```

---

## 📚 Documentation & Resources

- **GitHub Repository:** [https://github.com/subodhkryadav](https://github.com/subodhkryadav/suclepy)  
- **LinkedIn:** [Subodh Kumar Yadav](https://www.linkedin.com/in/subodh-kumar-yadav-522828293)

---

## 📝 License

This project is licensed under the **MIT License**.
