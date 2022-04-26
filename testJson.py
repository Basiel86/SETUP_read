import json
import curren_settings_class

cs = curren_settings_class.CurrentSettings()

header_row = ['Distance', 'File', 'Time', 'Speed', 'Pendulum', 'Pressure (product)', 'Temperature (battery module)']

graph_settings_array2 = {
    'ymin': 5,
    'ymax': 50,
    'ymajor': 5,
    'xmin': 0,
    'xmax': 100,
    'xmajor': 5,
    'ymax_format': '%.1f',
    'xlabel': 'X LABEL, ..',
    'ylabel': 'Y LABEL ..',
    'yadd': 1,
    'ymult': 1,
    'xmult_desire': 100,
    'savgol': 0,
    'color': 'black',
    'is_changed': False}

cs.write_graphs(header_row, "122.txt")

print(cs.graphs_list["Distance"])
print(cs.graphs_list["Speed"])

print('--------------------------')

cs.write_current_settings("Speed", 'ymin', 50)
cs.write_current_settings("Speed", 'ymax', 99)
cs.write_current_settings("Distance", 'ymajor', 77)

print(cs.graphs_list["Distance"])
print(cs.graphs_list["Speed"])

print('--------------------------')

# graph_settings = {'ymax': 10,
#                   "ymax_format": '%.1f',
#                   "ymax_base": 0.5,
#                   "ylabel": "Скорость, м/с",
#                   "color": "darkslateblue"}
#
# json_string = json.dumps(graph_settings, indent=5)
# json_string2 = json.dumps(graph_settings)

# print(json_string2)

# with open("sample.json", "w", encoding='utf-8') as outfile:
#     outfile.write(json_string)
#
# with open('sample.json', encoding='utf-8') as json_file:
#     data = json.load(json_file)
#     print("Json file:")
#     print(data['ylabel'])
