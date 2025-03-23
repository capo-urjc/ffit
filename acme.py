import os


def check_coords(board, input_coords):
    if board == "KCU105":
        board_coords = {"X_Lo": 50, "Y_Lo": 0, "X_Hi": 357, "Y_Hi": 309}
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
    bounds = [[50, 57],   [58, 65],   [66, 73],   [74, 80],   [81, 94],   [95, 102],  [103, 110],   # Clock region X0
              [111, 118], [119, 126], [127, 134], [135, 141], [142, 155], [156, 163], [164, 171],   # Clock region X1
              [172, 221], [222, 234], [235, 245], [246, 251], [252, 258], [259, 269], [270, 281], [282, 286], [287, 293],   # Clock region X2
              [294, 302], [303, 309], [310, 317], [318, 336], [337, 357]]   # Clock region X3
    offsets = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70]

    for coord in ["X_Lo", "X_Hi"]:
        for o, b in zip(offsets, bounds):
            if b[0] <= input_coords[coord] <= b[1]:
                input_coords[coord] -= o
                break
    return input_coords


def get_partial_frames(input_coords, fy_multiple):
    KCU105_MIN_X = 50
    KCU105_FX = 22
    KCU105_FY = 5236
    WF_ULTRASCALE = 123

    frames = [((input_coords["X_Lo"] - KCU105_MIN_X) * KCU105_FX + KCU105_FY * fy_multiple) * WF_ULTRASCALE,
              ((input_coords["X_Hi"] - KCU105_MIN_X) * KCU105_FX + (KCU105_FX - 1) + KCU105_FY * fy_multiple)
              * WF_ULTRASCALE]
    return frames


def get_words(input_coords, y_min_low, y_min_high, single_region=False):
    WF_ULTRASCALE = 123

    words = []
    if single_region:
        words.append((y_min_high - input_coords["Y_Hi"]) * 2)
    if input_coords["Y_Lo"] == (y_min_low + 1):
        words.append(WF_ULTRASCALE - 1)
    else:
        words.append((y_min_high - input_coords["Y_Lo"]) * 2 + 1)
    return words


def get_words_multiregion(input_coords, y_min_low, y_min_high):
    WF_ULTRASCALE = 123

    words = []
    if input_coords["Y_Hi"] == (y_min_low + 1):
        words.append(WF_ULTRASCALE - 1)
    else:
        words.append((y_min_high - input_coords["Y_Hi"]) * 2)
    return words


def get_words_filler(multiple):
    WF_ULTRASCALE = 123
    words = []
    for i in range(multiple):
        words.append(WF_ULTRASCALE - 1)
        words.append(0)
    return words


def get_frames(board, input_coords):
    KCU105_Y4 = 61
    KCU105_Y3 = 123
    KCU105_Y2 = 185
    KCU105_Y1 = 247
    #KCU105_MIN_X = 50
    KCU105_MAX_Y = 309
    #KCU105_FX = 22
    #KCU105_FY = 5236
    #WF_ULTRASCALE = 123

    frames = []
    words = []
    clock_regions = -1

    # Y Lo and Y Hi belong to CLOCK REGION Y4
    if input_coords["Y_Lo"] >= 0 and input_coords["Y_Hi"] <= KCU105_Y4:
        frames += get_partial_frames(input_coords, 4)
        words += get_words(input_coords, -1, KCU105_Y4, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y3
    elif input_coords["Y_Lo"] > KCU105_Y4 and input_coords["Y_Hi"] <= KCU105_Y3:
        frames += get_partial_frames(input_coords, 3)
        words += get_words(input_coords, KCU105_Y4, KCU105_Y3, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y2
    elif input_coords["Y_Lo"] > KCU105_Y3 and input_coords["Y_Hi"] <= KCU105_Y2:
        frames += get_partial_frames(input_coords, 2)
        words += get_words(input_coords, KCU105_Y3, KCU105_Y2, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y1
    elif input_coords["Y_Lo"] > KCU105_Y2 and input_coords["Y_Hi"] <= KCU105_Y1:
        frames += get_partial_frames(input_coords, 1)
        words += get_words(input_coords, KCU105_Y2, KCU105_Y1, single_region=True)
        clock_regions = 1

    # Y Lo and Y Hi belong to CLOCK REGION Y0
    elif input_coords["Y_Lo"] > KCU105_Y1 and input_coords["Y_Hi"] <= KCU105_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        words += get_words(input_coords, KCU105_Y1, KCU105_MAX_Y, single_region=True)
        clock_regions = 1

    # Y Lo belongs to CLOCK REGION Y4 and Y Hi belongs to CLOCK REGION Y3
    elif 0 <= input_coords["Y_Lo"] <= KCU105_Y4 and KCU105_Y4 < input_coords["Y_Hi"] <= KCU105_Y3:
        frames += get_partial_frames(input_coords, 3)
        frames += get_partial_frames(input_coords, 4)
        words += get_words_multiregion(input_coords, KCU105_Y4, KCU105_Y3)
        words += get_words_filler(1)
        words += get_words(input_coords, -1, KCU105_Y4)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y2
    elif KCU105_Y4 <= input_coords["Y_Lo"] <= KCU105_Y3 and KCU105_Y3 < input_coords["Y_Hi"] <= KCU105_Y2:
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, KCU105_Y3, KCU105_Y2)
        words += get_words_filler(1)
        words += get_words(input_coords, KCU105_Y4, KCU105_Y3)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y2 and Y Hi belongs to CLOCK REGION Y1
    elif KCU105_Y3 <= input_coords["Y_Lo"] <= KCU105_Y2 and KCU105_Y2 < input_coords["Y_Hi"] <= KCU105_Y1:
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        words += get_words_multiregion(input_coords, KCU105_Y2, KCU105_Y1)
        words += get_words_filler(1)
        words += get_words(input_coords, KCU105_Y3, KCU105_Y2)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y1 and Y Hi belongs to CLOCK REGION Y0
    elif KCU105_Y2 <= input_coords["Y_Lo"] <= KCU105_Y1 and KCU105_Y1 < input_coords["Y_Hi"] <= KCU105_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        words += get_words_multiregion(input_coords, KCU105_Y1, KCU105_MAX_Y)
        words += get_words_filler(1)
        words += get_words(input_coords, KCU105_Y2, KCU105_Y1)
        clock_regions = 2

    # Y Lo belongs to CLOCK REGION Y4 and Y Hi belongs to CLOCK REGION Y2
    elif 0 <= input_coords["Y_Lo"] <= KCU105_Y4 and KCU105_Y3 < input_coords["Y_Hi"] <= KCU105_Y2:
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        frames += get_partial_frames(input_coords, 4)
        words += get_words_multiregion(input_coords, KCU105_Y3, KCU105_Y2)
        words += get_words_filler(2)
        words += get_words(input_coords, -1, KCU105_Y4)
        clock_regions = 3

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y1
    elif KCU105_Y4 <= input_coords["Y_Lo"] <= KCU105_Y3 and KCU105_Y2 < input_coords["Y_Hi"] <= KCU105_Y1:
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, KCU105_Y2, KCU105_Y1)
        words += get_words_filler(2)
        words += get_words(input_coords, KCU105_Y4, KCU105_Y3)
        clock_regions = 3

    # Y Lo belongs to CLOCK REGION Y2 and Y Hi belongs to CLOCK REGION Y0
    elif KCU105_Y3 <= input_coords["Y_Lo"] <= KCU105_Y2 and KCU105_Y1 < input_coords["Y_Hi"] <= KCU105_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        words += get_words_multiregion(input_coords, KCU105_Y1, KCU105_MAX_Y)
        words += get_words_filler(2)
        words += get_words(input_coords, KCU105_Y3, KCU105_Y2)
        clock_regions = 3

    # Y Lo belongs to CLOCK REGION Y4 and Y Hi belongs to CLOCK REGION Y1
    elif 0 <= input_coords["Y_Lo"] <= KCU105_Y4 and KCU105_Y2 < input_coords["Y_Hi"] <= KCU105_Y1:
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        frames += get_partial_frames(input_coords, 4)
        words += get_words_multiregion(input_coords, KCU105_Y2, KCU105_Y1)
        words += get_words_filler(3)
        words += get_words(input_coords, -1, KCU105_Y4)
        clock_regions = 4

    # Y Lo belongs to CLOCK REGION Y3 and Y Hi belongs to CLOCK REGION Y0
    elif KCU105_Y4 <= input_coords["Y_Lo"] <= KCU105_Y3 and KCU105_Y1 < input_coords["Y_Hi"] <= KCU105_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        words += get_words_multiregion(input_coords, KCU105_Y1, KCU105_MAX_Y)
        words += get_words_filler(3)
        words += get_words(input_coords, KCU105_Y4, KCU105_Y3)
        clock_regions = 4

    # Y Lo belongs to CLOCK REGION Y4 and Y Hi belongs to CLOCK REGION Y0
    elif 0 <= input_coords["Y_Lo"] <= KCU105_Y4 and KCU105_Y1 < input_coords["Y_Hi"] <= KCU105_MAX_Y:
        frames += get_partial_frames(input_coords, 0)
        frames += get_partial_frames(input_coords, 1)
        frames += get_partial_frames(input_coords, 2)
        frames += get_partial_frames(input_coords, 3)
        frames += get_partial_frames(input_coords, 4)
        words += get_words_multiregion(input_coords, KCU105_Y1, KCU105_MAX_Y)
        words += get_words_filler(4)
        words += get_words(input_coords, -1, KCU105_Y4)
        clock_regions = 5

    return frames, words, clock_regions


def ebd_translate(lines, frames, words, clock_regions):
    import numpy as np
    DUMMY_ULTRASCALE = 141
    WF_ULTRASCALE = 123
    BITS_IN_LINE = 32

    lines = lines[DUMMY_ULTRASCALE:]  # skip Header and Dummy frames
    addresses = []
    for i in range(clock_regions):
        line_min = frames[i * 2]
        line_max = frames[i * 2 + 1]
        word_min = words[i * 2]
        word_max = words[i * 2 + 1]
        curr_line = line_min
        for k in range(line_min, line_max+1, WF_ULTRASCALE):
            for m in range(WF_ULTRASCALE):
                if word_min <= m <= word_max:
                    if curr_line >= len(lines):
                        break
                    line = lines[curr_line][:-1]
                    line = np.array([f for f in line[::-1]]).astype(int)
                    if sum(line) > 0:
                        for n in range(BITS_IN_LINE):
                            if line[n]:
                                la = hex(k // WF_ULTRASCALE)[2:]
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
    board = "KCU105"
    coords = {"X_Lo": 50, "Y_Lo": 0, "X_Hi": 357, "Y_Hi": 309}
    if check_coords(board, coords):
        filename = get_ebd_filename()
        with open(filename, "r") as file:
            lines = file.readlines()
        addresses = generate_injection_addresses(lines, coords, board)
        print(addresses)
    else:
        print("Coordenadas incorrectas")
