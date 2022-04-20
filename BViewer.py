import math
import tkinter
import numpy as np
import pandas as pd
import os

from matplotlib.ticker import FormatStrFormatter, MultipleLocator, MaxNLocator
import matplotlib.colors as mcolors
import matplotlib.transforms
from scipy.signal import savgol_filter
from tkinter import *
from tkinter import filedialog as fd
import csv
from datetime import datetime, date
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import curren_settings_class as cs
import matplotlib.pyplot as plt


class BViewer:
    EXP_DAY = '2022-05-15'

    header_item = ''
    export_path = ''
    x_change_status = False

    temperature_list = ['temperature', 'температура', 'temp']
    speed_list = ['speed', 'скорость']
    orientation_list = ['orientation', 'угловое положение', 'угол', 'angle']
    pressure_list = ['pressure (product)', 'pressure', 'давление']
    magnetization_list = ['magnetic induction (sensors)', 'magnetic induction (wt gauge)',
                          'magnetic intensity (sensors)',
                          'magnetic intensity (wt gauge)', 'magnetization', 'намагниченность', 'magn']
    names_repeats_list = ["speed", "orientation", "temperature", "magnetization"]

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
        self.filter_slider = tkinter.Scale(self.window, from_=0, to=200, orient='horizontal', width=20, length=200,
                                           command=self.filter_slider_change)
        self.filter_value_combobox = OptionMenu(self.window, self.filter_variable, *self.filter_options,
                                                command=self.set_filter)
        self.filter_value_label = Label(master=self.window, text="Smoothing Value")
        self.yaxis_name_textbox = Entry(master=self.window, width=35)
        self.xaxis_name_textbox = Entry(master=self.window, width=35)
        self.yaxis_name_label = Label(master=self.window, text="Y Axis Name")
        self.xaxis_name_label = Label(master=self.window, text="X Axis Name")
        self.x_mult_textbox = Entry(master=self.window, width=10)
        self.x_mult_label = Label(master=self.window, text="X Mult")
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

        self.CS = 0
        self.x_change_status = False
        self.x_change_status = True
        self.file_path = ""
        self.accept_graphs = ['speed', 'orientation', 'temperature', 'скорость', 'температура', 'угловое положение',
                              'magnetic intensity (sensors)']
        self.header_row = ""
        self.axis_table = ""
        self.filepath = ""

        self.slider_value = 0
        self.x_axis = []
        self.y_axis = []
        self.x_axis_name = ''
        self.y_axis_name = ''
        self.x_axis_mult = ''
        self.y_axis_filter = ''
        self.savgol_value = 0

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
                if "Distance" in headers:
                    header_row = np.array(headers)
                    header_row_index = 1
                    return header_row, header_row_index

        elif extension == "xlsx":
            pandas_df_excel = pd.read_excel(filename)
            header_row = np.array(pandas_df_excel.columns.values)

            if "Distance" in header_row:
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

        CS = cs.CurrentSettings(header_row, os.path.basename(filename))

        print(header_row)

        self.graphs_listbox.delete(0, END)
        for graph_name in header_row:
            self.graphs_listbox.insert(END, graph_name)

        return axis_array, header_row

    @staticmethod
    def list_item_in_string(base_list, search_in_string):
        """
        Возвращает True если один из элементов List в Строке
        """

        for item in base_list:
            if item in search_in_string:
                return True
        return False

    def graph_settings_parse(self, graph_name, y_max):
        """
        По названию графика создаем Словарь с характеристиками графика
        Возращаем пустой если графику не нужны настройки, возьмутся автоматические
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

        graph_name = graph_name.lower()

        if self.list_item_in_string(self.speed_list, graph_name):
            if y_max < 5:
                ymax = 5
            else:
                ymax = self.round_up_custom(y_max, 5)

            graph_settings = {'ymax': ymax,
                              "ymax_format": '%.1f',
                              "ymax_base": 0.5,
                              "ylabel": "Скорость, м/с",
                              "color": "darkslateblue"}

            return graph_settings
        elif self.list_item_in_string(self.temperature_list, graph_name):
            graph_settings = {'ymax': 100,
                              "ymax_format": '%.0f',
                              "ymax_base": 10,
                              "ylabel": "Температура, °С",
                              "color": "firebrick"}
            return graph_settings
        elif self.list_item_in_string(self.orientation_list, graph_name):
            graph_settings = {'ymax': 360,
                              "ymax_format": '%.0f',
                              "ymax_base": 30,
                              "ylabel": "Угловое положение, °",
                              "color": "darkolivegreen"}
            return graph_settings
        elif self.list_item_in_string(self.magnetization_list, graph_name):
            graph_settings = {'ymax': 40,
                              "ymax_format": '%.1f',
                              "ymax_base": 5,
                              "ylabel": "Намагниченность, кА/м",
                              "color": "maroon"}
            return graph_settings
        elif self.list_item_in_string(self.pressure_list, graph_name):
            graph_settings = {'ymax': 10,
                              "ymax_format": '%.1f',
                              "ymax_base": 1,
                              "ylabel": "Давление, МПа",
                              "color": "peru"}
            return graph_settings
        else:
            return {}

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

        # Линия для графика скорости
        # if list_item_in_string(speed_list, graph_name.lower()):
        #     x1, y1 = [0, round_up_custom(max(x_axis), 100)], [4, 4]
        #     ax.plot(x1, y1, color=colors['darkred'], linewidth=2)

        if self.list_item_in_string(self.magnetization_list, graph_name.lower()):
            x1, y1 = [0, self.round_up_custom(max(x_axis), 100)], [10, 10]
            self.ax.plot(x1, y1, color=colors['red'], linewidth=2)
            x2, y2 = [0, self.round_up_custom(max(x_axis), 100)], [30, 30]
            self.ax.plot(x2, y2, color=colors['blue'], linewidth=2)

        graph_settings = self.graph_settings_parse(graph_name, max(y_axis))
        self.ax.grid()
        plt.xlim(0)
        plt.ylim(0)
        plt.xlabel('Дистанция от камеры запуска, м', labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
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

        if self.x_change_status is False:
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
            self.ax.set_ylim(ymin=0, ymax=graph_settings['ymax'])
            # Локатор с фиксированным шагом
            self.ax.yaxis.set_major_locator(MultipleLocator(base=graph_settings['ymax_base']))
            # Формат оси
            self.ax.yaxis.set_major_formatter(FormatStrFormatter(graph_settings['ymax_format']))
            # Лэйбл оси
            plt.ylabel(graph_settings['ylabel'], labelpad=10, font={'family': 'sans', 'weight': 'bold', 'size': 18})
            # Меняем цвет графика
            plt.gca().get_lines()[0].set_color(graph_settings['color'])
        else:
            if self.x_change_status is False:
                self.ax.yaxis.set_major_locator(MaxNLocator())

        plt.subplots_adjust(left=.09, bottom=.1, right=0.97, top=0.98, wspace=0, hspace=0)

        self.canvas.draw()

    def plot_event(self, event):
        try:
            if self.graphs_listbox.curselection().__len__() != 0 or self.y_axis_name is not None:
                self.filter_slider.set(0)
                self.plot()
                self.get_minmax()
                self.status_label1.config(text=self.y_axis_name)

        except Exception as ex:
            print('plot_event' + str(ex))

    def plot(self):

        try:
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

            self.y_axis = self.y_axis * float(self.y_mult_textbox.get()) + float(self.add_textbox.get())

            # savgol_value = filter_variable.get()
            #
            # filter_options_list = {"no filter": 3,
            #                        "SAVG light": 33,
            #                        "SAVG medium": 333,
            #                        "SAVG heavy": 667}

            self.savgol_value = self.get_filter_slieder()
            self.y_axis_filter = savgol_filter(self.y_axis, window_length=self.savgol_value, polyorder=2)
            self.x_axis_mult = self.x_axis * float(self.x_mult_textbox.get())

            # if savgol_value in filter_options_list:
            #     savgol_value = filter_options_list[savgol_value]
            #     y_axis = savgol_filter(y_axis, window_length=savgol_value, polyorder=2)

            x_axis_min_value = round(np.min(self.x_axis), 1)
            x_axis_max_value = round(np.max(self.x_axis), 1)
            y_axis_min_value = round(np.min(self.y_axis), 1)
            y_axis_max_value = round(np.max(self.y_axis), 1)
            y_axis_average_value = round(np.average(self.y_axis), 2)

            self.status_label2.config(text=f"Average={y_axis_average_value}\n\n"
                                           f"XMIN={x_axis_min_value} : "
                                           f"XMAX={x_axis_max_value}\n"
                                           f"YMIN={y_axis_min_value} : "
                                           f"YMAX={y_axis_max_value}", anchor='w')

            self.make_graph(self.x_axis_mult, self.y_axis_filter, self.y_axis_name)

        except Exception as ex:
            print('plot: ' + str(ex))

    def set_xminmax_no_event(self):
        self.x_change_status = True
        if self.xmin_textbox.get() != "" and self.xmax_textbox.get() != 0:
            xmin = float(self.xmin_textbox.get())
            xmax = float(self.xmax_textbox.get())
            self.ax.set_xlim(xmin=xmin, xmax=xmax)

    def set_xminmax(self, event=None):
        self.x_change_status = True
        if self.xmin_textbox.get() != "" and self.xmax_textbox.get() != 0:
            xmin = float(self.xmin_textbox.get())
            xmax = float(self.xmax_textbox.get())
            self.ax.set_xlim(xmin=xmin, xmax=xmax)

        self.canvas.draw()

    def set_xmajor_no_event(self):
        if self.xmajor_textbox.get() != "":
            xmajor_value = float(self.xmajor_textbox.get())
            self.ax.xaxis.set_major_locator(MultipleLocator(base=xmajor_value))
            self.x_change_status = True

    def set_xmajor(self, event=None):
        if self.xmajor_textbox.get() != "":
            xmajor_value = float(self.xmajor_textbox.get())
            self.ax.xaxis.set_major_locator(MultipleLocator(base=xmajor_value))
            self.x_change_status = True
            self.canvas.draw()

    def set_yminmax(self, event=None):
        if self.ymin_textbox.get() != "" and self.ymax_textbox.get() != 0:
            ymin = float(self.ymin_textbox.get())
            ymax = float(self.ymax_textbox.get())
            self.ax.set_ylim(ymin=ymin, ymax=ymax)

        self.canvas.draw()

    def set_xlabel_name(self, event=None):
        xlabel_name = self.xaxis_name_textbox.get()
        plt.xlabel(xlabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
        self.canvas.draw()

    def set_ylabel_name(self, event=None):
        ylabel_name = self.yaxis_name_textbox.get()
        plt.ylabel(ylabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
        self.canvas.draw()

    def set_filter(self, event):
        if self.graphs_listbox.curselection().__len__() != 0 or self.y_axis_name is not None:
            self.plot()
            self.get_minmax()

    def filter_slider_change(self, event):
        self.plot()
        self.get_minmax()

    def get_filter_slieder(self):
        slider_value = self.filter_slider.get() + 3

        if slider_value % 2 == 0:
            slider_value = slider_value + 1
            self.filter_slider.set(slider_value - 3)

        return slider_value

    def set_ymajor(self, event):
        ymajor_value = float(self.ymajor_textbox.get())
        self.ax.yaxis.set_major_locator(MultipleLocator(base=ymajor_value))
        self.canvas.draw()

    def get_minmax(self):
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

        xticks_list = plt.gca().xaxis.major.formatter.locs
        xticks = xticks_list[1] - xticks_list[0]
        self.xmajor_textbox.delete(0, END)
        self.xmajor_textbox.insert(0, xticks)

    def select_file(self):
        filetypes = (
            ('Iligraph files', '*.ig~'),
            ('Excel files', '*.csv *.xlsx')
        )

        self.x_change_status = False
        self.get_minmax()

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=os.path.abspath(__file__),
            filetypes=filetypes)

        if filename != "":
            self.status_label1.config(text="Choose profile...")
            # filepath = pathlib.Path(filename).parent.resolve()
            self.axis_table, self.header_row = self.get_axis_from_file(filename)

    def open_with_file(self, file_path):

        self.status_label1.config(text="Choose profile...")
        # filepath = pathlib.Path(filename_path).parent.resolve()
        self.axis_table, self.header_row = self.get_axis_from_file(file_path)

    def auto_chart(self):
        self.x_change_status = False
        self.add_textbox.delete(0, END)
        self.add_textbox.insert(0, 0)
        self.y_mult_textbox.delete(0, END)
        self.y_mult_textbox.insert(0, 1)
        self.x_mult_textbox.delete(0, END)
        self.x_mult_textbox.insert(0, 1)
        self.plot()
        self.get_minmax()

    def export_selected(self):

        try:
            np.savetxt(f"{self.file_path}/{self.y_axis_name}.csv", np.transpose([self.x_axis_mult, self.y_axis_filter]),
                       delimiter=',',
                       header=f"Distance, {self.y_axis_name}")
        except Exception as ex:
            print("Nothing to export: " + str(ex))

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception as ex:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

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
            self.add_textbox.bind('<Return>', self.plot_event)
            self.y_mult_textbox.insert(0, "1")
            self.y_mult_textbox.bind('<Return>', self.plot_event)
            self.x_mult_textbox.insert(0, "1")
            self.x_mult_textbox.bind('<Return>', self.plot_event)
            self.xaxis_name_textbox.bind('<Return>', self.set_xlabel_name)
            self.yaxis_name_textbox.bind('<Return>', self.set_ylabel_name)
            self.filter_variable.set(self.filter_options[0])
            self.status_label2.place(x=10, y=700)
            self.filter_value_label.place(x=10, y=380)
            self.filter_slider.place(x=10, y=400)
            self.status_label1.place(x=10, y=5)
            self.status_label1.config(text="Select file...")
            self.open_button.place(x=10, y=35, width=70, height=25)
            self.export_button.place(x=100, y=35, width=90, height=25)
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
            self.autochart_button.place(x=10, y=670, width=70, height=25)
            self.add_label.place(x=10, y=620)
            self.add_textbox.place(x=10, y=641)
            self.y_mult_label.place(x=80, y=620)
            self.y_mult_textbox.place(x=80, y=641)
            self.x_mult_label.place(x=150, y=620)
            self.x_mult_textbox.place(x=150, y=641)

            try:
                open_with_path = str(sys.argv[1])
                print("sys path - " + open_with_path)
                self.open_with_file(open_with_path)
            except Exception as ex:
                print("sys path error: " + str(ex))
                x = np.linspace(0, 300, 150)
                y = np.sin(2 * np.pi * (x - 0.01 * 1)) + 1
                self.make_graph(x, y, "Sin (x)")

            def on_closing():
                self.window.destroy()
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


def main():
    b_viewer = BViewer()
    b_viewer.form_init()

if __name__ == "__main__":
    main()
