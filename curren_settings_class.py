import json
import copy


class CurrentSettings:
    graphs_list = {}

    graph_settings_array = {
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

    def __init__(self):
        self.graphs_list = {}

        # дериктория сохранения файлов
        # save_dir = os.path.dirname(__file__) + "/Json"
        # file_path = os.path.join(save_dir, filename)
        # if not os.path.exists(save_dir):
        #     os.makedirs(save_dir)
        #
        # with open(f"{file_path}.json", "w", encoding='utf-8') as outfile:
        #     outfile.write(json_string)

    def write_graphs(self, header_row, filename):
        for graph_name in header_row:
            self.graphs_list[graph_name] = copy.deepcopy(self.graph_settings_array)
        json_string = json.dumps(self.graphs_list, indent=5)

    def get_current_settings(self, graph_name):
        return self.graphs_list[graph_name]

    def write_current_settings(self, graph_name, cfg_name, cfg_value):
        # graph_settings_array_tmp = copy.deepcopy(self.graphs_list[graph_name])
        # graph_settings_array_tmp[cfg_name] = cfg_value
        # self.graphs_list[graph_name] = graph_settings_array_tmp
        self.graphs_list[graph_name][cfg_name] = cfg_value

    def json_export(self):
        json_string = json.dumps(self.graphs_list, indent=5)
        with open("Settings.json", "w", encoding='utf-8') as outfile:
            outfile.write(json_string)
