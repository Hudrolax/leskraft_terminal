import json


def parse_json(content):
    decoded_json = json.loads(content)
    team_leader = decoded_json.get('team_leader')
    teammates = decoded_json.get('teammates')
    print(team_leader)
    print(teammates)

json_str = """{
               "API_key":"plate1",
               "team_leader":"123",
               "teammates": [
	                {"1234":"Кладовщик"},
                    {"12345":"Грузчик"}
	                        ]
              }"""
parse_json(json_str)