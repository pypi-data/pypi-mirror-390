# LDAP Connection Helper

This module provides a Python class `Connect` that simplifies connecting and interacting with an LDAP (Active Directory) server using the [`ldap3`](https://ldap3.readthedocs.io/) library.  
It supports both **simple authentication** (username/password) and **SASL GSSAPI** (Kerberos) authentication for **Linux** and **Windows** environments.

---

## 🔧 Features

- Cross-platform LDAP connection handling (Linux & Windows)
- Supports:
  - Simple bind (username + password)
  - SASL GSSAPI (Kerberos keytab or Windows domain)
- Automatically loads configuration from environment variables or `.env` file
- Provides helper methods for:
  - Searching users
  - Fetching user attributes
  - Querying accounts by custom filters
  - Returning all matching LDAP entries

---

## 📦 Dependencies

- **Python 3.10+**
- ldap3
- dotenv

---
## ⚙️ Environment Variables

You can define these in a .env file located in your home directory (~/.env on Linux, %HOMEPATH%\.env on Windows):
| Variable            | Description                     | Example                                |
| ------------------- | ------------------------------- | -------------------------------------- |
| `LDAP_HOST`         | LDAP server hostname            | `ldap.teradyne.com`                    |
| `LDAP_PORT`         | LDAP port (default: 389)        | `389`                                  |
| `LDAP_USER`         | LDAP username or principal      | `jdoe`                    |
| `LDAP_PASSWORD`     | LDAP password (for simple auth) | `MySecretPass`                         |
| `LDAP_KEYTAB`       | Path to Kerberos keytab file    | `/etc/security/jdoe.keytab`            |
| `LDAP_USER_BASE`    | Base DN for active users        | `cn=users,dc=company,dc=com`   |
| `LDAP_TERMED_BASE`  | Base DN for termed users        | `cn=termed,dc=company,dc=com`  |
| `LDAP_SRV_ACC_BASE` | Base DN for service accounts    | `cn=service,dc=company,dc=com` |

---

## 🚀 Usage Examples
### 1. Connect to LDAP
```python
from pyconnldap import Connect

# Simple bind (username/password)
conn = Connect(host='ldap.hostname.com', user='jdoe', password='MySecretPass')

# Kerberos keytab authentication
conn = Connect(host='ldap.hostname.com', user='jdoe', keytab='/etc/security/jdoe.keytab')

# If using environment variables. Make sure environment variables are loaded.
conn = Connect()
```
--- 
### 2. Search for a user in an OU
```python
found = conn.search_user(username='jdoe', ou=conn.USERS_BASE)
print(found)  # True if found, False otherwise

```
---
### 3. Get user attributes
```python
attrs = conn.get_user_attrib(username='jdoe', attrib=['mail', 'displayName'])
print(attrs)
# {'mail': ['jdoe@company.com'], 'displayName': ['John Doe']}
```
---
### 4. Search by arbitrary filter
```python
attrs = conn.get_attrib(search='mail=jdoe@company.com', attrib='cn')
print(attrs)
# {'cn': ['jdoe']}
```
---
### 5. Search all matches in an OU
```python
matches = conn.search_all_attrib(search='division=BPIT (070)', attrib='cn')
print(matches)
# [{'cn': ['User1']}, {'cn': ['User2']}, ...]
```

