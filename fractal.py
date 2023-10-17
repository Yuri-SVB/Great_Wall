import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to monitor
directory = "./"

# Função para formatar a coordenada de zoom
def format_zoom_coordinate(zoom_coordinate, zoom):
    zoom_coordinate = zoom_coordinate.split('E')
    exponent = "00"
    if zoom == "in":
        exponent = "-05"
    if zoom == "out":
        exponent = "+03"
    #integer = zoom_coordinate[0].split('.')[0]
    return f"1E{exponent}", f"1E{exponent}"

# Função para gerar as coordenadas do fractal
def generate_fractal(*coordinates):
    center_x, center_y, real_axis, imaginary_axis = coordinates
    
    center_x = center_x.split('E')
    integer_x = center_x[0].split('.')[0].replace('-','')
    decimal_x = center_x[0].split('.')[1][:5]
    real_axis = real_axis.split('E')
    real_axis_integer = real_axis[0].split('.')[0]
    real_axis_exponent = real_axis[1]
    
    new_real_axis = f"{real_axis_integer}.{integer_x}{decimal_x}E{real_axis_exponent}"

    center_y = center_y.split('E')
    integer_y = center_y[0].split('.')[0].replace('-','') 
    decimal_y = center_y[0].split('.')[1][:5]
    imaginary_axis = imaginary_axis.split('E')
    imaginary_axis_integer = imaginary_axis[0].split('.')[0]
    imaginary_axis_exponent = imaginary_axis[1]

    new_imaginary_axis = f"{imaginary_axis_integer}.{integer_y}{decimal_y}E{imaginary_axis_exponent}"
    return new_real_axis, new_imaginary_axis
    
# Função para formatar as coordenadas
def format_center_coordinates(*coordinates, truncation=5):
    x, y = coordinates
    x_parts = x.split('E')
    if len(x_parts) > 1:
        number, exponent = x_parts[0], x_parts[1]
        number = number.split('.')
        decimal = number[1]
        decimal = decimal[:truncation] + '0' * (len(decimal) - truncation)
        integer = number[0]
        x = f"{integer}.{decimal}E{exponent}"

    y_parts = y.split('E')
    if len(y_parts) > 1:
        number, exponent = y_parts[0], y_parts[1]
        number = number.split('.')
        decimal = number[1]
        decimal = decimal[:truncation] + '0' * (len(decimal) - truncation)
        integer = number[0]
        y = f"{integer}.{decimal}E{exponent}"

    return x, y

def prepare_next_fractal(file):
    config_file_path = os.path.join(directory, file)
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            lines = config_file.readlines()
        center_zoom_line = lines[3].split()
        center_x = center_zoom_line[0]
        center_y = center_zoom_line[1]
        zoom = center_zoom_line[2]
        center_zoom_line[2], center_zoom_line[3] = format_zoom_coordinate(zoom, "in")
        center_zoom_line[0], center_zoom_line[1] = format_center_coordinates(center_x, center_y)
        center_zoom_line = ' '.join(center_zoom_line) + "\n"
        lines[3] = center_zoom_line

        with open(config_file_path, "w") as config_file:
            config_file.writelines(lines)

def perform_generation_fractal(file):
    config_file_path = os.path.join(directory, file)
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            lines = config_file.readlines()

        fractal_coordinates = lines[2].split()
        center_zoom_line = lines[3].split()

        real_axis = fractal_coordinates[0]
        imaginary_axis = fractal_coordinates[1]

        center_x = center_zoom_line[0]
        center_y = center_zoom_line[1]
        zoom = center_zoom_line[2]

        fractal_coordinates[0], fractal_coordinates[1] = generate_fractal(center_x, center_y, real_axis, imaginary_axis)
        center_zoom_line[2], center_zoom_line[3] = format_zoom_coordinate(zoom, "out")
        center_zoom_line[0], center_zoom_line[1] = format_center_coordinates(center_x, center_y)
        center_zoom_line = ' '.join(center_zoom_line) + "\n"
        fractal_coordinates = " ".join(fractal_coordinates) + "\n"
        lines[3] = center_zoom_line
        lines[2] = fractal_coordinates
        with open(config_file_path, "w") as config_file:
            config_file.writelines(lines)

config_file_to_monitor = None
config_file_modification_time = 0  

# Event handler class for Watchdog
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global config_file_modification_time
        if event.src_path == config_file_to_monitor:
            current_modification_time = os.path.getmtime(event.src_path)
            if current_modification_time != config_file_modification_time:
                config_file_modification_time = current_modification_time
                prepare_next_fractal(config_file_to_monitor)
                perform_generation_fractal(config_file_to_monitor)
                time.sleep(1)

observer = Observer()
event_handler = MyHandler()
observer.schedule(event_handler, path=directory, recursive=False)
observer.start()

try:
    config_file_name = input("Enter the name of the .config file (e.g., 'arquivo.config'): ").strip()
    existing_file_path = os.path.join(directory, config_file_name)
    if config_file_name.endswith(".config") and os.path.exists(existing_file_path):
        config_file_to_monitor = existing_file_path
        config_file_modification_time = os.path.getmtime(config_file_to_monitor)
        prepare_next_fractal(config_file_to_monitor)
        perform_generation_fractal(config_file_to_monitor)

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()