import threading
import collections
import queue
import time
import dearpygui.dearpygui as dpg


def read_not_finished():
    return w_finished


def write_not_finished():
    return not w_finished


def check_ready(input):
    # for c in list(input):
    #     print(ord(c))
    first_o_buffer = [chr(73), chr(84), chr(32), chr(79), chr(75), chr(13), chr(83), chr(67), chr(32), chr(48), chr(50),
                      chr(13), chr(79), chr(62), chr(32)]  # IT OK \n SC 02 \n O>
    i_buffer_1 = [chr(13), chr(79), chr(62), chr(32), chr(73), chr(13), chr(83), chr(67), chr(32), chr(48), chr(48),
                  chr(13), chr(73), chr(62), chr(32)]  # O> I \n SC 00 \n I>
    i_buffer_2 = [chr(83), chr(67), chr(32), chr(49), chr(48), chr(13), chr(83), chr(67), chr(32), chr(48), chr(48),
                  chr(13), chr(73), chr(62), chr(32)]  # SC 10 \n SC 00 \n I>
    i_buffer_1_2 = [chr(13), chr(79), chr(62), chr(32), chr(73), chr(13), chr(83), chr(67), chr(32), chr(48), chr(48),
                  chr(13), chr(73), chr(62), '']  # O> I \n SC 00 \n I>
    i_buffer_2_2 = [chr(83), chr(67), chr(32), chr(49), chr(48), chr(13), chr(83), chr(67), chr(32), chr(48), chr(48),
                  chr(13), chr(73), chr(62), '']  # SC 10 \n SC 00 \n I>
    ready_buffer = [chr(70), chr(67), chr(32), chr(52), chr(48), chr(13), chr(83), chr(67), chr(32), chr(48), chr(50),
                    chr(13), chr(79), chr(62), chr(32)]  # FC 40 \n SC 02 \n O>
    return list(input) == ready_buffer or list(input) == first_o_buffer or list(input) == i_buffer_1 \
                or list(input) == i_buffer_2 or list(input) == i_buffer_1_2 or list(input) == i_buffer_2_2


output_buffer = collections.deque(maxlen=15)


def sem_ip_uart_read(uart, done_write, log_file_path):
    global w_finished, output_buffer
    import collections

    incorrectible = [chr(70), chr(67), chr(32), chr(54), chr(48), chr(13), chr(83), chr(67), chr(32), chr(48), chr(48),
                     chr(13), chr(73), chr(62), chr(32)]  # FC 60 \n SC 00 \n I>

    uart.read_byte()  # initial byte
    file = open(log_file_path, "w")
    waiting = 0
    while True:
        done_write.acquire()
        done_write.wait_for(write_not_finished, 1)
        # print("BUFFER" + str(list(output_buffer)))
        if injection_done:
            # print("READ FINISHED")
            file.close()
            break
        if uart.in_waiting() > 0:
            byte = uart.read_byte()
            output_buffer.append(byte)
            if ord(byte) == 13:  # CR (new line) ascii character
                print("\n", end="", flush=True)
                file.write("\n")
            elif ord(byte) == 62:  # > ascii character, we read "> " and activate writing
                print(byte, end="", flush=True)
                file.write(byte)
                byte = uart.read_byte()
                output_buffer.append(byte)
                print(byte, end="", flush=True)
                file.write(byte)
                if check_ready(output_buffer):
                    # print("FINISHED")
                    waiting = 0
                    w_finished = True
                    done_write.notify()
                    done_write.release()
            else:
                print(byte, end="", flush=True)
                file.write(byte)
        elif list(output_buffer) == incorrectible:
            dpg.set_value("log", dpg.get_value("log") + "Incorrectible error, restart the FPGA")
            output_buffer.clear()
            waiting = 0
        else:  # to timeout faulty injections
            i_buffer_1 = [chr(13), chr(73), chr(62), chr(32), chr(79), chr(13), chr(83), chr(67), chr(32), chr(48),
                          chr(50), chr(13), chr(79), chr(62), chr(32)]  # I> O \n SC 02 \n O>

            if list(output_buffer) == i_buffer_1:
                # print("Waiting", waiting)
                waiting += 1
            if waiting >= 1000:
                waiting = 0
                w_finished = True
                done_write.notify()
                done_write.release()
    file.close()


def sem_ip_uart_write(uart, addresses_queue, addresses, done_write):
    global w_finished, done_writing, output_buffer

    first_o_buffer = [chr(73), chr(84), chr(32), chr(79), chr(75), chr(13), chr(83), chr(67), chr(32), chr(48), chr(50),
                      chr(13), chr(79), chr(62), chr(32)]  # IT OK \n SC 02 \n O>

    instr = 0
    addr_idx = 0
    while True:
        done_write.acquire()
        done_write.wait_for(read_not_finished)
        # print("WRITE_ACQUIRED", output_buffer)
        if list(output_buffer) == first_o_buffer:
            instr = 0
        if instr == 0:
            if addr_idx < len(addresses):
                uart.write_byte("I")
                uart.flush()
            else:
                # print("WRITE FINISHED")
                w_finished = False
                done_write.notify()
                done_write.release()
                break
        elif instr == 1:
            if addr_idx < len(addresses):
                uart.write_byte(f"N {addresses[addr_idx]}")
                uart.flush()
                addresses_queue.put(addr_idx)
                # dpg.set_value("log", dpg.get_value("log") + addresses[addr_idx][:-1])
                dpg.set_value("log", f"Injecting {addr_idx+1}/{len(addresses)}: {addresses[addr_idx][:-1]}")
                addr_idx += 1
        elif instr == 2:
            uart.write_byte("O")
            uart.flush()
            instr = -1
        instr += 1
        w_finished = False
        done_write.notify()
        done_write.release()


def design_uart_read(uart, responses_queue, out_file_path):
    uart.read_byte()  # initial byte
    file = open(out_file_path, "w")
    while True:
        if injection_done:
            file.close()
            break
        if uart.in_waiting() > 0:
            byte = uart.read_byte()
            dpg.set_value("log", dpg.get_value("log") + " - " + byte + "\n")
            responses_queue.put(byte)
            file.write(dpg.get_value("log")[-15:])
    file.close()


def update_clock(start_time, stop_clock):
    elapsed_time = int(time.time() - start_time)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if not stop_clock.is_set():
        dpg.set_value("time_text", "Injection Started! Elapsed Time: " + timer_text)
        threading.Timer(1, update_clock, [start_time, stop_clock]).start()
    else:
        dpg.set_value("time_text", "Injection Completed! Total Time: " + timer_text)


def update_gui(addresses_queue, responses_queue, addresses, output_file):
    num_addresses = len(addresses)
    dpg.set_axis_limits("x_axis", 1, num_addresses+(num_addresses*0.02))
    dpg.fit_axis_data("x_axis")
    num_faults = 0
    x_data = []
    y_data = []
    error_percentage = 0
    start_time = time.time()

    stop_clock = threading.Event()
    update_clock(start_time, stop_clock)
    dpg.set_value("time_text", "Injection in Progress!")

    while True:
        while addresses_queue.empty() and not injection_done:
            time.sleep(0.1)
            continue

        if injection_done and addresses_queue.empty():
            stop_clock.set()
            break

        current_addr_id = addresses_queue.get(block=True, timeout=1) + 1    # Adjustment of the address index to the address number
        addr_percentage = current_addr_id / num_addresses
        dpg.set_value("progress_bar", addr_percentage)
        dpg.set_value("progress_text", f"{addr_percentage*100:.02f}%")
        current_byte = responses_queue.get(block=True, timeout=1)
        if current_byte is not None:
            num_faults += int(current_byte)
            error_percentage = num_faults / current_addr_id * 100
            dpg.set_value("errors_text", f"Current Number of Output Errors: {num_faults} [{error_percentage:03.02f}%]")
            x_data.append(current_addr_id)
            y_data.append(error_percentage)
            dpg.set_value("plot_series", [x_data, y_data])

    dpg.set_value("errors_text", f"Total Output Errors: {num_faults}/{num_addresses} [{error_percentage:03.02f}%]")

    # Just to change the colour of the progress bar to green when finished:
    with dpg.theme(tag="progress_theme"):
        with dpg.theme_component(dpg.mvProgressBar):
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (195, 255, 104, 255))  # Green
    dpg.bind_item_theme("progress_bar", "progress_theme")

    # Save the results in the output file:
    with open(output_file, "a") as f:
        f.write("#################################\n")
        f.write("#     INJECTIONS  COMPLETED     #\n")
        f.write(f"# NUMBER OF INJECTIONS: {num_addresses:7} #\n") #26+7
        f.write(f"# OUTPUT ERRORS: {num_faults:6} ({(num_faults/num_addresses):3.2f}%) #\n")#17+4+2+6+4 = 33
        f.write(f"# TIME REQUIRED:       {dpg.get_value('time_text')[-8:]} #\n") #17+8+2
        f.write("#################################\n")
        f.close()



def launch_injection(injection_addresses, user_data):
    global w_finished, injection_done

    addresses_queue = queue.Queue(maxsize=0)
    responses_queue = queue.Queue(maxsize=0)

    injection_done = False
    w_finished = False
    with open(injection_addresses, "r") as file:
        addresses = file.readlines()

    sem_log_file_path = "sem.txt"
    out_log_file_path = "out.txt"

    update_gui_thread = threading.Thread(name="update gui", target=update_gui,
                                         args=[addresses_queue, responses_queue, addresses, out_log_file_path])
    update_gui_thread.start()

    done_write = threading.Condition()
    sem_ip_uart_read_thread = threading.Thread(name="sem ip uart read", target=sem_ip_uart_read,
                                               args=[user_data[0], done_write, sem_log_file_path])
    sem_ip_uart_read_thread.start()
    sem_ip_uart_write_thread = threading.Thread(name="sem ip uart write", target=sem_ip_uart_write,
                                                args=[user_data[0], addresses_queue, addresses, done_write])
    sem_ip_uart_write_thread.start()

    design_uart_read_thread = threading.Thread(name="design uart read", target=design_uart_read, args=[user_data[1], responses_queue, out_log_file_path])
    design_uart_read_thread.start()

    sem_ip_uart_write_thread.join()
    injection_done = True
    sem_ip_uart_read_thread.join()
    design_uart_read_thread.join()
    update_gui_thread.join()
    user_data[0].close()
    user_data[1].close()
    dpg.set_item_label("inject_btn", "Launch injection")
