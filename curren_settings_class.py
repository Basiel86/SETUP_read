import json
import copy
import os
import sys

from cryptography.fernet import Fernet


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class CurrentSettings:
    # дериктория сохранения файлов

    enable_encryption = True
    misc_list = {'is_x_changed': False}
    cfg_dir = os.path.abspath(".") + "\\CFGs"
    graphs_list = {}
    file_info = {"filename": "", "md5": ""}
    temperature_list = ['temperature', 'температура', 'temp', 'внутреняя температура', 'внешняя температура',
                        'temperature (product)']
    time_list = ['time', 'время']
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
        'x_desire': 1,
        'savgol': 0,
        'color': 'black',
        'lang': "RU"}

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

        if filename != "demo":
            self.check_cfg_exist()

    def get_current_settings(self, graph_name):
        return self.graphs_list[graph_name]

    def set_x_min_max_all(self, xmin, xmax):
        for graph_settings in self.graphs_list:
            self.graphs_list[graph_settings]['xmin'] = float(xmin)
            self.graphs_list[graph_settings]['xmax'] = float(xmax)

    def set_x_major_all(self, xmajor):
        for graph_settings in self.graphs_list:
            self.graphs_list[graph_settings]['xmajor'] = float(xmajor)

    def set_x_change_status(self, x_change_status):
        self.misc_list['is_x_changed'] = x_change_status

    def get_x_change_status(self):
        return self.misc_list['is_x_changed']

    def write_current_settings(self, graph_name, cfg_name, cfg_value):
        """
        Пишем адресно новое значение настроек в классе
        """
        try:
            if not isinstance(cfg_value, bool):
                cfg_value = float(cfg_value)
            self.graphs_list[graph_name][cfg_name] = cfg_value
        except ValueError:
            self.graphs_list[graph_name][cfg_name] = cfg_value

    def check_cfg_file_exists_in_path(self, cfg_folder_path):
        file_exists = False
        if cfg_folder_path is not None:
            for filename in os.listdir(cfg_folder_path):
                if f'{self.file_info["filename"]}.bjson' == filename:
                    return True
            return False


    def check_cfg_exist(self):
        """
        Проверяем наличие конфига
        """
        paths_list = [get_srv_path(), self.cfg_dir]

        if self.check_cfg_file_exists_in_path(paths_list[0]):
            search_path = paths_list[0]
            print("CFG exists on SRV")
        else:
            search_path = paths_list[1]
            print("CFG Not found on Server, try to find on local")

        for filename in os.listdir(search_path):
            if f'{self.file_info["filename"]}.bjson' == filename:
                filepath = os.path.join(search_path, filename)
                self.decrypt(filepath)
                with open(filepath, encoding='utf-8') as json_file:
                    json_pack_list = json.load(json_file)
                    cfg_md5 = json_pack_list['file_info']['md5']
                    if cfg_md5 == self.file_info['md5']:
                        print("CFG exists")
                        self.graphs_list.update(json_pack_list['graphs_list'])
                        self.misc_list.update((json_pack_list['misc_list']))
                        self.encrypt(filepath)
                        return True
        print("CFG NOT exists")

    def json_export(self):
        """
        Экспортируем в Json файл весь массив
        """

        json_pack_list = {'graphs_list': self.graphs_list, 'file_info': self.file_info, 'misc_list': self.misc_list}

        json_string = json.dumps(json_pack_list, indent=5)

        filename = self.file_info["filename"]
        if filename != "demo":
            with open(f"{os.path.join(self.cfg_dir, filename)}.bjson", "w", encoding='utf-8') as outfile:
                outfile.write(json_string)
                outfile.close()
                self.encrypt(f"{os.path.join(self.cfg_dir, filename)}.bjson")

            # пишем на сервер
            try:
                if get_srv_path() is not None:
                    with open(f"{os.path.join(get_srv_path(), filename)}.bjson", "w", encoding='utf-8') as outfile:
                        outfile.write(json_string)
                        outfile.close()
                        self.encrypt(f"{os.path.join(get_srv_path(), filename)}.bjson")
            except Exception as ex:
                print("Copy to server error: ", ex)

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

        elif graph_name.lower() in self.time_list:
            graph_settings = {"ylabel_RU": "Время, ч:м:с",
                              "ylabel_EN": "Time, h:m:s",
                              "color": "black"}

            self.graphs_list[graph_name].update(graph_settings)

        else:
            graph_settings = {'ymax': 0.0,
                              "ymax_format": '%.1f',
                              "ymajor": 10.0,
                              "color": "darkgreen"}
            self.graphs_list[graph_name].update(graph_settings)

    def encrypt(self, filename):
        # Зашифруем файл и записываем его

        if self.enable_encryption:
            key = self.load_key()

            f = Fernet(key)
            with open(filename, 'rb') as file:
                # прочитать все данные файла
                file_data = file.read()
                encrypted_data = f.encrypt(file_data)
                with open(f"{filename}", 'wb') as file:
                    file.write(encrypted_data)

    def decrypt(self, filename):

        if is_encrypted(filename):
            key = self.load_key()
            # Расшифруем файл и записываем его
            f = Fernet(key)
            with open(filename, 'rb') as file:
                # читать зашифрованные данные
                encrypted_data = file.read()
            # расшифровать данные
            file.close()
            decrypted_data = f.decrypt(encrypted_data)
            # записать оригинальный файл
            with open(filename, 'wb') as file:
                file.write(decrypted_data)

    def load_key(self):
        # Загружаем ключ 'crypto.key' из текущего каталога
        return open(resource_path('cryptotoken.key'), 'rb').read()


def is_encrypted(filename):
    infile = open(filename, 'r')
    text = infile.readlines()
    if text[0] == "{\n":
        return False
    else:
        return True


def write_key():
    # Создаем ключ и сохраняем его в файл
    key = Fernet.generate_key()
    with open('crypto.key', 'wb') as key_file:
        key_file.write(key)


def is_srv_list_exist():
    srv_path_file_name = "Server config folder path.txt"
    srv_path_file_path = os.path.join(os.path.abspath("."),srv_path_file_name)
    if not os.path.exists(srv_path_file_path):
        with open(srv_path_file_path, 'w') as file:
            file.write(f"\\\\192.168.1.201\Public\Share\BVConfigs")
    return srv_path_file_path


def get_srv_path():
    srv_path_file_path = is_srv_list_exist()
    with open(srv_path_file_path) as f:
        lines = f.read()
        first = lines.split('\n', 1)[0]
    if os.path.exists(first):
        return first
    else:
        return None
