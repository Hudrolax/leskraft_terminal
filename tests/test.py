import json


def parse_json(content):
    decoded_json = json.loads(content)
    team_leader = decoded_json.get('team_leader')
    teammates = decoded_json.get('teammates')
    print(team_leader)
    print(teammates)

teammates = ['123', '234']
json_str = json.dumps(teammates)
print(json_str)