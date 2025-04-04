import dearpygui.dearpygui as dpg
from fpga_data import fpgas

ebd_full_path = ""

def create_address_window():
    coords_inputs = []
    with dpg.group(horizontal=True):
        dpg.add_button(label="Load EDB file...", tag="load_ebd_file", callback=select_file)
        dpg.add_text(tag="ebd_filename_text")
    with dpg.group(horizontal=True):
        dpg.add_text("Select FPGA")
        dpg.add_combo([fpga for fpga in fpgas], width=150, tag="fpga_desp", callback=update_coords,
                      user_data=coords_inputs)
    with dpg.group(horizontal=True):
        dpg.add_text("X_Lo")
        x_lo_input = dpg.add_input_int(default_value=0, min_value=50, max_value=100, width=150, step=0, step_fast=0,
                                       callback=manual_clamp_xlo_callback, user_data=coords_inputs)
        coords_inputs.append(x_lo_input)
    with dpg.group(horizontal=True):
        dpg.add_text("Y_Lo")
        y_lo_input = dpg.add_input_int(default_value=0, min_value=50, max_value=100, width=150, step=0, step_fast=0,
                                       callback=manual_clamp_ylo_callback, user_data=coords_inputs)
        coords_inputs.append(y_lo_input)
    with dpg.group(horizontal=True):
        dpg.add_text("X_Hi")
        x_hi_input = dpg.add_input_int(default_value=0, min_value=50, max_value=100, width=150, step=0, step_fast=0,
                                       callback=manual_clamp_xhi_callback, user_data=coords_inputs)
        coords_inputs.append(x_hi_input)
    with dpg.group(horizontal=True):
        dpg.add_text("Y_Hi")
        y_hi_input = dpg.add_input_int(default_value=0, min_value=50, max_value=100, width=150, step=0, step_fast=0,
                                       callback=manual_clamp_yhi_callback, user_data=coords_inputs)
        coords_inputs.append(y_hi_input)
    with dpg.group(horizontal=True):
        dpg.add_text("Injection Strategy [WIP]")
        #types = ["Statistical", "Accumulated", "Multiple Bit Upset", "Patterns", "Bit-Flip"]
        strategies = ["Exhaustive", "Random", "Module-Specific", "Pattern-Based"]
        dpg.add_combo([strategy for strategy in strategies], width=230, tag="type_desp")#, callback=update_coords, user_data=coords_inputs)

    with dpg.group(horizontal=True):
        dpg.add_button(label="Generate addresses", callback=gen_addrs_callback, user_data=coords_inputs)

    with dpg.group(horizontal=True):
        dpg.add_text("", tag="acme_log")


def select_file(sender, app_data):
    with dpg.file_dialog(directory_selector=False, show=True, height=600, callback=file_selected):
        dpg.add_file_extension(".ebd", color=(30, 140, 30, 255))


def file_selected(sender, value, user_data):
    global ebd_full_path
    ebd_full_path = value["file_path_name"]
    dpg.set_value("ebd_filename_text", value["file_name"])


def update_coords(sender, value, user_data):
    for i, coord in enumerate(["X_Lo", "Y_Lo", "X_Hi", "Y_Hi"]):
        if dpg.get_value(user_data[i]) == 0:
            dpg.set_value(user_data[i], fpgas[value][coord])
        if i == 0:
            if dpg.get_value(user_data[i]) < fpgas[value][coord]:
                dpg.set_value(user_data[i], fpgas[value][coord])
            dpg.configure_item(user_data[i], min_value=fpgas[value]["X_Lo"])
            dpg.configure_item(user_data[i], max_value=fpgas[value]["X_Hi"] - 1)
        elif i == 1:
            if dpg.get_value(user_data[i]) < fpgas[value][coord]:
                dpg.set_value(user_data[i], fpgas[value][coord])
            dpg.configure_item(user_data[i], min_value=fpgas[value]["Y_Lo"])
            dpg.configure_item(user_data[i], max_value=fpgas[value]["Y_Hi"] - 1)
        elif i == 2:
            if dpg.get_value(user_data[i]) > fpgas[value][coord]:
                dpg.set_value(user_data[i], fpgas[value][coord])
            dpg.configure_item(user_data[i], min_value=fpgas[value]["X_Lo"] + 1)
            dpg.configure_item(user_data[i], max_value=fpgas[value]["X_Hi"])
        elif i == 3:
            if dpg.get_value(user_data[i]) > fpgas[value][coord]:
                dpg.set_value(user_data[i], fpgas[value][coord])
            dpg.configure_item(user_data[i], min_value=fpgas[value]["Y_Lo"] + 1)
            dpg.configure_item(user_data[i], max_value=fpgas[value]["Y_Hi"])


def manual_clamp_xlo_callback(sender, value, user_data):
    x_lo_pos = 0
    x_hi_pos = 2
    if value > dpg.get_value(user_data[x_hi_pos]) and dpg.get_value(user_data[x_hi_pos]) != 0:
        dpg.set_value(user_data[x_lo_pos], dpg.get_value(user_data[x_hi_pos])-1)


def manual_clamp_ylo_callback(sender, value, user_data):
    y_lo_pos = 1
    y_hi_pos = 3
    if value > dpg.get_value(user_data[y_hi_pos]) and dpg.get_value(user_data[y_hi_pos]) != 0:
        dpg.set_value(user_data[y_lo_pos], dpg.get_value(user_data[y_hi_pos])-1)


def manual_clamp_xhi_callback(sender, value, user_data):
    x_lo_pos = 0
    x_hi_pos = 2
    if value < dpg.get_value(user_data[x_lo_pos]):
        dpg.set_value(user_data[x_hi_pos], dpg.get_value(user_data[x_lo_pos])+1)


def manual_clamp_yhi_callback(sender, value, user_data):
    y_lo_pos = 1
    y_hi_pos = 3
    if value < dpg.get_value(user_data[y_lo_pos]):
        dpg.set_value(user_data[y_hi_pos], dpg.get_value(user_data[y_lo_pos])+1)


def gen_addrs_callback(sender, value, user_data):
    coords = {"X_Lo": dpg.get_value(user_data[0]), "Y_Lo": dpg.get_value(user_data[1]),
              "X_Hi": dpg.get_value(user_data[2]), "Y_Hi": dpg.get_value(user_data[3])}
    try:
        with open(ebd_full_path, "r") as file:
            ebd_file_lines = file.readlines()
        if dpg.get_value("fpga_desp") == "":
            dpg.set_value("acme_log", "Please, select a valid FPGA.")
            return
        with dpg.window(modal=True, no_move=True, no_close=True, no_title_bar=True, no_resize=True) as loading_window:
            with dpg.group(horizontal=True):
                dpg.add_loading_indicator(pos=[10, 20])
                dpg.add_text("Generating injection addresses...", pos=[100, 42])
        if dpg.get_value("fpga_desp") == "KCU105":
            from acme import generate_injection_addresses
            result = generate_injection_addresses(ebd_file_lines, coords, "KCU105")
        elif dpg.get_value("fpga_desp") == "Nexys4":
            from acme_nexys import generate_injection_addresses
            result = generate_injection_addresses(ebd_file_lines, coords, "Nexys4")
        injection_file_path = ebd_full_path[:ebd_full_path.rfind("\\")] + "\\injection_addresses.txt"
        #print(injection_file_path)
        with open(injection_file_path, "w") as file:
            for line in result:
                file.write(line)
        dpg.delete_item(loading_window)
        dpg.set_value("acme_log", f"Done! {len(result)} Injection Addresses Generated!")
    except FileNotFoundError:
        dpg.set_value("acme_log", "EDB file not found. Please, select a valid EDB file.")
