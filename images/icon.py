import sys
from PIL import Image

def color(t) -> str:
    r, g, b = t
    if r >= 180:
        return '2'
    elif (r+g+b)/3 >= 50:
        return '1'
    return '0'

# python3 get_list_from_png.py 01d.png 16 16
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print("please specify paths to images")

    png = args[1]
    width = int(args[2])
    height = int(args[3])

    white = (0, 0, 0) # 0
    black = (73, 72, 74) # 1
    red = (236, 110, 76) # 2
    with Image.open(png) as im:
        resized = im.resize((width, height), resample=Image.BILINEAR)
        ret = list(resized.getdata())
        for i in range(len(ret)):
            ret[i] = color(ret[i][:3])
        ret = [" ".join([ret[i+j*width] for i in range(width)]) for j in range(height)]
        file_name = png[:-4] + ".txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(ret))
        print(f"succeeded to write to {file_name}")
