if __name__ == '__main__':
    original_colors = [(0, 124,188), (0, 153,210), (0, 157,80),
                       (116,174,54), (172,198,26), (235,170,18),
                       (232,136,16), (233,53,16), (225,43,81),
                       (179,53,125), (109,63,151), (70,64,152)]
    res_colors = []
    for color in original_colors:
        new_r_value = round(color[0] / 255, 3)
        new_g_value = round(color[1] / 255, 3)
        new_b_value = round(color[2] / 255, 3)
        new_color = (new_r_value, new_g_value, new_b_value)
        res_colors.append(new_color)
    print(res_colors)
