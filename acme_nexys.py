import os


def check_coords(board, input_coords):
    if board == "Nexys4":
        board_coords = {"X_Lo": 3, "Y_Lo": 1, "X_Hi": 145, "Y_Hi": 207}
    return input_coords["X_Lo"] < input_coords["X_Hi"] and \
           input_coords["Y_Lo"] < input_coords["Y_Hi"] and \
           board_coords["X_Lo"] <= input_coords["X_Lo"] <= board_coords["X_Hi"] and \
           board_coords["X_Lo"] <= input_coords["X_Hi"] <= board_coords["X_Hi"] and \
           board_coords["Y_Lo"] <= input_coords["Y_Lo"] <= board_coords["Y_Hi"] and \
           board_coords["Y_Lo"] <= input_coords["Y_Hi"] <= board_coords["Y_Hi"]


def get_ebd_filename():
    ebd_file = [f for f in os.listdir(os.getcwd()) if "ebd" in f][0]
    return ebd_file


def adjust_coords(input_coords):
    bounds = [[3, 18], [19, 27], [28, 87],                               # Clock region X0
              [88, 93], [94, 107], [108, 118], [119, 127], [128, 145]]   # Clock region X1

    offsets = [0, 1, 2, 3, 4, 5, 6, 7]

    for coord in ["X_Lo", "X_Hi"]:
        for o, b in zip(offsets, bounds):
            if b[0] <= input_coords[coord] <= b[1]:
                input_coords[coord] -= o
                break
    return input_coords


def get_partial_frames(input_coords, fy_multiple):
    NEXYS4_MIN_X = 3
    NEXYS4_FX = 15
    NEXYS4_FY1 = 2025
    NEXYS4_FY2 = 1800
    WF_7SERIES = 101

    offset = None
    if fy_multiple == 0:
        offset = 2 * NEXYS4_FY1 + NEXYS4_FY2
    elif fy_multiple == 1:
        offset = NEXYS4_FY1 + NEXYS4_FY2
    elif fy_multiple == 2:
        offset = 0
    elif fy_multiple == 3:
        offset = NEXYS4_FY1

    frames = [((input_coords["X_Lo"] - NEXYS4_MIN_X) * NEXYS4_FX + offset) * WF_7SERIES + 1,
              ((input_coords["X_Hi"] - NEXYS4_MIN_X) * NEXYS4_FX + (NEXYS4_FX - 1) + offset)
              * WF_7SERIES + 1]
    return frames


def get_words(input_coords, y_min_low, y_min_high, single_region=False):
    WF_7SERIES = 101

    words = []
    if single_region:
        words.append((y_min_high - input_coords["Y_Hi"]) * 2)
    if input_coords["Y_Lo"] == (y_min_low + 1):
        words.append(WF_7SERIES - 1)
    else:
        words.append((y_min_high - input_coords["Y_Lo"]) * 2 + 1)
    return words


def get_words_multiregion(input_coords, y_min_low, y_min_high):
    WF_7SERIES = 101

    words = []
    if input_coords["Y_Hi"] == (y_min_low + 1):
        words.append(WF_7SERIES - 1)
    else:
        words.append((y_min_high - input_coords["Y_Hi"]) * 2)
    return words


def get_words_filler(multiple):
    WF_7SERIES = 101
    words = []
    for i in range(multiple):
        words.append(WF_7SERIES - 1)
        words.append(0)
    return words


def get_frames(board, input_coords):
    NEXYS_Y3 = 51
    NEXYS_Y2 = 103
    NEXYS_Y1 = 155
    NEXYS_MAX_Y = 207


    frames = []
    words = []
    clock_regions = -1

    # Y Lo and Y Hi belong to CLOCK REGION Y3
    if input_coords["Y_Lo"] >= 0 and input_coords["Y_Hi"] <= NEXYS_Y3:
        frames += get_partial_frames(input_coords, 3)
        words += get_words(input_coords, -1, NEXYS_Y3, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y2
    elif input_coords["Y_Lo"] > NEXYS_Y3 and input_coords["Y_Hi"] <= NEXYS_Y2:
        frames += get_partial_frames(input_coords, 2)
        words += get_words(input_coords, NEXYS_Y3, NEXYS_Y2, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y1
    elif input_coords["Y_Lo"] > NEXYS_Y2 and input_coords["Y_Hi"] <= NEXYS_Y1:
        frames += get_partial_frames(input_coords, 1)
        words += get_words(input_coords, NEXYS_Y2, NEXYS_Y1, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y0
    elif input_coords["Y_Lo"] > NEXYS_Y1 and input_coords["Y_Hi"] <= NEXYS_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        words += get_words(input_coords, NEXYS_Y1, NEXYS_MAX_Y, single_region=True)
        clock_regions = 1

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y2
    elif 0 <= input_coords["Y_Lo"] <= NEXYS_Y3 and NEXYS_Y3 < input_coords["Y_Hi"] <= NEXYS_Y2:
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, NEXYS_Y3, NEXYS_Y2)
        words += get_words_filler(1)
        words += get_words(input_coords, -1, NEXYS_Y3)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y2 and Y Hi belongs to CLOCK REGION Y1
    elif NEXYS_Y3 <= input_coords["Y_Lo"] <= NEXYS_Y2 and NEXYS_Y2 < input_coords["Y_Hi"] <= NEXYS_Y1:
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        words += get_words_multiregion(input_coords, NEXYS_Y2, NEXYS_Y1)
        words += get_words_filler(1)
        words += get_words(input_coords, NEXYS_Y3, NEXYS_Y2)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y1 and Y Hi belongs to CLOCK REGION Y0
    elif NEXYS_Y2 <= input_coords["Y_Lo"] <= NEXYS_Y1 and NEXYS_Y1 < input_coords["Y_Hi"] <= NEXYS_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        words += get_words_multiregion(input_coords, NEXYS_Y1, NEXYS_MAX_Y)
        words += get_words_filler(1)
        words += get_words(input_coords, NEXYS_Y2, NEXYS_Y1)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y1
    elif 0 <= input_coords["Y_Lo"] <= NEXYS_Y3 and NEXYS_Y2 < input_coords["Y_Hi"] <= NEXYS_Y1:
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, NEXYS_Y2, NEXYS_Y1)
        words += get_words_filler(2)
        words += get_words(input_coords, -1, NEXYS_Y3)
        clock_regions = 3

    # Y Lo belongs to CLOCK REGION Y2 and Y Hi belongs to CLOCK REGION Y0
    elif NEXYS_Y3 <= input_coords["Y_Lo"] <= NEXYS_Y2 and NEXYS_Y1 < input_coords["Y_Hi"] <= NEXYS_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        words += get_words_multiregion(input_coords, NEXYS_Y1, NEXYS_MAX_Y)
        words += get_words_filler(2)
        words += get_words(input_coords, NEXYS_Y3, NEXYS_Y2)
        clock_regions = 3

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y0
    elif 0 <= input_coords["Y_Lo"] <= NEXYS_Y3 and NEXYS_Y1 < input_coords["Y_Hi"] <= NEXYS_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, NEXYS_Y1, NEXYS_MAX_Y)
        words += get_words_filler(3)
        words += get_words(input_coords, -1, NEXYS_Y3)
        clock_regions = 4

    return frames, words, clock_regions


def ebd_translate(lines, frames, words, clock_regions):
    import numpy as np
    DUMMY_7SERIES = 109
    WF_7SERIES = 101
    BITS_IN_LINE = 32

    lines = lines[DUMMY_7SERIES:]  # skip Header and Dummy frames
    addresses = []
    for i in range(clock_regions):
        line_min = frames[i * 2]
        line_max = frames[i * 2 + 1]
        word_min = words[i * 2]
        word_max = words[i * 2 + 1]
        curr_line = line_min
        for k in range(line_min, line_max+1, WF_7SERIES):
            for m in range(WF_7SERIES):
                if word_min <= m <= word_max:
                    if curr_line >= len(lines):
                        break
                    line = lines[curr_line][:-1]
                    line = np.array([f for f in line[::-1]]).astype(int)
                    if sum(line) > 0:
                        for n in range(BITS_IN_LINE):
                            if line[n]:
                                la = hex(k // WF_7SERIES)[2:]
                                wd_bt = hex((m << 5) + n)[2:].zfill(3)
                                addr = f"C{(la + wd_bt).zfill(9)}\n".upper()
                                addresses.append(addr)
                    curr_line += 1
    return addresses
                        
                        
def generate_injection_addresses(ebd_lines, coords, board):
    coords = adjust_coords(coords)
    frames, words, clock_regions = get_frames(board, coords)
    addresses = ebd_translate(ebd_lines, frames, words, clock_regions)
    return addresses


if __name__ == "__main__":
    board = "Nexys4"
    coords = {"X_Lo": 3, "Y_Lo": 1, "X_Hi": 145, "Y_Hi": 207}
    if check_coords(board, coords):
        filename = get_ebd_filename()
        with open(filename, "r") as file:
            lines = file.readlines()
        addresses = generate_injection_addresses(lines, coords, board)
        print(addresses)
    else:
        print("Coordenadas incorrectas")
