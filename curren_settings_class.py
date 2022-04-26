import json
import copy


class CurrentSettings:
    graphs_list = {}

    temperature_list = ['temperature', 'температура', 'temp']
    speed_list = ['speed', 'скорость']
    signal_loss_list = ['потеря сигнала', 'signal loss', 'abnormal sensors t1', 'abnormal sensors t2']
    orientation_list = ['orientation', 'угловое положение', 'угол', 'angle']
    pressure_list = ['pressure (product)', 'pressure', 'давление']
    magnetization_list = ['magnetic induction (sensors)', 'magnetic induction (wt gauge)',
                          'magnetic intensity (sensors)',
                          'magnetic intensity (wt gauge)', 'magnetization', 'намагниченность', 'magn']
    distance_dict = {"RU": "Дистанция от камеры запуска, м", "EN": "Distance, m"}

    graph_settings_array = {
        'ymin': 0.0,
        'ymax': 0.0,
        'ymajor': 5.0,
        'xmin': 0.0,
        'xmax': 100.0,
        'xmajor': 5.0,
        'ymax_format': '%.1f',
        'xlabel_RU': '# Ось X, ..',
        'xlabel_EN': '# X LABEL, ..',
        'ylabel_RU': '# Ось Y ..',
        'ylabel_EN': '# Y LABEL ..',
        'yadd': 0.0,
        'ymult': 1.0,
        'xmult_desire': 100,
        'savgol': 0,
        'color': 'black',
        'lang': "RU",
        'is_changed': False}

    def __init__(self):
        self.graphs_list = {}
        self.write_graphs(["Sin (x)"])

        # дериктория сохранения файлов
        # save_dir = os.path.dirname(__file__) + "/Json"
        # file_path = os.path.join(save_dir, filename)
        # if not os.path.exists(save_dir):
        #     os.makedirs(save_dir)
        #
        # with open(f"{file_path}.json", "w", encoding='utf-8') as outfile:
        #     outfile.write(json_string)

    def write_graphs(self, header_row, filename="tmp"):
        """
        Инициализируем настройки всех графиков получви Список
        """
        for graph_name in header_row:
            self.graphs_list[graph_name] = copy.deepcopy(self.graph_settings_array)
            self.presets_apply(graph_name=graph_name)
            if "#" in self.graphs_list[graph_name]['ylabel_RU']:
                self.write_current_settings(graph_name=graph_name, cfg_name="ylabel_RU", cfg_value=graph_name)
                self.write_current_settings(graph_name=graph_name, cfg_name="ylabel_EN", cfg_value=graph_name)
            if "#" in self.graphs_list[graph_name]['xlabel_RU']:
                self.write_current_settings(graph_name=graph_name, cfg_name="xlabel_RU",
                                            cfg_value="Дистанция от камеры запуска, м")
                self.write_current_settings(graph_name=graph_name, cfg_name="xlabel_EN", cfg_value="Distance, m")

    def get_current_settings(self, graph_name):
        return self.graphs_list[graph_name]

    def set_x_min_max_all(self, xmin, xmax):
        for graph_settings in self.graphs_list:
            self.graphs_list[graph_settings]['xmin'] = float(xmin)
            self.graphs_list[graph_settings]['xmax'] = float(xmax)

    def set_x_major_all(self, xmajor):
        for graph_settings in self.graphs_list:
            self.graphs_list[graph_settings]['xmajor'] = float(xmajor)

    def write_current_settings(self, graph_name, cfg_name, cfg_value):
        """
        Пишем адресно новое значение настроек в классе
        """
        try:
            cfg_value = float(cfg_value)
            self.graphs_list[graph_name][cfg_name] = float(cfg_value)
        except ValueError:
            self.graphs_list[graph_name][cfg_name] = cfg_value

    def json_export(self):
        """
        Экспортируем в Json файл весь массив
        """
        json_string = json.dumps(self.graphs_list, indent=5)
        with open("Settings.json", "w", encoding='utf-8') as outfile:
            outfile.write(json_string)

    def presets_apply(self, graph_name):
        """
        По названию графика создаем Словарь с характеристиками графика
        Обновляем его в целевом
        """

        # https://stackoverflow.com/questions/22408237/named-colors-in-matplotlib

        # darkcyan
        # darkgoldenrod
        # maroon
        # darkslateblue
        # darkolivegreen
        # olive
        # cadetblue
        # peru

        if graph_name.lower() in self.speed_list:

            graph_settings = {'ymax': 5,
                              "ymax_format": '%.1f',
                              "ymajor": 0.5,
                              "ylabel_RU": "Скорость, м/с",
                              "ylabel_EN": "Speed, m/s",
                              "color": "darkslateblue"}

            self.graphs_list[graph_name].update(graph_settings)

        elif graph_name.lower() in self.temperature_list:
            graph_settings = {'ymax': 100,
                              "ymax_format": '%.0f',
                              "ymajor": 10,
                              "ylabel_RU": "Температура, °С",
                              "ylabel_EN": "Temperature, deg",
                              "color": "firebrick"}
            self.graphs_list[graph_name].update(graph_settings)

        elif graph_name.lower() in self.orientation_list:
            graph_settings = {'ymax': 360,
                              "ymax_format": '%.0f',
                              "ymajor": 30,
                              "ylabel_RU": "Угловое положение, °",
                              "ylabel_EN": "Orientation, °",
                              "color": "darkolivegreen"}

            self.graphs_list[graph_name].update(graph_settings)

        elif graph_name.lower() in self.magnetization_list:
            graph_settings = {'ymax': 40,
                              "ymax_format": '%.0f',
                              "ymajor": 5,
                              "ylabel_RU": "Намагниченность, кА/м",
                              "ylabel_EN": "Magnetization, kA/m",
                              "color": "maroon"}

            self.graphs_list[graph_name].update(graph_settings)

        elif graph_name.lower() in self.pressure_list:
            graph_settings = {'ymax': 10,
                              "ymax_format": '%.1f',
                              "ymajor": 1,
                              "ylabel_RU": "Давление, МПа",
                              "ylabel_EN": "Pressure, MPa",
                              "color": "peru"}

            self.graphs_list[graph_name].update(graph_settings)

        elif graph_name.lower() in self.signal_loss_list:
            graph_settings = {'ymax': 100,
                              "ymax_format": '%.0f',
                              "ymajor": 10,
                              "ylabel_RU": "Потеря сигнала, %",
                              "ylabel_EN": "Signal loss, %",
                              "color": "darkgreen"}

            self.graphs_list[graph_name].update(graph_settings)

        else:
            graph_settings = {'ymax': 0.0,
                              "ymax_format": '%.1f',
                              "ymajor": 10.0,
                              "color": "darkgreen"}
            self.graphs_list[graph_name].update(graph_settings)
