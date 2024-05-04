import sys
from PIL import Image

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
        resized = im.resize((width, height), resample=Image.NEAREST)
        ret = list(resized.getdata())
        for i in range(len(ret)):
            if ret[i][:3] == white:
                ret[i] = '0'
            elif ret[i][:3] == black:
                ret[i] = '1'
            elif ret[i][:3] == red:
                ret[i] = '2'
            else:
                print("there is an invalid color: ", ret[i])
        ret = [" ".join([ret[i+j*width] for i in range(width)]) for j in range(height)]
        file_name = png[:-4] + ".txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(ret))
        print(f"succeeded to write to {file_name}")
