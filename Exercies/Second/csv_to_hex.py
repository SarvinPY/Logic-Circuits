import csv
import os

ROM_SIZE = 32768         
ROWS = 8
FRAMES = 16
BYTES_PER_CHAR = ROWS * FRAMES



def build_scroll_frames(bitmap):
    frames = []

    for shift in range(8,0,-1):
        frame=[]
        for row in bitmap:
            frame.append((row >> shift) & 0xFF)
        frames.append(frame)
    frames.append(bitmap.copy())
    for shift in range(1,8):
        frame=[]
        for row in bitmap:
            frame.append((row << shift) & 0xFF)
        frames.append(frame)


    return frames


def ihex_record(rectype,address,data):

    count=len(data)

    s=count
    s+=(address>>8)&0xFF
    s+=address&0xFF
    s+=rectype
    s+=sum(data)

    checksum=((~s+1)&0xFF)

    return ":" \
        +f"{count:02X}" \
        +f"{address:04X}" \
        +f"{rectype:02X}" \
        +''.join(f"{b:02X}" for b in data) \
        +f"{checksum:02X}"


def build_hex(rom):

    lines=[]
    addr=0
    while addr<len(rom):
        chunk=rom[addr:addr+16]
        lines.append(
            ihex_record(0,addr,chunk)
        )
        addr+=16
    lines.append(":00000001FF")

    return lines


def load_csv(path):
    chars=[]
    with open(path,newline='',encoding='utf8') as f:
        reader=csv.DictReader(f)
        for row in reader:
            bitmap=[int(x,16) for x in row["HEX_BYTES"].split()]
            chars.append({
                "index":int(row["INDEX"]),
                "name":row["NAME"],
                "bitmap":bitmap})
    chars.sort(key=lambda c:c["index"])

    return chars


def main():
    csv_file="Fonts.csv"
    out_file="27C256_LED_MATRIX.hex"
    chars=load_csv(csv_file)
    rom=bytearray([0x00]*ROM_SIZE)
    for c in chars:
        frames=build_scroll_frames(c["bitmap"])
        base=c["index"]*BYTES_PER_CHAR
        for f in range(FRAMES):
            for r in range(ROWS):
                addr=base+f*ROWS+r
                rom[addr]=frames[f][r]
    hexlines=build_hex(rom)
    with open(out_file,"w") as f:
        f.write("\n".join(hexlines))
    print("Done.")
    print("Characters :",len(chars))
    print("HEX :",out_file)


if __name__=="__main__":
    main()
    