import dearpygui.dearpygui as dpg


def calculate_venabletime(sender, value, user_data):
    baud_rates = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    with dpg.window(modal=True, no_move=True, no_close=False, no_title_bar=False, no_resize=True,
                    on_close=delete_venable_items) as venable_window:
        with dpg.group(horizontal=True, horizontal_spacing=20):
            dpg.add_text("Clock Frequency (MHz)")
            dpg.add_text("Baudrate (bps)")
            dpg.add_text("V_ENABLETIME")
            dpg.add_text("ERROR (%)")
        with dpg.group(horizontal=True, horizontal_spacing=20):
            dpg.add_input_int(tag="freq", width=225, step=0, step_fast=0, callback=calculate_venabletime_callback)
            dpg.add_combo([baud for baud in baud_rates], width=143, tag="baud_desp", default_value="115200",
                          height_mode=dpg.mvComboHeight_Largest, callback=calculate_venabletime_callback)
            dpg.add_input_int(tag="v_enable", width=167, step=0, step_fast=0, readonly=True)
            dpg.add_text(tag="v_enable_error")


def delete_venable_items(sender, value, user_data):
    dpg.delete_item("freq")
    dpg.delete_item("baud_desp")
    dpg.delete_item("v_enable")
    dpg.delete_item("v_enable_error")


def calculate_venabletime_callback(sender, value, user_data):
    freq = dpg.get_value("freq")
    baud_rate = int(dpg.get_value("baud_desp"))
    v_enable_time = round(freq * 1000000 / (16 * baud_rate))-1
    error = (abs(freq * 1000000 / (16 * (v_enable_time + 1)) - baud_rate) / baud_rate) * 100
    dpg.set_value("v_enable", v_enable_time)
    dpg.set_value("v_enable_error", f"{error:.2f}")
    if error < 1:
        dpg.configure_item("v_enable_error", color=[0, 0, 0])
    else:
        dpg.configure_item("v_enable_error", color=[255, 0, 0])
