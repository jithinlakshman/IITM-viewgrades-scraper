# viewgradesAPI

## Description

Package for fetching grade card info from IITM Server in json format

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```python
from viewgradesAPI import ViewGrades


remote = ViewGrades()
remote.login(LDAP_USERNAME, LDAP_PASSWORD)

data: dict = remote.fetchInfo()
```
