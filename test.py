import json

graph_settings = {'ymax': 10,
                  "ymax_format": '%.1f',
                  "ymax_base": 0.5,
                  "ylabel": "Скорость, м/с",
                  "color": "darkslateblue"}

json_string = json.dumps(graph_settings, indent=5)
json_string2 = json.dumps(graph_settings)

print(json_string2)

with open("sample.json", "w", encoding='utf-8') as outfile:
    outfile.write(json_string)

with open('sample.json', encoding='utf-8') as json_file:
    data = json.load(json_file)
    print("Json file:")
    print(data['ylabel'])