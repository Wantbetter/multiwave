import struct
import numpy as np


class Grd:
    def __init__(self, nRow, nCol, xLL, yLL, xSize, ySize, zMin, zMax, data):
        self.rows = nRow
        self.cols = nCol
        self.x_ll = xLL
        self.y_ll = yLL
        self.x_size = xSize
        self.y_size = ySize
        self.z_min = zMin
        self.z_max = zMax
        self.data = data

    def clone_with_new_data(self, data):
        return Grd(self.rows, self.cols, self.x_ll, self.y_ll, self.x_size, self.y_size, self.z_min, self.z_max, data)


def _from_grd_binary(path):
    with open(path, 'rb') as fg:
        fg.seek(0)
        mark, = struct.unpack('4s', fg.read(4))
        fg.seek(20)
        nRow, = struct.unpack('l', fg.read(4))
        nCol, = struct.unpack('l', fg.read(4))
        xLL, = struct.unpack('d', fg.read(8))
        yLL, = struct.unpack('d', fg.read(8))
        xSize, = struct.unpack('d', fg.read(8))
        ySize, = struct.unpack('d', fg.read(8))
        zMin, = struct.unpack('d', fg.read(8))
        zMax, = struct.unpack('d', fg.read(8))

        data = np.zeros((nRow, nCol), dtype=float)
        fg.seek(100)
        for i in range(nRow):
            for j in range(nCol):
                data[i, j], = struct.unpack('d', fg.read(8))

        # func = np.vectorize(lambda x: struct.unpack('d', fg.read(8)))
        # fg.seek(100)
        # map_in_place(data, func)
        return Grd(nRow, nCol, xLL, yLL, xSize, ySize, zMin, zMax, data)


def from_ascii_grd(path):
    lines_to_int = lambda lines: list(map(int, next(lines).split()))
    lines_to_float = lambda lines: list(map(float, next(lines).split()))

    with open(path, 'r') as fr:
        lines = iter(fr.readlines())
        mark = next(lines).strip()

        if mark != 'DSAA':
            raise IOError("错误的grd文件类型")

        line0 = lines_to_int(lines)
        line1 = lines_to_float(lines)
        line2 = lines_to_float(lines)
        line3 = lines_to_float(lines)

        lines = reversed(list(lines))

        cols, rows = line0
        x_ll, x_end = line1
        y_ll, y_end = line2
        z_min, z_max = line3

        x_size = (x_end - x_ll) / (cols - 1)
        y_size = (y_end - y_ll) / (rows - 1)

        data = []
        for i in range(0, rows):
            line = lines_to_float(lines)
            data.append(line)

        data = np.array(data)
        return Grd(rows, cols, x_ll, y_ll, x_size, y_size, z_min, z_max, data)


def to_ascii_grd(path, grd):
    if path is None or path is "":
        return
    if grd is None:
        return
    with open(path, 'w') as fw:
        txt = []
        txt.append('DSAA' + '\n')
        txt.append(str(grd.nCol) + " " + str(grd.nRow) + '\n')
        txt.append(str(grd.xLL) + " " + str(grd.xLL + (grd.nCol-1) * grd.xSize) + '\n')
        txt.append(str(grd.yLL) + " " + str(grd.yLL + (grd.nRow - 1) * grd.ySize) + '\n')
        txt.append(str(grd.zMin) + " " + str(grd.zMax) + '\n')
        data = grd.data.copy()
        data.shape = -1
        data = list(map(str, data))
        txt.append(' '.join(data))
        fw.writelines(txt)
