import json
import copy
import os
import sys

from cryptography.fernet import Fernet


class CurrentSettings:
    # дериктория сохранения файлов
    cfg_dir = os.path.dirname(__file__) + "/CFGs"
    graphs_list = {}
    file_info = {"filename": "", "md5": ""}
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
        self.write_graphs(["Sin (x)"], filename="demo", md5="123")

        # если папки нет - создаем
        if not os.path.exists(self.cfg_dir):
            os.makedirs(self.cfg_dir)

        # дериктория сохранения файлов
        # save_dir = os.path.dirname(__file__) + "/Json"
        # file_path = os.path.join(save_dir, filename)
        # if not os.path.exists(save_dir):
        #     os.makedirs(save_dir)
        #
        # with open(f"{file_path}.json", "w", encoding='utf-8') as outfile:
        #     outfile.write(json_string)

    def write_graphs(self, header_row, filename, md5):
        """
        Инициализируем настройки всех графиков получви Список
        """
        self.filename = filename
        self.md5 = md5

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

        self.file_info["filename"] = filename
        self.file_info["md5"] = md5

        self.graphs_list["file_info"] = self.file_info
        if filename != "demo":
            print("CFG exists - ", self.check_cfg_exist())

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

    def check_cfg_exist(self):
        for filename in os.listdir(self.cfg_dir):
            if f'{self.file_info["filename"]}.json' == filename:
                print(self.read_json(json_filename=filename))
                return True
        return False

    def read_json(self, json_filename):
        json_path = os.path.join(self.cfg_dir, json_filename)
        with open(json_path, encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data
            # print("Json file:")
            # print(data['ylabel'])

    def json_export(self):
        """
        Экспортируем в Json файл весь массив
        """

        json_string = json.dumps(self.graphs_list, indent=5)

        filename = self.file_info["filename"]
        if filename != "demo1":
            with open(f"{os.path.join(self.cfg_dir, filename)}.json", "w", encoding='utf-8') as outfile:
                outfile.write(json_string)
            # encrypt(f"{os.path.join(self.cfg_dir, filename)}.json",load_key())

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


def write_key():
    # Создаем ключ и сохраняем его в файл
    key = Fernet.generate_key()
    with open('crypto.key', 'wb') as key_file:
        key_file.write(key)


def load_key():
    # Загружаем ключ 'crypto.key' из текущего каталога
    return open('cryptotoken.key', 'rb').read()


def encrypt(filename, key):
    # Зашифруем файл и записываем его
    f = Fernet(key)
    with open(filename, 'rb') as file:
        # прочитать все данные файла
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(f"{filename}", 'wb') as file:
            file.write(encrypted_data)


def decrypt(filename, key):
    # Расшифруем файл и записываем его
    f = Fernet(key)
    with open(filename, 'rb') as file:
        # читать зашифрованные данные
        encrypted_data = file.read()
    # расшифровать данные
    decrypted_data = f.decrypt(encrypted_data)
    # записать оригинальный файл
    with open(filename, 'wb') as file:
        file.write(decrypted_data)
