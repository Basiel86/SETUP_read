import json
import os

class CurrentSettings:
    graphs_list = {}

    graph_settings_array = {
        'ymin': '0',
        'ymax': '100',
        'ymajor': '5',
        'xmin': '0',
        'xmax': '100',
        'xmajor': '5',
        'ymax_format': '%.1f',
        'xlabel': 'X LABEL, ..',
        'ylabel': 'Y LABEL ..',
        'yadd': '0',
        'ymult': '1',
        'xmult_desire': '100',
        'savgol': '0',
        'color': 'black'}

    def __init__(self, header_row, filename):
        self.graphs_list={}
        for graph_name in header_row:
            self.graphs_list[graph_name] = self.graph_settings_array
        json_string = json.dumps(self.graphs_list, indent=5)

        # дериктория сохранения файлов
        # save_dir = os.path.dirname(__file__) + "/Json"
        # file_path = os.path.join(save_dir, filename)
        # if not os.path.exists(save_dir):
        #     os.makedirs(save_dir)
        #
        # with open(f"{file_path}.json", "w", encoding='utf-8') as outfile:
        #     outfile.write(json_string)

    @staticmethod
    def get_current_settings(self, graph_name):
        return self.graphs_list[graph_name]

    @staticmethod
    def write_current_settings(self, graph_name):
        pass

    #     graph_settings = {'ymax': ymax,
    #                       "ymax_format": '%.1f',
    #                       "ymax_base": 0.5,
    #                       "ylabel": "Скорость, м/с",
    #                       "color": "darkslateblue"}
    #
    #     return graph_settings
    # elif list_item_in_string(temperature_list, graph_name):
    #     graph_settings = {'ymax': 100,
    #                       "ymax_format": '%.0f',
    #                       "ymax_base": 10,
    #                       "ylabel": "Температура, °С",
    #                       "color": "firebrick"}
    #     return graph_settings
    # elif list_item_in_string(orientation_list, graph_name):
    #     graph_settings = {'ymax': 360,
    #                       "ymax_format": '%.0f',
    #                       "ymax_base": 30,
    #                       "ylabel": "Угловое положение, °",
    #                       "color": "darkolivegreen"}
    #     return graph_settings
    # elif list_item_in_string(magnetization_list, graph_name):
    #     graph_settings = {'ymax': 40,
    #                       "ymax_format": '%.1f',
    #                       "ymax_base": 5,
    #                       "ylabel": "Намагниченность, кА/м",
    #                       "color": "maroon"}
    #     return graph_settings
    # elif list_item_in_string(pressure_list, graph_name):
    #     graph_settings = {'ymax': 10,
    #                       "ymax_format": '%.1f',
    #                       "ymax_base": 1,
    #                       "ylabel": "Давление, МПа",
    #                       "color": "peru"}
    #     return graph_settings
