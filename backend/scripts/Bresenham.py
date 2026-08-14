import numpy as np
from numba import njit

EARTH_Redius = 6371


# @njit(cache=True)
def GenericBresenhamLine(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    # 根据直线的走势方向，设置变化的单位是正是负
    s1 = 1 if ((x2 - x1) > 0) else -1
    s2 = 1 if ((y2 - y1) > 0) else -1
    # 根据斜率的大小，交换dx和dy，可以理解为变化x轴和y轴使得斜率的绝对值为[0,1]
    if dy > dx:
        dy, dx = dx, dy
        point_line = np.zeros((2, dx), dtype=np.int32)
        e = 2 * dy - dx
        x = x1
        y = y1
        point_line0 = [x1, y1]
        for i in range(0, int(dx)):
            if e >= 0:
                x += s1
                e -= 2 * dx
            y += s2
            e += 2 * dy
            point_line[1][i] = x
            point_line[0][i] = y
        point_line[[0, 1], :] = point_line[[1, 0], :]
        point_line_out = np.c_[point_line0, point_line]
    else:
        e = 2 * dy - dx
        x = x1
        y = y1
        point_line = np.zeros((2, dx), dtype=np.int32)
        point_line0 = [x1, y1]
        for i in range(0, int(dx)):
            if e >= 0:
                y += s2
                e -= 2 * dx
            # 根据斜率的不同，让变化大的方向改变一单位，保证两边的变化小于等于1单位，让直线更加均匀
            x += s1
            e += 2 * dy
            point_line[0][i] = x
            point_line[1][i] = y
        point_line_out = np.c_[point_line0, point_line]

    return point_line_out


@njit(cache=True)
def getDistance(lng1, lat1, lng2, lat2):
    radLat1 = np.radians(lat1)
    radLat2 = np.radians(lat2)
    a = radLat1 - radLat2
    b = np.radians(lng1 - lng2)
    s = 2 * np.arcsin(
        np.sqrt(
            np.sin(a / 2) ** 2 +
            np.cos(radLat1) * np.cos(radLat2) * np.sin(b / 2) ** 2
        )
    ) * EARTH_Redius
    return s
