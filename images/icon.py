import sys
import os
import re

def xbm_to_bitstring(xbm_file_path: str, width: int, height: int):
    if os.path.splitext(xbm_file_path)[1] != '.xbm':
        print(f"{xbm_file_path} is not a xbm file")
        return []
    with open(xbm_file_path, 'r') as file:
        xbm_data = file.read()

    # ビットマップデータを抽出
    bits_data = re.search(r'static\s+char\s+\w+_bits\[\]\s+=\s+\{([^}]+)\};', xbm_data, re.DOTALL).group(1)
    bits_data = bits_data.replace('\n', '').replace(' ', '').split(',')

    # ビット列を01に変換
    bitstring = ''
    for byte in bits_data:
        byte = byte.strip()
        if byte:
            bitstring += f'{int(byte, 16):08b}'

    half = width // 2
    bit_rows = []
    for i in range(height):
        bit_rows.append(bitstring[i*width+half:(i+1)*width] + bitstring[i*width:i*width+half])

    return bit_rows

def write_to_file(path, width, height):
        rows = xbm_to_bitstring(path, width, height)
        for row in rows:
            print(row)

        file_name = f"{os.path.splitext(os.path.basename(path)[:-4])[0]}_{width}_{height}.txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(rows))
            print(f"succeeded to write to {file_name}")

# python3 icon.py weather-pixel-icons/16/sum.xbm 16 16
# -> translate the input xbm file to sum_16_16.txt
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print("please specify paths to images")

    path = args[1]
    width = int(args[2])
    height = int(args[3])

    if os.path.isfile(path):
        write_to_file(path, width, height)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            write_to_file(os.path.join(path, file), width, height)