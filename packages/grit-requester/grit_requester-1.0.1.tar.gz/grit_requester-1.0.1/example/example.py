from dotenv import load_dotenv
load_dotenv()

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

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

print(resp.json())

# make a request from domain
users = ms.domain("user").list_all(
  filters=[{ "field": "name", "type": "eql", "value": "Admin" }]
)

print(users)

# you can save the domain context to reuse
user_ms = ms.domain("user")

user = user_ms.detail(users[0]["id"])

print(user)

