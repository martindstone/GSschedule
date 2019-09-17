import pd
import json
from datetime import datetime, timedelta

api_key = 'YOUR_PD_API_KEY'
number_of_overrides_to_create = 365
fetch_users_query = "SOME_QUERY_TEXT_FOR_USERS"

def ts_string(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

# Get some users to create overrides with...
# Make sure you have a query parameter that gives you users that can be responders,
# or else adding the override will fail
users = pd.fetch_users(api_key=api_key, params={"query": fetch_users_query})
print(f"Fetched {len(users)} users to create overrides")


schedule_create_body = {
  "schedule": {
    "name": "Test Schedule 1",
    "type": "schedule",
    "time_zone": "America/New_York",
    "description": "Test schedule",
    "schedule_layers": [
      {
        "name": "Forever Rotation",
        "start": "2019-09-17T00:00:00-05:00",
        "rotation_virtual_start": "2019-09-17T00:00:00-05:00",
        "rotation_turn_length_seconds": 86400,
        "users": [
          {
            "user": {
              "id": users[-1]["id"],
              "type": "user"
            }
          }
        ]
      }
    ]
  }
}

schedule = pd.request(api_key=api_key, endpoint="schedules", method="POST", data=schedule_create_body)
schedule_id = schedule["schedule"]["id"]
print(f"Created schedule {schedule_id} with forever on-call {users[-1]['summary']}")

input("Press Enter to create overrides...")


print(f"Going to create {number_of_overrides_to_create} overrides...")

dt = datetime.utcnow()
override_count = 0
while (override_count < number_of_overrides_to_create):
    user = users[override_count % len(users)]
    override_body = {
        "override": {
            "start": ts_string(dt),
            "end": ts_string(dt + timedelta(days=1)),
            "user": {
                "id": user["id"],
                "type": "user_reference"
            }
        }
    }
    override = pd.request(api_key=api_key, endpoint=f"schedules/{schedule_id}/overrides", method="POST", data=override_body)
    user_name = override['override']['user']['summary']
    start = override['override']['start']
    end = override['override']['end']
    dt = dt + timedelta(days=1)
    override_count += 1
    print(f"Created override #{override_count} for {user_name} ({start} - {end})")


input("Press Enter to create a non-aligned overlapping override...")

# Create a non-aligned override and see what happens
dt = datetime.utcnow() + timedelta(hours=8)
override_body = {
    "override": {
        "start": ts_string(dt),
        "end": ts_string(dt + timedelta(hours=23)),
        "user": {
            "id": users[-1]["id"],
            "type": "user_reference"
        }
    }
}
override = pd.request(api_key=api_key, endpoint=f"schedules/{schedule_id}/overrides", method="POST", data=override_body)
user_name = override['override']['user']['summary']
start = override['override']['start']
end = override['override']['end']
print(f"\nCreated overlapping non-aligned override for {user_name} ({start} - {end})")
