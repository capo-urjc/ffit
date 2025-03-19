import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

from screeninfo import get_monitors
from serial_port import SerialPort

from acme_window import create_address_window
from injection_window import create_injection_window

screen_resolution = 0


def header_logos():
    if screen_resolution < 1080:
        pos = (1100, 5)
        width = 400
        height = 50
        xoffset = 120
    else:
        pos = (1400, 5)
        width = 400
        height = 90
        xoffset = 250
    with dpg.group(tag="logos_group", pos=pos, width=width, height=height, horizontal=True, xoffset=xoffset):
        if screen_resolution < 1080:
            d1 = 100
            d2 = 50
        else:
            d1 = 200
            d2 = 100
        with dpg.drawlist(d1, d2):
            if screen_resolution < 1080:
                pmin = (0, 0)
                pmax = (100, 50)
            else:
                pmin = (0, 0)
                pmax = (200, 100)
            dpg.draw_image("capo_logo", pmin, pmax)
        with dpg.drawlist(d1, d2):
            if screen_resolution < 1080:
                pmin = (0, 0)
                pmax = (120, 45)
            else:
                pmin = (0, 0)
                pmax = (240, 90)
            dpg.draw_image("urjc_logo", pmin, pmax)


def add_title():
    if screen_resolution < 1080:
        text_offset = 220
        authors_offset = 130
        title_y = 30
        authors_y = title_y + 10
    else:
        text_offset = resolution.width // 2 - 45  # 950
        authors_offset = -300
        title_y = 25
        authors_y = title_y + 30
    dpg.add_text("FPGA Fault Injection Tool", pos=(text_offset-110, title_y))
    dpg.bind_item_font(dpg.last_item(), "ttf-font-big")
    dpg.add_text("Francisco Jose Garcia-Espinosa, Diego Hortelano, Luis Alberto Aranda",
                 pos=(text_offset + authors_offset, authors_y))
    dpg.bind_item_font(dpg.last_item(), "ttf-font-small")
    header_logos()


def load_logos():
    with dpg.texture_registry():
        width_capo, height_capo, _, data_capo = dpg.load_image("images/capo.png")
        dpg.add_static_texture(width_capo, height_capo, data_capo, tag="capo_logo")
        width_urjc, height_urjc, _, data_urjc = dpg.load_image("images/urjc.png")
        dpg.add_static_texture(width_urjc, height_urjc, data_urjc, tag="urjc_logo")


def load_fonts():
    with dpg.font_registry():
        if screen_resolution < 1080:
            big_font = 25
            small_font = 20
        else:
            big_font = 30
            small_font = 25
        dpg.add_font("fonts/LiberationSans-Regular.ttf", big_font, tag="ttf-font-big")
        dpg.add_font("fonts/LiberationSans-Regular.ttf", small_font, tag="ttf-font-small")
    dpg.bind_font("ttf-font-small")


def create_main_window(window_name="Window"):
    load_logos()

    with dpg.window(label=window_name, tag=window_name):
        add_title()
        if screen_resolution < 1080:
            pos = (10, 100)
        else:
            pos = (10, 120)
        with dpg.child_window(border=False, pos=pos):
            with dpg.tab_bar(tag="tab_bar_general"):
                initial_x_pos = 0
                initial_y_pos = 50
                space_between_elements = 10
                width_widget_half_window = 940
                with dpg.tab(label="Fault Injection"):  # First tab, focused on Fault Injection
                    with dpg.group(tag="windows_group_fault_injection", pos=(initial_x_pos, initial_y_pos)):
                        height_configuration_window = 290
                        height_log_window = 190
                        height_completion_window = 90
                        height_graph_window = 550
                        with dpg.child_window(width=width_widget_half_window, height=height_configuration_window, pos=(initial_x_pos, initial_y_pos)):
                            create_injection_window()

                        with dpg.child_window(width=width_widget_half_window, height=height_log_window, pos=(initial_x_pos, height_configuration_window + initial_y_pos + space_between_elements)):
                            log = dpg.add_text("", tag="log")
                            dpg.bind_item_font(log, "ttf-font-big")

                        with dpg.child_window(width=width_widget_half_window, height=height_completion_window, pos=(width_widget_half_window + space_between_elements, initial_y_pos)):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Completed Injections:", pos=(10,10))
                                dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=300, height=25, pos=(10,50))
                                dpg.add_text("0.00%", tag="progress_text", pos=(120, 45))
                                dpg.add_text("Injections not Launched", tag="time_text", pos=(450, 10))
                                dpg.add_text("", tag="errors_text", pos=(450, 45))

                        with dpg.child_window(width=width_widget_half_window, height=height_graph_window, pos=(width_widget_half_window + space_between_elements, initial_y_pos + height_completion_window + space_between_elements)):
                            with dpg.plot(label="Percentage of Output Errors caused by Fault Injections", tag="plot", height=530, width=-1):
                                dpg.add_plot_axis(dpg.mvXAxis, label="Number of Injections", tag="x_axis", no_tick_labels=False)
                                with dpg.plot_axis(dpg.mvYAxis, label="Output Errors (%)", tag="y_axis"):
                                    dpg.set_axis_limits("y_axis", 0, 100)  # 0-100%
                                    dpg.add_scatter_series([], [], label="Fault Rate", tag="plot_series", parent="y_axis")

                with dpg.tab(label="Address Generation", tag="tab_address"):   # Second tab, with functions to obtain injection addresses
                    with dpg.group(tag="windows_group_address_generation", pos=(initial_x_pos, initial_y_pos)):
                        height_widget_window = 500
                        with dpg.child_window(width=width_widget_half_window, height=height_widget_window):
                            create_address_window()
    dpg.set_value("tab_bar_general", "tab_address")
    dpg.set_primary_window(window_name, True)


def exit_app(sender, app_data):
    dpg.stop_dearpygui()


if __name__ == "__main__":
    resolution = get_monitors()[0]
    screen_resolution = get_monitors()[0].height

    dpg.create_context()

    theme_id = themes.create_theme_imgui_light()
    dpg.bind_theme(theme_id)
    load_fonts()
    with dpg.handler_registry():
        dpg.add_key_press_handler(key=256, callback=exit_app)
        dpg.add_key_press_handler(key=27, callback=exit_app)

    create_main_window()

    dpg.create_viewport(title="Fault injection", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.toggle_viewport_fullscreen()
    dpg.start_dearpygui()
    dpg.destroy_context()
