from PIL import Image, ImageDraw, ImageFont
import numpy
import os

def farbbalken(border_list, ppm_value):
    global data
    grüngrenze = border_list[0]
    gelbgrenze = border_list[1]
    try:
        orangegrenze = border_list[2]
    except IndexError:
        orangegrenze = None
    try:
        rotgrenze = border_list[3]
    except IndexError:
        rotgrenze = None

    if orangegrenze == None:

        # grün
        for i in range(129):
            for a in range(round((1024 / gelbgrenze) * grüngrenze)):
                data[i, a] = [0, 255, 0]

        # gelb
        for i in range(129):
            for a in range(round((1024 / gelbgrenze) * grüngrenze), 1024):
                data[i, a] = [255, 255, 0]

       # ppmwerte auf farbbalken anpassen
        if ppm_value <= 0:
            xwert = 0
        elif ppm_value > gelbgrenze:
            xwert = 1024
        else:
            xwert = round((ppm_value / gelbgrenze) * 1024)

    else:

        for i in range(129):
            for a in range(round((1024 / rotgrenze) * grüngrenze)):
                data[i, a] = [0, 255, 0]

        # gelb
        for i in range(129):
            for a in range(round((1024 / rotgrenze) * grüngrenze), round((1024 / rotgrenze) * gelbgrenze)):
                data[i, a] = [255, 255, 0]

        # orange
        for i in range(129):
            for a in range(round((1024 / rotgrenze) * gelbgrenze), round((1024 / rotgrenze) * orangegrenze)):
                data[i, a] = [255, 165, 0]

         # rot
        for i in range(129):
            for a in range(round((1024 / rotgrenze) * orangegrenze), 1024):
                 data[i, a] = [255, 0, 0]

        # ppmwerte auf farbbalken anpassen
        if ppm_value <= 0:
            xwert = 0
        elif ppm_value > rotgrenze:
            xwert = 1024
        else:
            xwert = round((ppm_value / rotgrenze) * 1024)


    # farbübergang
    if xwert != 0:
        r = 210 / xwert
        g = 105 / xwert
        b = 30 / xwert

        for i in range(32, 96):
            r2 = r
            g2 = g
            b2 = b
            for a in range(xwert):
                data[i, a] = [210 - r2, 105 - g2, 30 - b2]
                r2 = r2 + r
                g2 = g2 + g
                b2 = b2 + b

values_element = {
    'pb': [200, 400, 950, 1900],
    'cd': [2, 2.2, 5.5, 11],
    'cu': [40, 100],
    'zn': [400, 1000],
    'cr': [200, 1000],
    'ni': [70, 150],
    'as': [25, 40, 90, 180]
}

data = None

def createImg(filename, element, ppm_value):
    global data
    data = numpy.zeros((155, 1024, 3), dtype=numpy.uint8)
    # weiß
    for i in range(129, 155):
        for a in range(1024):
            data[i, a] = [255, 255, 255]
    farbbalken(values_element[element], ppm_value)

    image = Image.fromarray(data)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.dirname(os.path.abspath(__file__))+"/static/fonts/GT-Walsheim-Thin.ttf", 25)

    draw.text((5, 128), "0", fill="black", font=font)

    last_value = 11.5
    for border_value, i in zip(values_element[element], range(len(values_element[element]))):
        adjust = - 6.5 * len(str(border_value)) if i != len(values_element[element]) - 1 else - 20 * len(str(border_value))
        x_value = max(border_value / values_element[element][-1] * 1024 + adjust, last_value)
        draw.text((x_value, 128), str(border_value), fill="black", font=font)
        last_value = x_value + 30 * len(str(border_value))

    image.save(filename)

