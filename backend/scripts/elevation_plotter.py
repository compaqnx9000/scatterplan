from os import path, makedirs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from django.conf import settings
import matplotlib

matplotlib.use('Agg')
# matplotlib.use('TkAgg')


class ElevationPlotter:
    """
    高程剖面绘图类
    """

    def __init__(self, figsize=(12, 6)):
        """
        初始化绘图类
        :param figsize: 画布大小
        """
        self.figsize = figsize

    def plot_profile(self, D, H, scatterer_point, tx_barrier_point, rx_barrier_point, image_path):
        """
       绘制高程剖面图（可视域、非可视域、最高点标记）

       :param D: 距离数据，单位为米的数组
       :param H: 高程数据，单位为米的数组
       :param scatterer_point: 散射体位置坐标，格式为 (距离, 高度) 的元组
       :param tx_barrier_point: 发射端障碍物点位置坐标，格式为 (距离, 高度) 的元组
       :param rx_barrier_point: 接收端障碍物点位置坐标，格式为 (距离, 高度) 的元组
       """
        # --- 计算高程图相关信息 ---
        distances_km = [d / 1000.0 for d in D]
        # max_H = np.max(H)
        # max_idx = np.argmax(H)
        # max_dist = distances_km[max_idx]

        # --- 计算散射体信息 ---
        scatterer_x = np.array([distances_km[0], scatterer_point[0] / 1000, distances_km[-1]])
        scatterer_y = np.array([H[0], scatterer_point[1], H[-1]])

        # --- 计算障碍物信息 ---
        barrier_x = [tx_barrier_point[0] / 1000, rx_barrier_point[0] / 1000]
        barrier_y = [tx_barrier_point[1], rx_barrier_point[1]]

        # --- 配置 matplotlib 中文 + 深色主题（对齐前端 Gotham） ---
        bg = "#1a222c"
        panel = "#12181f"
        text = "#e8e2d2"
        muted = "#8b8790"
        grid = "#3a4552"
        elev_color = "#7ec8ff"
        path_color = "#c45c4a"

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=self.figsize, facecolor=bg)
        ax.set_facecolor(panel)

        xs = np.asarray(distances_km, dtype=float)
        ys = np.asarray(H, dtype=float)
        y_floor = 0.0
        y_top = max(float(np.max(ys)), float(scatterer_point[1]), float(np.max(barrier_y))) * 1.08

        fill_verts = np.vstack([
            np.column_stack([xs, ys]),
            [xs[-1], y_floor],
            [xs[0], y_floor],
            [xs[0], ys[0]],
        ])
        fill_clip = PathPatch(Path(fill_verts), transform=ax.transData, facecolor='none', edgecolor='none')
        ax.add_patch(fill_clip)
        fill_cmap = LinearSegmentedColormap.from_list(
            'elev_fill',
            [(0.0, (0.49, 0.78, 1.0, 0.0)), (1.0, (0.49, 0.78, 1.0, 0.58))],
        )
        ax.imshow(
            np.linspace(0, 1, 256).reshape(-1, 1),
            cmap=fill_cmap,
            aspect='auto',
            origin='lower',
            extent=[xs[0], xs[-1], y_floor, y_top],
            interpolation='bicubic',
            clip_path=fill_clip,
            clip_on=True,
            zorder=0,
        )
        ax.set_xlim(xs[0], xs[-1])
        ax.set_ylim(y_floor, y_top)

        ax.plot(xs, ys, color=elev_color, linewidth=1.8, label='高程', zorder=3)
        ax.plot(scatterer_x, scatterer_y, color=path_color, linewidth=1.4, zorder=4)
        ax.scatter([scatterer_x[1]], [scatterer_y[1]], color='#e8b52a', s=36, label='散射体', zorder=5)
        ax.scatter(barrier_x, barrier_y, color='#c47a5a', s=32, label='障碍物点', zorder=5)
        ax.scatter([distances_km[0]], [H[0]], color='#5aa8ff', s=36, label='发射点', zorder=5)
        ax.scatter([distances_km[-1]], [H[-1]], color='#5a9e6f', s=36, label='接收点', zorder=5)

        ax.set_xlabel("距离 (km)", color=text)
        ax.set_ylabel("高程 (m)", color=text)
        ax.set_title("高程剖面图", color=text, pad=10)
        ax.tick_params(colors=muted)
        for spine in ax.spines.values():
            spine.set_color(grid)
        ax.grid(True, color=grid, alpha=0.55, linewidth=0.6)
        legend = ax.legend(
            facecolor=bg,
            edgecolor=grid,
            labelcolor=text,
            framealpha=0.92,
        )
        legend.get_frame().set_linewidth(0.6)
        fig.tight_layout()

        fig.savefig(
            image_path,
            dpi=300,
            bbox_inches='tight',
            facecolor=fig.get_facecolor(),
            edgecolor='none',
        )
        plt.close(fig)
