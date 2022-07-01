import csv
import hashlib
import math
import numpy as np
import os
import tkinter
from PIL import Image
from datetime import datetime, date
from io import StringIO
from time import sleep
from tkinter import *
from tkinter import colorchooser
from tkinter import filedialog as fd
import xlrd

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.transforms
import pandas as pd
import win32clipboard
from matplotlib import pyplot as plt, dates
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.ticker import FormatStrFormatter, MultipleLocator, MaxNLocator
from scipy.signal import savgol_filter

import curren_settings_class as cs


class BViewer:
    EXP_DAY = '2022-07-30'
    header_item = ''
    export_path = ''

    def __init__(self):

        self.window = Tk()
        self.fig = plt.figure(figsize=(16, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().place(x=250, y=10)
        self.ax = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.window, pack_toolbar=False)

        self.filter_value_var = StringVar()
        self.filter_options = ["no filter",
                               "SAVG light",
                               "SAVG medium",
                               "SAVG heavy"]
        self.filter_variable = StringVar(self.window)
        self.language_variable = StringVar(self.window)
        self.filter_slider = tkinter.Scale(self.window, from_=0, to=200, orient='horizontal', width=20, length=200,
                                           command=self.change_savgol_slider)
        self.filter_value_combobox = OptionMenu(self.window, self.filter_variable, *self.filter_options,
                                                command=self.set_filter)
        self.language_options = ["RU", "EN"]
        self.language_value_combobox = OptionMenu(self.window, self.language_variable, *self.language_options,
                                                  command=self.change_language)
        self.filter_value_label = Label(master=self.window, text="Smoothing Value")
        self.noise_variable = IntVar()
        self.noise_checkbox = Checkbutton(master=self.window, variable=self.noise_variable, text="Enable Noise",
                                          onvalue=1, offvalue=0, command=self.noise_checkbox_change)

        # Lines
        self.line_1_variable = IntVar()
        self.line_1_checkbox = Checkbutton(master=self.window, variable=self.line_1_variable, text="Line 1 Red",
                                           onvalue=1, offvalue=0, command=self.line_1_checkbox_change)
        self.line_2_variable = IntVar()
        self.line_2_checkbox = Checkbutton(master=self.window, variable=self.line_2_variable, text="Line 2 Blue",
                                           onvalue=1, offvalue=0, command=self.line_2_checkbox_change)
        self.line_1_textbox = Entry(master=self.window, width=10)
        self.line_2_textbox = Entry(master=self.window, width=10)

        self.yaxis_name_textbox = Entry(master=self.window, width=35)
        self.xaxis_name_textbox = Entry(master=self.window, width=35)
        self.yaxis_name_label = Label(master=self.window, text="Y Axis Name")
        self.xaxis_name_label = Label(master=self.window, text="X Axis Name")
        self.x_desire_textbox = Entry(master=self.window, width=12)
        self.x_desire_label = Label(master=self.window, text="X Desire")
        self.y_mult_textbox = Entry(master=self.window, width=10)
        self.y_mult_label = Label(master=self.window, text="Y Mult")
        self.add_textbox = Entry(master=self.window, width=10)
        self.add_label = Label(master=self.window, text="Add")
        self.ymajor_textbox = Entry(master=self.window, width=10)
        self.xmajor_textbox = Entry(master=self.window, width=10)
        self.ymax_textbox = Entry(master=self.window, width=10)
        self.ymin_textbox = Entry(master=self.window, width=10)
        self.xmax_textbox = Entry(master=self.window, width=10)
        self.xmin_textbox = Entry(master=self.window, width=10)
        self.ymajor_label = Label(master=self.window, text="Y-Major")
        self.xmajor_label = Label(master=self.window, text="X-Major")
        self.ymax_label = Label(master=self.window, text="Y-Max")
        self.ymin_label = Label(master=self.window, text="Y-Min")
        self.xmax_label = Label(master=self.window, text="X-Max")
        self.xmin_label = Label(master=self.window, text="X-Min")
        self.status_label2 = Label(master=self.window, font=('arial bold', 10))
        self.status_label1 = Label(master=self.window, text="Selected:", font="12")
        self.graphs_listbox = Listbox(width=30, height=19)
        self.export_button = Button(master=self.window, text='Export Current', command=self.export_selected)
        self.open_button = Button(master=self.window, text='Open a File', command=self.select_file)
        self.autochart_button = Button(master=self.window, command=self.auto_chart, height=2, width=10,
                                       text="Auto Chart")
        self.color_button = Button(master=self.window, text='', command=self.select_color, width=2)

        self.cur_set = cs.CurrentSettings()

        self.cur_set.set_x_change_status(False)
        self.file_path = ""
        self.accept_graphs = ['speed', 'orientation', 'temperature', 'скорость', 'температура', 'угловое положение',
                              'magnetic intensity (sensors)']
        self.header_row = ""
        self.axis_table = ""
        self.filepath = ""

        self.slider_value = 0
        self.x_axis = []
        self.time_data_array = []
        self.y_axis = []
        self.x_axis_name = ''
        self.y_axis_name = ''
        self.x_axis_mult = ''
        self.y_axis_filter = ''
        self.savgol_value = 0

        self.form_init()

    # Ищем вхождение в Distance
    @staticmethod
    def setup_parse_row(filename):
        extension = os.path.splitext(filename)[1][1:]
        if extension == "ig~":
            with open(filename) as ig_file:
                graph_data = False
                header_row_index = 0
                for line in ig_file:
                    header_row_index += 1
                    line = line.rstrip()  # remove '\n' at end of line
                    if "[GRAPHDATA]" in line:
                        graph_data = True
                    if graph_data and "Distance" in line:
                        header_row = np.array(line.split('\t'))
                        # header_row = np.delete(header_row, 0)
                        return header_row, header_row_index
                    if header_row_index > 50:
                        break
        elif extension == "csv":
            with open(filename, encoding="utf-8-sig") as csv_file:
                reader = csv.reader(csv_file)
                headers = next(reader)
                if "Distance" or "Дистанция" in headers:
                    header_row = np.array(headers)
                    header_row_index = 1
                    return header_row, header_row_index

        elif extension == "xlsx":
            pandas_df_excel = pd.read_excel(filename)
            header_row = np.array(pandas_df_excel.columns.values)

            if "Distance" or "Дистанция" in header_row:
                header_row_index = 1
                return header_row, header_row_index

        raise ValueError("Дистанции в файле не обнаружено")

    def get_axis_from_file(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        header_row, header_row_index = self.setup_parse_row(filename)
        start_column = 0
        axis_array = 0
        if header_row[0] == "":
            start_column = 1
        if extension == "ig~":
            axis_array = np.loadtxt(filename, usecols=range(start_column, len(header_row)),
                                    skiprows=header_row_index + 9)
        elif extension == "csv":
            axis_array = np.loadtxt(filename, usecols=range(0, len(header_row)), skiprows=1, delimiter=',')
        elif extension == "xlsx":
            pandas_df_excel = pd.read_excel(filename)
            axis_array = np.array(pandas_df_excel)
        if header_row[0] == '':
            header_row = np.delete(header_row, 0)

        md5_val = self.md5(filename=filename)
        self.cur_set.write_graphs(header_row=header_row, filename=os.path.basename(filename), md5=md5_val)
        self.write_log(filepath=filename)
        # CS = cs.CurrentSettings(header_row, os.path.basename(filename))

        # print(header_row)

        if "Time" in header_row:
            y_index = np.argwhere(header_row == "Time")[0][0]
            date_time_array = np.empty((len(axis_array[:, y_index]), 1), dtype=object)
            for i, elem in enumerate(axis_array[:, y_index]):
                date_time_array[i, 0] = datetime(*xlrd.xldate_as_tuple(elem, 0))

            self.time_data_array = date_time_array

        self.graphs_listbox.delete(0, END)
        for graph_name in header_row:
            self.graphs_listbox.insert(END, graph_name)

        return axis_array, header_row

    @staticmethod
    def md5(filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def list_item_in_string(base_list, search_in_string):
        """
        Возвращает True если один из элементов List в Строке
        """

        for item in base_list:
            if item in search_in_string:
                return True
        return False

    @staticmethod
    def round_up_custom(num, step):
        """
        Округление вверх с шагом
        """
        return math.ceil(num / step) * step

    def make_graph(self, x_axis, y_axis, graph_name):
        """
        Рисуем сам график
        """
        # https://matplotlib.org/stable/gallery/color/named_colors.html

        colors = mcolors.CSS4_COLORS

        font = {'family': 'sans',
                'weight': 'normal',
                'size': 16}
        plt.rc('font', **font)

        toolbarFrame = Frame(master=self.window)
        toolbarFrame.grid(row=10, column=1)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        toolbar.place(x=10, y=50)

        self.toolbar.update()
        self.toolbar.place(x=250, y=810)

        if plt.get_fignums().__len__() == 0:
            pass
            # self.canvas.draw()
            # self.toolbar.update()
            # self.toolbar.place(x=250, y=810)

            # toolbarFrame = Frame(master=self.window)
            # toolbarFrame.grid(row=10, column=1)
            # toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
            # toolbar.place(x=10,y=50)
        else:
            plt.cla()
            # canvas.draw()

        # color = (0.5, 0, 0.5)

        self.ax.plot(x_axis, y_axis, color=colors['darkgreen'], linewidth=1)

        # if self.list_item_in_string(self.cur_set.magnetization_list, graph_name.lower()):
        if self.line_1_variable.get() == 1:
            x1, y1 = [0, self.round_up_custom(max(x_axis), 100)], [float(self.line_1_textbox.get()),
                                                                   float(self.line_1_textbox.get())]
            self.ax.plot(x1, y1, color=colors['red'], linewidth=2)
        if self.line_2_variable.get() == 1:
            x2, y2 = [0, self.round_up_custom(max(x_axis), 100)], [float(self.line_2_textbox.get()),
                                                                   float(self.line_2_textbox.get())]
            self.ax.plot(x2, y2, color=colors['blue'], linewidth=2)

        graph_settings = self.cur_set.graphs_list[graph_name]
        self.ax.grid()
        plt.xlim(0)
        plt.ylim(0)

        if self.y_axis_name != "":
            plt.xlabel("", labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
            plt.xlabel(self.cur_set.graphs_list[self.y_axis_name][f'xlabel_{self.language_variable.get()}'])
        else:
            plt.xlabel(graph_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})

        plt.ylabel(graph_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})

        # plt.title(graph_name, pad=30)
        # plt.title(graph_settings['color'], pad=15)
        # MultipleLocator(base=500) - Локатор с шагом в 500
        # MaxNLocator() - Автоматиечский локатор

        # Create offset transform by 5 points in x direction
        dy1 = -5 / 72.
        dx2 = -5 / 72
        offsetX = matplotlib.transforms.ScaledTranslation(0, dy1, self.fig.dpi_scale_trans)
        offsetY = matplotlib.transforms.ScaledTranslation(dx2, 0, self.fig.dpi_scale_trans)
        for label in self.ax.xaxis.get_majorticklabels():
            label.set_transform(label.get_transform() + offsetX)
        for label in self.ax.yaxis.get_majorticklabels():
            label.set_transform(label.get_transform() + offsetY)

        if self.cur_set.get_x_change_status() == False:
            self.ax.set_xlim(xmin=0, xmax=self.round_up_custom(max(x_axis), 100))
            self.ax.xaxis.set_major_locator(MaxNLocator())

            self.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        else:
            self.set_xminmax_no_event()
            self.set_xmajor_no_event()
        # ax.set_xlim(xmin=0,xmax=100)

        # Возвращаем настройки под график по имени Серии

        if graph_settings != {}:
            # Максимальное значение графика
            ymax = graph_settings['ymax']
            ymajor = graph_settings['ymajor']

            if ymax != 0:
                if graph_name == "Time":
                    ymin = round(np.min(y_axis), 1)
                else:
                    ymin = 0
                self.ax.set_ylim(ymin=ymin, ymax=ymax)

                self.y_major_locator_parse_and_set(ymin, ymax, ymajor)

            else:
                self.ax.set_ylim(ymin=0, ymax=self.round_up_custom(max(y_axis), 1))
                self.ax.yaxis.set_major_locator(MaxNLocator())

            if graph_name == "Time":
                # date_time_array = np.empty((len(self.y_axis), 1), dtype=object)
                # for i, elem in enumerate(self.y_axis):
                #     exceldate = datetime(*xlrd.xldate_as_tuple(elem, 0))
                #     # dt_format = datetime.strptime(exceldate,'%y:%m:%d').date()
                #     date_time_array[i, 0] = exceldate
                self.y_axis = self.time_data_array

            # Формат оси
            if graph_name == "Time":
                self.ax.yaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
            else:
                self.ax.yaxis.set_major_formatter(FormatStrFormatter(graph_settings['ymax_format']))

            # Лэйбл оси
            lang = self.language_variable.get()
            plt.ylabel(graph_settings[f'ylabel_{lang}'], labelpad=10,
                       font={'family': 'sans', 'weight': 'bold', 'size': 18})
            # Меняем цвет графика
            plt.gca().get_lines()[0].set_color(graph_settings['color'])
        else:
            if self.cur_set.get_x_change_status() is False:
                self.ax.yaxis.set_major_locator(MaxNLocator())

        # Формат оси
        if graph_name == "Time":
            plt.subplots_adjust(left=.1, bottom=.1, right=0.97, top=0.98, wspace=0, hspace=0)
        else:
            plt.subplots_adjust(left=.09, bottom=.1, right=0.97, top=0.98, wspace=0, hspace=0)

        self.canvas.draw()

    def graph_update(self):
        self.ax.plot(self.x_axis, self.y_axis)
        self.canvas.draw()

    def plot_event(self, event):

        # try:
        if self.graphs_listbox.curselection().__len__() != 0 or self.y_axis_name is not None:
            for i in self.graphs_listbox.curselection():
                self.y_axis_name = self.graphs_listbox.get(i)
            # self.filter_slider.set(0)
            self.form_update_current_settings()
            self.plot()
            self.get_minmax_major_from_graph()
            self.write_current_settings()
            self.status_label1.config(text=self.y_axis_name)
            self.color_button.config(bg=self.cur_set.graphs_list[self.y_axis_name]['color'])

    # except Exception as ex:
    #   print('plot_event' + str(ex))

    def plot(self):

        # try:
        self.x_axis_name = "Distance"

        if self.graphs_listbox.curselection().__len__() != 0 or self.y_axis_name is not None:
            for i in self.graphs_listbox.curselection():
                self.y_axis_name = self.graphs_listbox.get(i)

        if self.x_axis_name not in self.header_row:
            raise ResourceWarning("Дистанция не найдена")

        x_index = np.argwhere(self.header_row == self.x_axis_name)[0][0]
        y_index = np.argwhere(self.header_row == self.y_axis_name)[0][0]

        self.x_axis = self.axis_table[:, x_index]
        self.y_axis = self.axis_table[:, y_index]

        # Домножение давления
        if self.list_item_in_string(self.cur_set.pressure_list, self.y_axis_name.lower()):
            self.y_axis = self.y_axis / 9.869

        self.y_axis = self.y_axis * float(self.y_mult_textbox.get()) + float(self.add_textbox.get())

        x_axis_min_value = round(np.min(self.x_axis), 1)
        x_axis_max_value = round(np.max(self.x_axis), 1)
        y_axis_min_value = round(np.min(self.y_axis), 1)
        y_axis_max_value = round(np.max(self.y_axis), 1)
        y_axis_average_value = round(np.average(self.y_axis), 2)

        self.savgol_value = self.get_filter_slieder()
        self.y_axis_filter = savgol_filter(self.y_axis, window_length=self.savgol_value, polyorder=2)

        if self.noise_variable.get() == 1:
            # добавляем шумов
            # ***********************
            koeff = 200 / (y_axis_average_value * 6 + 12)
            rho = self.savgol_value / koeff / 150
            sr = rho
            n = len(self.y_axis)
            noise = white_noise(rho, sr, n)
            y_axis_noise = self.y_axis + noise

            tmp_savg = int(round(self.savgol_value / 20, 0))
            if tmp_savg < 3:
                tmp_savg = 3
            if tmp_savg % 2 == 0:
                tmp_savg = tmp_savg + 1

            y_axis_noise = savgol_filter(y_axis_noise, window_length=tmp_savg, polyorder=2)

            # ******************

            y_axis_use = y_axis_noise
        else:
            y_axis_use = self.y_axis_filter

        # coeff = self.savgol_value/2000
        # target_noise_db = self.savgol_value / 2000
        # target_noise_watts = coeff ** (target_noise_db / coeff)
        # mean_noise = 0
        # y_noise = np.random.normal(mean_noise, np.sqrt(target_noise_watts), len(self.y_axis))
        # y_axis_noise = self.y_axis + y_noise
        # ***********************

        x_desire = float(self.x_desire_textbox.get())
        if x_desire > 1:
            desire_coeff = float(self.x_desire_textbox.get()) / x_axis_max_value
        else:
            desire_coeff = 1
        self.x_axis_mult = self.x_axis * desire_coeff

        self.status_label2.config(text=f"Average={y_axis_average_value}   |   "
                                       f"X-MIN = {x_axis_min_value} : "
                                       f"X-MAX = {x_axis_max_value}   |   "
                                       f"Y-MIN = {y_axis_min_value} : "
                                       f"Y-MAX = {y_axis_max_value}   |   "
                                       f"{self.cur_set.file_info['filename']}", anchor='w')

        self.make_graph(self.x_axis_mult, y_axis_use, self.y_axis_name)

    # except Exception as ex:
    #    print('plot: ' + str(ex))

    def set_xminmax_no_event(self):
        self.cur_set.set_x_change_status(True)
        if self.xmin_textbox.get() != "" and self.xmax_textbox.get() != 0:
            self.form_update_current_settings()
            xmin = float(self.xmin_textbox.get())
            xmax = float(self.xmax_textbox.get())
            self.ax.set_xlim(xmin=xmin, xmax=xmax)
            self.cur_set.set_x_min_max_all(xmin=xmin, xmax=xmax)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmin', cfg_value=xmin)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmax', cfg_value=xmax)

    def set_xminmax(self, event):
        self.cur_set.set_x_change_status(True)
        if self.xmin_textbox.get() != "" and self.xmax_textbox.get() != 0:
            xmin = float(self.xmin_textbox.get())
            xmax = float(self.xmax_textbox.get())
            self.ax.set_xlim(xmin=xmin, xmax=xmax)
            self.cur_set.set_x_min_max_all(xmin=xmin, xmax=xmax)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmin', cfg_value=xmin)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmax', cfg_value=xmax)
            self.canvas.draw()

    def set_yadd(self, event):
        yadd = self.add_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='yadd', cfg_value=yadd)
        self.plot()

    def set_xmajor_no_event(self):
        self.cur_set.set_x_change_status(True)
        if self.xmajor_textbox.get() != "":
            xmajor_value = float(self.xmajor_textbox.get())
            self.ax.xaxis.set_major_locator(MultipleLocator(base=xmajor_value))
            self.cur_set.set_x_major_all(xmajor=xmajor_value)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmajor', cfg_value=xmajor_value)

    def set_xmajor(self, event):
        self.cur_set.set_x_change_status(True)
        if self.xmajor_textbox.get() != "":
            xmajor_value = float(self.xmajor_textbox.get())
            self.ax.xaxis.set_major_locator(MultipleLocator(base=xmajor_value))
            self.cur_set.set_x_major_all(xmajor=xmajor_value)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmajor', cfg_value=xmajor_value)
            self.canvas.draw()

    def set_x_desire(self, event):
        x_desire = self.x_desire_textbox.get()
        self.cur_set.set_x_desire_all(x_desire)
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name="x_desire",
                                            cfg_value=x_desire)
        self.cur_set.set_x_change_status(False)
        self.plot()
        self.get_minmax_major_from_graph()
        self.write_current_settings()

    def set_yminmax(self, event):
        self.y_change_status = True
        if self.ymin_textbox.get() != "" and self.ymax_textbox.get() != 0:
            ymin = float(self.ymin_textbox.get())
            ymax = float(self.ymax_textbox.get())
            ymajor = float(self.ymajor_textbox.get())
            self.y_major_locator_parse_and_set(ymin=ymin, ymax=ymax, ymajor=ymajor)
            self.ax.set_ylim(ymin=ymin, ymax=ymax)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymin', cfg_value=ymin)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymax', cfg_value=ymax)
            self.canvas.draw()

    def set_ymajor(self, event):

        ymin = float(self.ymin_textbox.get())
        ymax = float(self.ymax_textbox.get())
        ymajor = float(self.ymajor_textbox.get())

        self.y_major_locator_parse_and_set(ymin=ymin, ymax=ymax, ymajor=ymajor)
        # self.ax.yaxis.set_major_locator(MultipleLocator(base=ymajor_value))
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymajor', cfg_value=ymajor)
        self.canvas.draw()

    def y_major_locator_parse_and_set(self, ymin, ymax, ymajor):

        if ymajor == 0:
            ymajor = 0.0001

        ticks_count = (ymax - ymin) / ymajor

        if 2 < ticks_count < 100:
            # Локатор с фиксированным шагом
            self.ax.yaxis.set_major_locator(MultipleLocator(base=ymajor))
            # self.get_minmax_major_from_graph()
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymajor', cfg_value=ymin)
        else:
            self.ax.yaxis.set_major_locator(MaxNLocator())

    def set_xlabel_name(self, event):
        lang = self.cur_set.graphs_list[self.y_axis_name]['lang']
        xlabel_name = self.xaxis_name_textbox.get()
        plt.xlabel(xlabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name=f'xlabel_{lang}',
                                            cfg_value=xlabel_name)
        self.canvas.draw()

    def set_ylabel_name(self, event):
        lang = self.cur_set.graphs_list[self.y_axis_name]['lang']
        ylabel_name = self.yaxis_name_textbox.get()
        plt.ylabel(ylabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name=f'ylabel_{lang}',
                                            cfg_value=ylabel_name)
        self.canvas.draw()

    def set_filter(self, event):
        if self.graphs_listbox.curselection().__len__() != 0 or self.y_axis_name is not None:
            self.plot()
            self.graph_update()
            # self.get_minmax_major()
            self.form_update_current_settings()

    def set_ymult(self, event):
        ymult = self.y_mult_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name="ymult", cfg_value=ymult)
        self.plot()

    def change_language(self, event):
        lang = self.language_variable.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='lang',
                                            cfg_value=lang)
        self.form_update_current_settings()
        self.plot()

    def change_savgol_slider(self, event):

        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name="savgol",
                                            cfg_value=event)  # self.filter_slider.get())
        self.plot()
        # self.get_minmax_major()
        # self.write_current_settings(self.y_axis_name)
        # self.form_update_current_settings()

    def get_filter_slieder(self):
        slider_value = self.filter_slider.get() + 3

        if slider_value % 2 == 0:
            slider_value = slider_value + 1
            self.filter_slider.set(slider_value - 3)

        return slider_value

    def get_minmax_major_from_graph(self):

        xmin, xmax = plt.gca().get_xlim()
        self.xmin_textbox.delete(0, END)
        self.xmax_textbox.delete(0, END)
        self.xmin_textbox.insert(0, round(xmin, 1))
        self.xmax_textbox.insert(0, round(xmax, 1))

        ymin, ymax = plt.gca().get_ylim()
        self.ymin_textbox.delete(0, END)
        self.ymax_textbox.delete(0, END)
        self.ymin_textbox.insert(0, round(ymin, 1))
        self.ymax_textbox.insert(0, round(ymax, 1))

        xlabel_name = plt.gca().get_xlabel()
        self.xaxis_name_textbox.delete(0, END)
        self.xaxis_name_textbox.insert(0, xlabel_name)

        ylabel_name = plt.gca().get_ylabel()
        self.yaxis_name_textbox.delete(0, END)
        self.yaxis_name_textbox.insert(0, ylabel_name)

        xmajor_list = plt.gca().xaxis.major.formatter.locs
        xmajor = xmajor_list[1] - xmajor_list[0]
        self.xmajor_textbox.delete(0, END)
        self.xmajor_textbox.insert(0, xmajor)

        ymajor_list = plt.gca().yaxis.major.formatter.locs
        ymajor = ymajor_list[1] - ymajor_list[0]
        self.ymajor_textbox.delete(0, END)
        self.ymajor_textbox.insert(0, ymajor)

    def write_current_settings(self):

        xmin = self.xmin_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmin', cfg_value=xmin)

        xmax = self.xmax_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmax', cfg_value=xmax)

        if self.xmajor_textbox.get() != "":
            xmajor_value = float(self.xmajor_textbox.get())
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xmajor', cfg_value=xmajor_value)

        ymin = self.ymin_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymin', cfg_value=ymin)

        ymax = self.ymax_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymax', cfg_value=ymax)

        ymajor_value = self.ymajor_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymajor', cfg_value=ymajor_value)

        xlabel_name = self.xaxis_name_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='xlabel', cfg_value=xlabel_name)

        ylabel_name = self.yaxis_name_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ylabel', cfg_value=ylabel_name)

        slider_value = self.filter_slider.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='savgol', cfg_value=slider_value)

        yadd = self.add_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='yadd', cfg_value=yadd)

        ymult = self.y_mult_textbox.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='ymult', cfg_value=ymult)

        line_1_ch = self.line_1_variable.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_1_ch', cfg_value=line_1_ch)
        line_1_value = float(self.line_1_textbox.get())
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_1_value',
                                            cfg_value=line_1_value)
        line_2_ch = self.line_2_variable.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_2_ch', cfg_value=line_2_ch)
        line_2_value = float(self.line_2_textbox.get())
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_2_value',
                                            cfg_value=line_2_value)

    def copy2clipboard(fig=None):
        '''
        copy a matplotlib figure to clipboard as BMP on windows
        http://stackoverflow.com/questions/7050448/write-image-to-windows-clipboard-in-python-with-pil-and-win32clipboard
        '''
        if not fig:
            fig = matplotlib.pyplot.gcf()

        output = StringIO()
        # fig.savefig(output, format='bmp') # bmp not supported
        buf = fig.canvas.buffer_rgba()
        w = int(fig.get_figwidth() * fig.dpi)
        h = int(fig.get_figheight() * fig.dpi)
        im = Image.frombuffer('RGBA', (w, h), buf)
        im.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # The file header off-set of BMP is 14 bytes
        output.close()

        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            # win32clipboard.SetClipboardData(win32clipboard.CF_BITMAP, data) # did not work!
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)  # DIB = device independent bitmap
            win32clipboard.CloseClipboard()
        except:
            sleep(0.2)
            # copy2clipboard(fig)

    # Берем настройки из конфига
    def form_update_current_settings(self):

        if self.y_axis_name != "":
            lang = self.cur_set.graphs_list[self.y_axis_name]['lang']

            xmin = self.cur_set.graphs_list[self.y_axis_name]['xmin']
            self.xmin_textbox.delete(0, END)
            self.xmin_textbox.insert(0, xmin)

            xmax = self.cur_set.graphs_list[self.y_axis_name]['xmax']
            self.xmax_textbox.delete(0, END)
            self.xmax_textbox.insert(0, xmax)

            xmajor_value = self.cur_set.graphs_list[self.y_axis_name]['xmajor']
            self.xmajor_textbox.delete(0, END)
            self.xmajor_textbox.insert(0, xmajor_value)

            ymin = self.cur_set.graphs_list[self.y_axis_name]['ymin']
            self.ymin_textbox.delete(0, END)
            self.ymin_textbox.insert(0, ymin)

            ymax = self.cur_set.graphs_list[self.y_axis_name]['ymax']
            self.ymax_textbox.delete(0, END)
            self.ymax_textbox.insert(0, ymax)

            ymajor_value = self.cur_set.graphs_list[self.y_axis_name]['ymajor']
            self.ymajor_textbox.delete(0, END)
            self.ymajor_textbox.insert(0, ymajor_value)

            xlabel_name = self.cur_set.graphs_list[self.y_axis_name][f'xlabel_{lang}']
            self.xaxis_name_textbox.delete(0, END)
            self.xaxis_name_textbox.insert(0, xlabel_name)

            ylabel_name = self.cur_set.graphs_list[self.y_axis_name][f'ylabel_{lang}']
            self.yaxis_name_textbox.delete(0, END)
            self.yaxis_name_textbox.insert(0, ylabel_name)

            slider_value = self.cur_set.graphs_list[self.y_axis_name]['savgol']
            self.filter_slider.set(slider_value)

            yadd = self.cur_set.graphs_list[self.y_axis_name]['yadd']
            self.add_textbox.delete(0, END)
            self.add_textbox.insert(0, yadd)

            ymult = self.cur_set.graphs_list[self.y_axis_name]['ymult']
            self.y_mult_textbox.delete(0, END)
            self.y_mult_textbox.insert(0, ymult)

            x_desire = self.cur_set.graphs_list[self.y_axis_name]['x_desire']
            self.x_desire_textbox.delete(0, END)
            self.x_desire_textbox.insert(0, x_desire)

            line_1_ch = self.cur_set.graphs_list[self.y_axis_name]['line_1_ch']
            if line_1_ch == 1:
                self.line_1_variable.set(1)
            else:
                self.line_1_variable.set(0)

            line_1_value = self.cur_set.graphs_list[self.y_axis_name]['line_1_value']
            self.line_1_textbox.delete(0, END)
            self.line_1_textbox.insert(0, line_1_value)

            line_2_ch = self.cur_set.graphs_list[self.y_axis_name]['line_2_ch']
            if line_2_ch == 1:
                self.line_2_variable.set(1)
            else:
                self.line_2_variable.set(0)
            line_2_value = self.cur_set.graphs_list[self.y_axis_name]['line_2_value']
            self.line_2_textbox.delete(0, END)
            self.line_2_textbox.insert(0, line_2_value)

    def select_file(self):

        self.cur_set.json_export()
        filetypes = (
            ('Iligraph files', '*.ig~'),
            ('Excel files', '*.csv *.xlsx')
        )

        self.cur_set.set_x_change_status(False)
        self.form_update_current_settings()

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=os.path.abspath(__file__),
            filetypes=filetypes)

        if filename != "":
            self.file_path = os.path.dirname(filename)

            self.status_label1.config(text="Choose profile...")
            # filepath = pathlib.Path(filename).parent.resolve()
            self.axis_table, self.header_row = self.get_axis_from_file(filename)

    def open_with_file(self, file_path):

        self.cur_set.set_x_change_status(False)
        self.form_update_current_settings()

        self.status_label1.config(text="Choose profile...")
        self.axis_table, self.header_row = self.get_axis_from_file(file_path)

    def select_color(self):
        rgb, hex_color = colorchooser.askcolor(title="Select a color")
        if hex_color is not None:
            self.color_button.config(bg=hex_color)
            self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='color', cfg_value=hex_color)
            self.plot()

    def auto_chart(self):
        self.cur_set.set_x_change_status(False)
        self.add_textbox.delete(0, END)
        self.add_textbox.insert(0, 0)
        self.y_mult_textbox.delete(0, END)
        self.y_mult_textbox.insert(0, 1)
        self.cur_set.set_x_desire_all(1)

        self.plot()
        self.get_minmax_major_from_graph()
        self.write_current_settings()
        # self.get_minmax_major()
        self.form_update_current_settings()

    def export_selected(self):

        try:
            np.savetxt(f"{self.file_path}/{self.y_axis_name}.csv", np.transpose([self.x_axis_mult, self.y_axis_filter]),
                       delimiter=',',
                       header=f"Distance,{self.y_axis_name}",
                       comments='')
        except Exception as ex:
            print("Nothing to export: " + str(ex))

    def noise_checkbox_change(self):
        if self.noise_variable.get() == 1:
            self.filter_value_label.config(text="Noise Value")
        else:
            self.filter_value_label.config(text="Smoothing Value")

    def line_1_textbox_change(self, event):
        line_1_value = self.line_1_textbox.get()
        print("line_1_change_textbox")
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_1_value',
                                            cfg_value=line_1_value)
        self.plot()

    def line_2_textbox_change(self, event):
        line_2_value = self.line_2_textbox.get()
        print("line_2_change_textbox")
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_2_value',
                                            cfg_value=line_2_value)
        self.plot()

    def line_1_checkbox_change(self):
        line_1_ch = self.line_1_variable.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_1_ch', cfg_value=line_1_ch)
        self.plot()

    def line_2_checkbox_change(self):
        line_2_ch = self.line_2_variable.get()
        self.cur_set.write_current_settings(graph_name=self.y_axis_name, cfg_name='line_2_ch', cfg_value=line_2_ch)
        self.plot()

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception as ex:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def write_log(self, filepath=""):
        log_path = r"\\vasilypc\Vasily Shared (Full Access)\###\BVLog\BVLOG.txt"

        try:
            if not os.path.exists(log_path):
                with open(log_path, 'w') as file:
                    file.write("")
                file.close()

            log_file = open(log_path, 'a', encoding='utf-8')

            now_date_time = datetime.today().strftime("%d.%m.%Y %H:%M:%S")
            username = os.getenv('username')
            pc_name = os.environ['COMPUTERNAME']

            log_file.write(f'{now_date_time}\t'
                           f'user: {username}\t\t'
                           f'pc: {pc_name}\t\t'
                           f'{self.cur_set.file_info["filename"]}\t'
                           f'{filepath}\n')
            log_file.close()
        except Exception as ex:
            print("Log export error: ", ex)

    def form_init(self):
        exp_date_formatted = datetime.strptime(self.EXP_DAY, "%Y-%m-%d").date()
        now_date = date.today()
        days_left = exp_date_formatted - now_date

        # the main Tkinter window

        if exp_date_formatted >= now_date:
            self.window.title(f'BViewer, expires in (days): {days_left.days}')
            self.window.geometry("1900x850")
            ico_abs_path = self.resource_path('BV2.ico')
            self.window.wm_iconbitmap(ico_abs_path)
            self.graphs_listbox.bind('<<ListboxSelect>>', self.plot_event)
            self.status_label2.config(text="Stats...")
            self.xmin_textbox.bind('<Return>', self.set_xminmax)
            self.xmax_textbox.bind('<Return>', self.set_xminmax)
            self.ymin_textbox.bind('<Return>', self.set_yminmax)
            self.ymax_textbox.bind('<Return>', self.set_yminmax)
            self.xmajor_textbox.bind('<Return>', self.set_xmajor)
            self.ymajor_textbox.bind('<Return>', self.set_ymajor)
            self.add_textbox.insert(0, "0")
            self.add_textbox.bind('<Return>', self.set_yadd)
            self.y_mult_textbox.insert(0, "1")
            self.y_mult_textbox.bind('<Return>', self.set_ymult)
            self.x_desire_textbox.insert(0, "1")
            self.x_desire_textbox.bind('<Return>', self.set_x_desire)
            self.xaxis_name_textbox.bind('<Return>', self.set_xlabel_name)
            self.yaxis_name_textbox.bind('<Return>', self.set_ylabel_name)
            self.filter_variable.set(self.filter_options[0])
            self.status_label2.place(x=800, y=820)
            self.filter_value_label.place(x=10, y=380)
            self.noise_checkbox.place(x=120, y=380)
            self.filter_slider.place(x=10, y=400)
            self.status_label1.place(x=10, y=5)
            self.status_label1.config(text="Select file...")
            self.open_button.place(x=10, y=35, width=70, height=25)
            self.export_button.place(x=85, y=35, width=90, height=25)
            self.language_value_combobox.place(x=185, y=32, width=50, height=30)
            self.language_variable.set(self.language_options[0])
            self.graphs_listbox.place(x=10, y=70)
            self.xmin_label.place(x=10, y=450)
            self.xmax_label.place(x=80, y=450)
            self.xmajor_label.place(x=150, y=450)
            self.xmin_textbox.place(x=10, y=471)
            self.xmax_textbox.place(x=80, y=471)
            self.xmajor_textbox.place(x=150, y=471)
            self.ymin_label.place(x=10, y=490)
            self.ymax_label.place(x=80, y=490)
            self.ymajor_label.place(x=150, y=490)
            self.ymin_textbox.place(x=10, y=516)
            self.ymax_textbox.place(x=80, y=516)
            self.ymajor_textbox.place(x=150, y=516)
            self.xaxis_name_label.place(x=10, y=540)
            self.xaxis_name_textbox.place(x=10, y=561)
            self.yaxis_name_label.place(x=10, y=580)
            self.yaxis_name_textbox.place(x=10, y=601)
            self.add_label.place(x=10, y=620)
            self.add_textbox.place(x=10, y=641)
            self.y_mult_label.place(x=80, y=620)
            self.y_mult_textbox.place(x=80, y=641)
            self.x_desire_label.place(x=150, y=620)
            self.x_desire_textbox.place(x=150, y=641)

            self.line_1_textbox.bind('<Return>', self.line_1_textbox_change)
            self.line_1_checkbox.place(x=10, y=670)
            self.line_1_textbox.place(x=100, y=670)

            self.line_2_textbox.bind('<Return>', self.line_2_textbox_change)
            self.line_2_checkbox.place(x=10, y=695)
            self.line_2_textbox.place(x=100, y=695)

            self.autochart_button.place(x=10, y=750, width=70, height=25)
            self.color_button.place(x=200, y=750)

            try:
                open_with_path = str(sys.argv[1])
                # print("sys path - " + open_with_path)
                self.file_path = os.path.dirname(str(sys.argv[1]))
                print(self.file_path)
                self.open_with_file(open_with_path)
            except Exception as ex:
                # print("sys path error: " + str(ex))
                x = np.linspace(0, 300, 150)
                y = np.sin(2 * np.pi * (x - 0.01 * 1)) + 1

                self.make_graph(x, y, "Sin (x)")

            def on_closing():
                try:
                    self.cur_set.json_export()
                    self.window.destroy()
                    sys.exit()
                except:
                    sys.exit()

            self.window.protocol("WM_DELETE_WINDOW", on_closing)

            self.window.mainloop()

        else:
            self.window.geometry("1900x850")
            self.window.title('BaZViewer - EXPIRED')
            self.window.geometry("300x50")

            exp_label = Label(master=self.window, text="Your version has expired", fg='red', font=15)
            exp_label.pack()
            exp_label2 = Label(master=self.window, text="Please update", fg='red', font=15)
            exp_label2.pack()

            def on_closing():
                self.window.destroy()
                sys.exit()

            self.window.protocol("WM_DELETE_WINDOW", on_closing)
            self.window.mainloop()


def white_noise(rho, sr, n, mu=0):
    sigma = rho * np.sqrt(sr / 2)
    noise = np.random.normal(mu, sigma, n)
    return noise


if __name__ == "__main__":
    BViewer()
