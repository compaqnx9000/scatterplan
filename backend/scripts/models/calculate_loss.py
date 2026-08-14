import math
import numpy as np
from numba import njit
from utils.math.math_utils import calculate_theta_pair, calculate_theta_t, calculate_theta_r

LOSS_PARAMS = np.array([
    [7.2, 0.5, 2.7, 6.6, 1, 200],  # 温带/亚热带大陆性
    [7.8, 0.375, 3.4, 20, 2, 280],  # 大陆性温带
    [7.8, 0.375, 3.2, 16, 1.7, 280],  # 海洋性温带
    [10.2, 0.33, 6.4, 8, 0.85, 300],  # 海洋性亚热带
    [6.3, 0.43, 2.3, 4.7, 0.45, 250],  # 赤道
], dtype=np.float32)

CLIMATE_PARAMS = np.array([
    (26.00, 0.27, 8),  # 海洋
    (39.60, 0.33, 9),  # 赤道
    (29.73, 0.27, 7),  # 大陆性亚热带
    (19.30, 0.32, 10),  # 海洋性亚热带
    (38.50, 0.27, 11),  # 沙漠
    (29.73, 0.27, 7),  # 大陆性温带
    (33.20, 0.27, 7),  # 海洋性温带
], dtype=[('M', np.float32), ('gamma', np.float32), ('Y90_equation', np.int32)])


@njit(cache=True)
def _estimate_Yq(Y90_equation, distance_km, q, h, freq_mhz):
    if Y90_equation == 7:
        Y90 = -2.2 - (8.1 - 2.3e-4 * min(freq_mhz, 4000)) * np.exp(-0.137 * h)
    elif Y90_equation == 8:
        Y90 = -9.5 - 3 * np.exp(-0.137 * h)
    elif Y90_equation == 9:
        if distance_km < 100:
            Y90 = -8.2
        elif 100 <= distance_km < 1000:
            Y90 = 1.006e-8 * distance_km ** 3 - 2.569e-5 * distance_km ** 2 + 0.02242 * distance_km - 10.2
        else:
            Y90 = -3.4
    elif Y90_equation == 10:
        if distance_km < 100:
            Y90 = -10.845
        elif 100 <= distance_km < 465:
            Y90 = -4.5e-7 * distance_km ** 3 + 4.45e-4 * distance_km ** 2 - 0.122 * distance_km - 2.645
        else:
            Y90 = -8.4
    elif Y90_equation == 11:
        if distance_km < 100:
            Y90 = -11.5
        elif 100 <= distance_km < 465:
            Y90 = -8.519e-8 * distance_km ** 3 + 7.444e-5 * distance_km ** 2 + 4.18e-4 * distance_km - 12.1
        else:
            Y90 = -4.0
    else:
        Y90 = 0.0

    if 50 <= q < 90:
        Cq = 0
    elif 90 <= q < 99:
        Cq = 1
    elif 99 <= q < 99.9:
        Cq = 1.82
    elif 99.9 <= q < 99.99:
        Cq = 2.41
    else:
        Cq = 2.90
    return Cq * Y90


@njit(cache=True)
def _estimate_Lc(Gt, Gr):
    return 0.07 * np.exp(0.055 * (Gt + Gr))


@njit(cache=True)
def _estimate_transmission_loss(M, d_km, theta_mrad, Ln, Lc, Y_q_dB, Gt, Gr, freq_mhz):
    term1 = M
    term2 = 30 * np.log10(freq_mhz)
    term3 = 10 * np.log10(d_km)
    term4 = 30 * np.log10(theta_mrad)
    return term1 + term2 + term3 + term4 + Ln + Lc - Gt - Gr - Y_q_dB


@njit(cache=True)
def calculate_scatter_angle(d_km, theta_t_mrad, theta_r_mrad, k=4 / 3, a_km=6370):
    theta_e_mrad = (d_km * 1000) / (k * a_km)
    return theta_e_mrad + theta_t_mrad + theta_r_mrad


@njit(cache=True)
def estimate_Ln(theta_mrad, d_km, gamma, k=4 / 3, a_km=6370.0):
    H = (1e-3 * theta_mrad * d_km) / 4
    h = (1e-6 * (theta_mrad ** 2) * k * a_km) / 8
    LN = 20 * np.log10(5 + gamma * H) + 4.34 * gamma * h
    return LN, h


@njit(cache=True)
def calculate_residual_value(d_km, zone):
    sigma_max, k_sigma_max, sigma_min, p_sigma, C_sigma, Dm = LOSS_PARAMS[zone]
    if d_km <= Dm:
        sigma = sigma_max * (np.sin(np.radians(k_sigma_max * d_km)) ** 2)
    else:
        sigma = sigma_min + p_sigma * np.exp(-1e6 * C_sigma * (d_km ** 2))
    M0 = 1.0
    residual_value_M_0 = M0 / sigma
    # 近似erf，可用taylor或查表，或直接返回residual_value_M_0
    reliability = 0.5 * (1 + residual_value_M_0 / np.sqrt(2)) * 100
    return residual_value_M_0, reliability


@njit(cache=True)
def calculate_area_loss(distances, height, flag, freq, zone):
    length = flag.shape[0]
    losses = np.zeros(length, dtype=np.uint16)
    theta_t, theta_r = 0.0, 0.0

    for i in range(1, length):
        d_km = distances[i] / 1000
        if flag[i]:
            losses[i] = int(32.45 + 20 * np.log10(d_km) + 20 * np.log10(freq))
        else:
            if i < 300:
                # theta_t, theta_r = calculate_theta_pair(height[:i + 1], distances[:i + 1])
                theta_t = calculate_theta_t(height[:i + 1], distances[:i + 1])
            theta_r = calculate_theta_r(height[:i + 1], distances[:i + 1])

            M = CLIMATE_PARAMS[zone]['M']
            gamma = CLIMATE_PARAMS[zone]['gamma']

            theta_scattering = calculate_scatter_angle(d_km, theta_t, theta_r)
            Ln, h = estimate_Ln(theta_scattering, d_km, gamma)

            losses[i] = int(M + 30 * np.log10(freq) + 10 * np.log10(d_km) + 30 * np.log10(theta_scattering) + Ln)
    return losses
