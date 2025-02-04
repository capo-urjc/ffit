import dearpygui.dearpygui as dpg
from serial_port import SerialPort, com_ports
from injection import launch_injection


injection_full_path = ""
sem_port = SerialPort()
design_port = SerialPort()


def select_file(sender, app_data):
    with dpg.file_dialog(directory_selector=False, show=True, height=600, callback=file_selected):
        dpg.add_file_extension(".txt", color=(0, 255, 0, 255))


def file_selected(sender, value, user_data):
    global injection_full_path
    injection_full_path = value["file_path_name"]
    dpg.set_value("addr_filename_text", value["file_name"])


def set_port_name_callback(sender, value, user_data):
    if value != "None":
        user_data.set_serial_name(value)
        user_data.set_baudrate(int(dpg.get_value("baud_desp_inj")))


def set_baudrate_callback(sender, value, user_data):
    if dpg.get_value("sem_port_cb") != "" and dpg.get_value("design_port_cb") != "":
        sem_port.set_baudrate(int(dpg.get_value("baud_desp_inj")))
        design_port.set_baudrate(int(dpg.get_value("baud_desp_inj")))


def update_ports_callback(sender, value, user_data):
    ports = com_ports()
    dpg.configure_item("sem_port_cb", items=[p.name + " - " + p.description for p in ports])
    dpg.configure_item("design_port_cb", items=[p.name + " - " + p.description for p in ports])


def remove_port_descrip(user_data):
    user_data[0].set_serial_name(user_data[0].get_serial_name().split("-")[0][:-1])
    user_data[1].set_serial_name(user_data[1].get_serial_name().split("-")[0][:-1])
    return user_data


def injection_callback(sender, value, user_data):
    dpg.set_item_label("inject_btn", "Launched")
    user_data = remove_port_descrip(user_data)
    launch_injection(injection_full_path, user_data)


def create_right_window():
    with dpg.group(horizontal=True):
        dpg.add_button(label="Load file...", tag="load_addr_file", callback=select_file)
        dpg.add_text(tag="addr_filename_text")
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Update ports", callback=update_ports_callback)
    with dpg.group(horizontal=True):
        dpg.add_text("Baudrate (bps)")
        baud_rates = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        dpg.add_combo([baud for baud in baud_rates], width=143, tag="baud_desp_inj", default_value="921600",
                      height_mode=dpg.mvComboHeight_Largest, callback=set_baudrate_callback)
    with dpg.group(horizontal=True):
        dpg.add_text("SEM IP Port")
        dpg.add_spacer()
        ports = com_ports()
        dpg.add_combo([p.name + " - " + p.description for p in ports], width=300, tag="sem_port_cb", callback=set_port_name_callback,
                      user_data=sem_port)
    with dpg.group(horizontal=True):
        dpg.add_text("Design Port")
        dpg.add_spacer(width=7)
        ports = com_ports()

        dpg.add_combo([p.name + " - " + p.description for p in ports], width=300, tag="design_port_cb", callback=set_port_name_callback,
                      user_data=design_port)
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Launch injection", tag="inject_btn", callback=injection_callback, user_data=[sem_port, design_port])
    with dpg.group(horizontal=True):
        dpg.add_text("IMPORTANT: Turn on the FPGA after \"Launch injection\"")
