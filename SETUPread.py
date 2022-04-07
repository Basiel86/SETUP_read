import math
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator, MaxNLocator
import matplotlib.colors as mcolors
import matplotlib.transforms
from scipy.signal import savgol_filter
from tkinter import *
from tkinter import filedialog as fd
from os import walk
import pathlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

header_item = ''
export_path = ''

temperature_list = ['temperature', 'температура']
speed_list = ['speed', 'скорость']
orientation_list = ['orientation', 'угловое положение']
pressure_list = ['pressure (product)']
magnetization_list = ['magnetic induction (sensors)', 'magnetic induction (wt gauge)', 'magnetic intensity (sensors)',
                      'magnetic intensity (wt gauge)']
names_repeats_list = ["speed", "orientation", "temperature", "magnetization"]


# Ищем вхождение в Distance
def setup_parse_row(filename):
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
    raise ValueError("Дистанции в файле не обнаружено")


def get_axis_from_file(filename):
    header_row, header_row_index = setup_parse_row(filename)
    start_column = 0
    if header_row[0] == "":
        start_column = 1
    axis_array = np.loadtxt(filename, usecols=range(start_column, len(header_row)), skiprows=header_row_index + 9)
    if header_row[0] == '':
        header_row = np.delete(header_row, 0)
    return axis_array, header_row


def list_item_in_string(base_list, search_in_string):
    """
    Возвращает True если один из элементов List в Строке
    """
    for item in base_list:
        if item in search_in_string:
            return True
    return False


def graph_settings_parse(graph_name, y_max):
    """
    По названию графика создаем Словарь с характеристиками графика
    Возращаем пустой если графику не нужны настройки, возьмутся автоматические
    """
    # darkcyan
    # darkgoldenrod
    # maroon
    # darkslateblue
    # darkolivegreen
    # olive
    # cadetblue
    # peru

    graph_name = graph_name.lower()

    if list_item_in_string(speed_list, graph_name):
        if y_max < 5:
            ymax = 5
        else:
            ymax = round_up_custom(y_max, 5)

        graph_settings = {'ymax': ymax,
                          "ymax_format": '%.1f',
                          "ymax_base": 0.5,
                          "ylabel": "Скорость, м/с",
                          "color": "darkslateblue"}

        return graph_settings
    elif list_item_in_string(temperature_list, graph_name):
        graph_settings = {'ymax': 100,
                          "ymax_format": '%.0f',
                          "ymax_base": 10,
                          "ylabel": "Температура, °С",
                          "color": "firebrick"}
        return graph_settings
    elif list_item_in_string(orientation_list, graph_name):
        graph_settings = {'ymax': 360,
                          "ymax_format": '%.0f',
                          "ymax_base": 30,
                          "ylabel": "Угловое положение, °",
                          "color": "darkolivegreen"}
        return graph_settings
    elif list_item_in_string(magnetization_list, graph_name):
        graph_settings = {'ymax': 60,
                          "ymax_format": '%.1f',
                          "ymax_base": 10,
                          "ylabel": "Намагниченность, кА/м",
                          "color": "maroon"}
        return graph_settings
    elif list_item_in_string(pressure_list, graph_name):
        graph_settings = {'ymax': 50,
                          "ymax_format": '%.1f',
                          "ymax_base": 1,
                          "ylabel": "Давление, МПа",
                          "color": "peru"}
        return graph_settings
    else:
        return {}


def round_up_custom(num, step):
    """
    Округление вверх с шагом
    """
    return math.ceil(num / step) * step


def make_graph(x_axis, y_axis, graph_name):
    """
    Рисуем сам график
    """

    global ax
    global fig
    global canvas
    # https://matplotlib.org/stable/gallery/color/named_colors.html
    colors = mcolors.CSS4_COLORS

    if plt.get_fignums().__len__() == 0:
        fig = plt.figure(figsize=(16, 8))
        font = {'family': 'sans',
                'weight': 'normal',
                'size': 16}

        canvas = FigureCanvasTkAgg(fig,
                                   master=window)
        canvas.draw()
        canvas.get_tk_widget().place(x=250, y=10)

        plt.rc('font', **font)

        ax = fig.add_subplot(111)
    else:
        plt.cla()
        # canvas.draw()

    # color = (0.5, 0, 0.5)

    ax.plot(x_axis, y_axis, color=colors['darkgreen'], linewidth=1)

    # Линия для графика скорости

    if list_item_in_string(speed_list, graph_name.lower()):
        x1, y1 = [0, round_up_custom(max(x_axis), 100)], [4, 4]
        ax.plot(x1, y1, color=colors['darkred'], linewidth=2)

    graph_settings = graph_settings_parse(graph_name, max(y_axis))
    ax.grid()
    plt.xlim(0)
    plt.ylim(0)
    plt.xlabel('Дистанция от камеры запуска, м', labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
    plt.ylabel('Ось Y, ...', labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})

    # plt.title(graph_name, pad=30)
    # plt.title(graph_settings['color'], pad=15)

    # MultipleLocator(base=500) - Локатор с шагом в 500
    # MaxNLocator() - Автоматиечский локатор

    # Create offset transform by 5 points in x direction
    dy1 = -5 / 72.
    dx2 = -5 / 72
    offsetX = matplotlib.transforms.ScaledTranslation(0, dy1, fig.dpi_scale_trans)
    offsetY = matplotlib.transforms.ScaledTranslation(dx2, 0, fig.dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offsetX)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offsetY)

    ax.xaxis.set_major_locator(MaxNLocator())
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.set_xlim(xmin=0, xmax=round_up_custom(max(x_axis), 100))
    # ax.set_xlim(xmin=0,xmax=100)

    # Возвращаем настройки под график по имени Серии

    if graph_settings != {}:
        # Максимальное значение графика
        ax.set_ylim(ymin=0, ymax=graph_settings['ymax'])
        # Локатор с фиксированным шагом
        ax.yaxis.set_major_locator(MultipleLocator(base=graph_settings['ymax_base']))
        # Формат оси
        ax.yaxis.set_major_formatter(FormatStrFormatter(graph_settings['ymax_format']))
        # Лэйбл оси
        plt.ylabel(graph_settings['ylabel'], labelpad=10, font={'family': 'sans', 'weight': 'bold', 'size': 18})
        # Меняем цвет графика
        plt.gca().get_lines()[0].set_color(graph_settings['color'])
    else:
        ax.yaxis.set_major_locator(MaxNLocator())

    plt.subplots_adjust(left=.09, bottom=.1, right=0.97, top=0.98, wspace=0, hspace=0)

    # дериктория сохранения файлов
    # save_dir = os.path.dirname(__file__) + "/IG_TMP/GraphsTest"
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)

    # чистим папку с графиками
    """
    for filename in os.listdir(save_dir):
        file_path = os.path.join(save_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    """

    # Переименовываем нужные графики однообразно и избавляемся от дублирования
    # if list_item_in_string(speed_list, graph_name.lower()):
    #     graph_name = "Speed"
    # if list_item_in_string(temperature_list, graph_name.lower()):
    #     graph_name = "Temperature"
    # if list_item_in_string(orientation_list, graph_name.lower()):
    #     graph_name = "Orientation"
    # if list_item_in_string(magnetization_list, graph_name.lower()):
    #     graph_name = "Magnetization"

    # graph_filename = graph_name + ".jpg"

    # for g_name in names_repeats_list:
    #     if g_name in graph_name.lower():
    #         indx = 1
    #         graph_filename = g_name.capitalize() + ".jpg"
    #         while os.path.exists(save_dir + "/" + graph_filename):
    #             graph_filename = g_name.capitalize() + "_" + str(indx) + ".jpg"
    #             indx += 1

    # print("going to save to:" + export_path + "/" + graph_filename)

    # plt.savefig(export_path + "/" + graph_filename, dpi=300)
    # plt.show()
    # plt.close()
    canvas.draw()


def SETUPgraphs(file_path, export_path):
    global axis_table
    global header_row
    axis_table, header_row = get_axis_from_file(file_path)

    print(header_row)

    graphs_listbox.delete(0, END)
    for graph_name in header_row:
        graphs_listbox.insert(END, graph_name)

    accept_graphs = ['speed', 'orientation', 'temperature', 'скорость', 'температура', 'угловое положение',
                     'magnetic intensity (sensors)']

    # for accept_item in accept_graphs:
    #     for header_item in header_row:
    #         if accept_item.lower() in header_item.lower():
    #             print(header_item.lower())
    #
    #             x_axis_name = "Distance"
    #             y_axis_name = header_item
    #
    #             if x_axis_name not in header_row:
    #                 raise ResourceWarning("Дистанция не найдена")
    #
    #             x_index = np.argwhere(header_row == x_axis_name)[0][0]
    #             y_index = np.argwhere(header_row == y_axis_name)[0][0]
    #
    #             x_axis = axis_table[:, x_index]
    #
    #             y_axis = axis_table[:, y_index]
    #
    #             y_axis = savgol_filter(y_axis, window_length=900, polyorder=2)
    #
    #             make_graph(x_axis, y_axis, header_item, export_path)


def plot_event(event):
    global y_axis_name
    if graphs_listbox.curselection().__len__() != 0 or y_axis_name is not None:
        plot()
        get_minmax()


def plot():
    global y_axis_name
    global axis_table
    global header_row
    global x_axis
    global y_axis

    x_axis_name = "Distance"

    if graphs_listbox.curselection().__len__() != 0 or y_axis_name is not None:
        for i in graphs_listbox.curselection():
            y_axis_name = graphs_listbox.get(i)

    if x_axis_name not in header_row:
        raise ResourceWarning("Дистанция не найдена")

    x_index = np.argwhere(header_row == x_axis_name)[0][0]
    y_index = np.argwhere(header_row == y_axis_name)[0][0]

    x_axis = axis_table[:, x_index]
    y_axis = axis_table[:, y_index]

    y_axis = y_axis * float(mult_textbox.get()) + float(add_textbox.get())

    sovgol_value = filter_variable.get()

    filter_options_list = {"no filter": 3,
                           "SOVG light": 33,
                           "SOVG memium": 333,
                           "SOVG heavy": 3333}

    if sovgol_value in filter_options_list:
        sovgol_value = filter_options_list[sovgol_value]
        y_axis = savgol_filter(y_axis, window_length=sovgol_value, polyorder=2)

    make_graph(x_axis, y_axis, y_axis_name)


def set_minmax(event):
    if xmin_textbox.get() != "" and xmax_textbox.get() != 0:
        xmin = float(xmin_textbox.get())
        xmax = float(xmax_textbox.get())
        ax.set_xlim(xmin=xmin, xmax=xmax)

    if ymin_textbox.get() != "" and ymax_textbox.get() != 0:
        ymin = float(ymin_textbox.get())
        ymax = float(ymax_textbox.get())
        ax.set_ylim(ymin=ymin, ymax=ymax)

    canvas.draw()


def set_xlabel_name(event):
    xlabel_name = xaxis_name_textbox.get()
    plt.xlabel(xlabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
    canvas.draw()


def set_ylabel_name(event):
    ylabel_name = yaxis_name_textbox.get()
    plt.ylabel(ylabel_name, labelpad=8, font={'family': 'sans', 'weight': 'bold', 'size': 18})
    canvas.draw()

    #print


def set_filter(event):
    if graphs_listbox.curselection().__len__() != 0 or y_axis_name is not None:
        plot()
        get_minmax()


def set_xmajor(event):
    xmajor_value = float(xmajor_textbox.get())
    ax.xaxis.set_major_locator(MultipleLocator(base=xmajor_value))
    canvas.draw()


def set_ymajor(event):
    ymajor_value = float(ymajor_textbox.get())
    ax.yaxis.set_major_locator(MultipleLocator(base=ymajor_value))
    canvas.draw()


def get_minmax():
    xmin, xmax = plt.gca().get_xlim()
    xmin_textbox.delete(0, END)
    xmax_textbox.delete(0, END)
    xmin_textbox.insert(0, round(xmin, 1))
    xmax_textbox.insert(0, round(xmax, 1))

    ymin, ymax = plt.gca().get_ylim()
    ymin_textbox.delete(0, END)
    ymax_textbox.delete(0, END)
    ymin_textbox.insert(0, round(ymin, 1))
    ymax_textbox.insert(0, round(ymax, 1))

    xlabel_name = plt.gca().get_xlabel()
    xaxis_name_textbox.delete(0, END)
    xaxis_name_textbox.insert(0, xlabel_name)

    ylabel_name = plt.gca().get_ylabel()
    yaxis_name_textbox.delete(0, END)
    yaxis_name_textbox.insert(0, ylabel_name)


def select_file():
    filetypes = (
        ('text files', '*.ig~'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=r'c:\Users\Vasily\OneDrive\Macro\PYTHON\SETUPread',
        filetypes=filetypes)

    filepath = pathlib.Path(filename).parent.resolve()
    SETUPgraphs(filename, filepath)


if __name__ == "__main__":
    # the main Tkinter window

    window = Tk()
    window.title('BaZViewer 0.5')
    window.geometry("1900x830")
    plot_button = Button(master=window,
                         command=plot,
                         height=2,
                         width=10,
                         text="Plot")

    # sv.trace("w", lambda name, index, mode, sv=sv: callback(sv))

    open_button = Button(master=window, text='Open a File', command=select_file)
    get_minmax_button = Button(master=window, text='Get Min/Max', command=get_minmax, width=10, height=1)
    set_minmax_button = Button(master=window, text='Set Min/Max', command=set_minmax, width=10, height=1)

    graphs_listbox = Listbox(width=30, height=20)
    graphs_listbox.bind('<<ListboxSelect>>', plot_event)

    xmin_label = Label(master=window, text="X-Min")
    xmax_label = Label(master=window, text="X-Max")
    ymin_label = Label(master=window, text="Y-Min")
    ymax_label = Label(master=window, text="Y-Max")
    xmajor_label = Label(master=window, text="X-Major")
    ymajor_label = Label(master=window, text="Y-Major")

    xmin_textbox = Entry(master=window, width=10)
    xmax_textbox = Entry(master=window, width=10)
    ymin_textbox = Entry(master=window, width=10)
    ymax_textbox = Entry(master=window, width=10)
    xmajor_textbox = Entry(master=window, width=10)
    ymajor_textbox = Entry(master=window, width=10)

    xmin_textbox.bind('<Return>', set_minmax)
    xmax_textbox.bind('<Return>', set_minmax)
    ymin_textbox.bind('<Return>', set_minmax)
    ymax_textbox.bind('<Return>', set_minmax)
    xmajor_textbox.bind('<Return>', set_xmajor)
    ymajor_textbox.bind('<Return>', set_ymajor)

    add_label = Label(master=window, text="Add")
    add_textbox = Entry(master=window, width=10)
    add_textbox.insert(0, "0")
    add_textbox.bind('<Return>', plot_event)

    mult_label = Label(master=window, text="Mult")
    mult_textbox = Entry(master=window, width=10)
    mult_textbox.insert(0, "1")
    mult_textbox.bind('<Return>', plot_event)

    xaxis_name_label = Label(master=window, text="X Axis Name")
    yaxis_name_label = Label(master=window, text="Y Axis Name")

    xaxis_name_textbox = Entry(master=window, width=35)
    yaxis_name_textbox = Entry(master=window, width=35)

    xaxis_name_textbox.bind('<Return>', set_xlabel_name)
    yaxis_name_textbox.bind('<Return>', set_ylabel_name)

    filter_value_label = Label(master=window, text="Filter Value")

    filter_value_var = StringVar()

    filter_options = ["no filter",
                      "SOVG light",
                      "SOVG memium",
                      "SOVG heavy"]
    filter_variable = StringVar(window)
    filter_value_combobox = OptionMenu(window, filter_variable, *filter_options, command=set_filter)
    filter_variable.set(filter_options[0])
    filter_value_combobox.place(x=10, y=420)
    filter_value_label.place(x=10, y=400)

    plot_button.place(x=10, y=10, width=70, height=25)
    open_button.place(x=10, y=35, width=70, height=25)
    graphs_listbox.place(x=10, y=70)

    xmin_label.place(x=10, y=450)
    xmax_label.place(x=80, y=450)
    xmajor_label.place(x=150, y=450)
    xmin_textbox.place(x=10, y=470)
    xmax_textbox.place(x=80, y=470)
    xmajor_textbox.place(x=150, y=470)

    ymin_label.place(x=10, y=490)
    ymax_label.place(x=80, y=490)
    ymajor_label.place(x=150, y=490)
    ymin_textbox.place(x=10, y=515)
    ymax_textbox.place(x=80, y=515)
    ymajor_textbox.place(x=150, y=515)

    xaxis_name_label.place(x=10, y=540)
    xaxis_name_textbox.place(x=10, y=560)

    yaxis_name_label.place(x=10, y=580)
    yaxis_name_textbox.place(x=10, y=600)

    get_minmax_button.place(x=10, y=700)
    set_minmax_button.place(x=110, y=700)

    add_label.place(x=10, y=620)
    add_textbox.place(x=10, y=640)

    mult_label.place(x=100, y=620)
    mult_textbox.place(x=100, y=640)

    x = np.linspace(0, 300, 150)
    y = np.sin(2 * np.pi * (x - 0.01 * 1)) + 1
    make_graph(x, y, "Welcome!")

    window.mainloop()

    # filename = os.path.dirname(__file__) + '/IG_TMP/1ngcm_StatisticsForReport.ig~'
    # #filename = os.path.dirname(__file__) + '/IG_TMP/TestPlots.ig~'
    # #filename = os.path.dirname(__file__) + '/IG_TMP/NoBlankFirst.ig~'
    # make_all = False
    # export_path = save_dir = os.path.dirname(__file__) + "/IG_TMP/GraphsTest"
    #
    # axis_table, header_row = get_axis_from_file(filename)
    # print(header_row)
    #
    # if not make_all:
    #
    #     x_axis_name = "Distance"
    #     y_axis_name = "Speed"
    #
    #     if x_axis_name.lower not in header_row:
    #         raise ResourceWarning("Дистанция не найдена")
    #
    #     x_index = np.argwhere(header_row == x_axis_name)[0][0]
    #     y_index = np.argwhere(header_row == y_axis_name)[0][0]
    #
    #     x_axis = axis_table[:, x_index]
    #     y_axis = axis_table[:, y_index]
    #
    #     make_graph(x_axis, y_axis, y_axis_name, export_path)
    # else:
    #
    #     accept_graphs = ['speed', 'orientation', 'temperature', 'скорость', 'температура', 'угловое положение',
    #                      'magnetic intensity (sensors)']
    #
    #     for accept_item in accept_graphs:
    #         for header_item in header_row:
    #             if accept_item.lower() in header_item.lower():
    #                 print(header_item.lower())
    #
    #                 x_axis_name = "Distance"
    #                 y_axis_name = header_item
    #
    #
    #
    #                 if x_axis_name not in header_row:
    #                     raise ResourceWarning("Дистанция не найдена")
    #
    #                 x_index = np.argwhere(header_row == x_axis_name)[0][0]
    #                 y_index = np.argwhere(header_row == y_axis_name)[0][0]
    #
    #                 x_axis = axis_table[:, x_index]
    #                 y_axis = axis_table[:, y_index]
    #                 # https://stackoverflow.com/questions/37598986/reducing-noise-on-data
    #                 #y_axis = savgol_filter(y_axis, window_length=101, polyorder=2)
    #
    #
    #
    #                 make_graph(x_axis, y_axis, header_item, export_path)
