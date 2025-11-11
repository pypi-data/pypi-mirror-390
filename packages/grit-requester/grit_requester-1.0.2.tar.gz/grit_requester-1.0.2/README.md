# grit-requester

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

**grit-requester-python** is a python library to abstract requests to microservices built using Grit.

Features:

- 🔁 Automatic retry on `401 Unauthorized`
- 🔐 Per-service token cache with concurrency safety
- 💉 Config and HTTP client injection (perfect for testing)
- 📦 Full support for generics (`any`) in request/response
- 🧠 Context-aware: all requests support context.Context for cancellation, timeouts, and APM tracing

---

## ✨ Installation

```bash
pip install grit_requester
```

---

## 🚀 Usage Example

### Configure and do a request
```python
from grit_requester import GritService, GritConfig

# configure grit requester
config = GritConfig(
  base_url=os.getenv("SERVICE_BASE_URL"),
  auth_url=os.getenv("SERVICE_AUTH_URL"),
  token=os.getenv("SERVICE_TOKEN"),
  secret=os.getenv("SERVICE_SECRET"),
  context=os.getenv("SERVICE_CONTEXT"),
)

ms = GritService(config)

# doing a request
resp = ms.request(
  "GET",
  "/user/list",
)
```

### Make crud requests from a domain

Here you can call a domain passing the type and path to access the following base routers:

| Path              | Description                                |
| ----------------- | -------------------------------------------|
| add               | Create a new record                        |
| bulk              | Fetch specific records by IDs              |
| bulk_add          | Create up to 25 records in the same request|
| dead_detail       | Get a deleted record by ID                 |
| dead_list         | List deleted records (paginated)           |
| delete            | Soft-delete a record by ID                 |
| detail            | Get an active record by ID                 |
| edit              | Update specific fields                     |
| list              | List active records (paginated)            |
| list_one          | List one record based on params            |
| select_raw        | Execute a predefined raw SQL query safely  |

```python
from grit_requester import GritService, GritConfig

# configure grit requester
config = GritConfig(
  base_url=os.getenv("SERVICE_BASE_URL"),
  auth_url=os.getenv("SERVICE_AUTH_URL"),
  token=os.getenv("SERVICE_TOKEN"),
  secret=os.getenv("SERVICE_SECRET"),
  context=os.getenv("SERVICE_CONTEXT"),
)

ms = GritService(config)

# make a request from domain
users = ms.domain("user").list_all(
  filters=[{ "field": "name", "type": "eql", "value": "Admin" }]
)

# you can save the domain context to reuse
user_ms = ms.domain("user")

user = user_ms.detail(users[0]["id"])

```
---

## 🔧 License

MIT © [Not Empty](https://github.com/not-empty)

**Not Empty Foundation - Free codes, full minds**
