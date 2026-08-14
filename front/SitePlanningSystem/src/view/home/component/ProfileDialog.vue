<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="station-config"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__title">剖面洞察</div>
          <button class="station-config__close" type="button" title="关闭" @click="setVisible(false)" @mousedown.stop>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>

        <section class="insight-card" v-loading="loading">
          <div class="insight-stats">
            <div class="insight-stat">
              <span class="insight-stat__icon is-tx">
                <svg viewBox="0 0 24 24"><path d="M4 18h16v2H4zm2-3 4-5 3 4 4-6 3 7H6z" fill="currentColor"/></svg>
              </span>
              <div>
                <div class="insight-stat__label">发射点高程</div>
                <div class="insight-stat__value">{{ fmt(insights.tx_height) }} m</div>
              </div>
            </div>
            <div class="insight-stat">
              <span class="insight-stat__icon is-peak">
                <svg viewBox="0 0 24 24"><path d="M3 19 9 9l3 4 4-6 5 12H3z" fill="currentColor"/></svg>
              </span>
              <div>
                <div class="insight-stat__label">地形最高</div>
                <div class="insight-stat__value">{{ fmt(insights.max_height) }} m</div>
              </div>
            </div>
            <div class="insight-stat">
              <span class="insight-stat__icon is-dist">
                <svg viewBox="0 0 24 24"><path d="M4 12h16M16 8l4 4-4 4M8 8l-4 4 4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <div>
                <div class="insight-stat__label">通信距离</div>
                <div class="insight-stat__value">{{ fmt(insights.distance, 2) }} km</div>
              </div>
            </div>
            <div class="insight-stat">
              <span class="insight-stat__icon is-scatter">
                <svg viewBox="0 0 24 24"><path d="M12 4v16M7 9l5-5 5 5M7 15l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <div>
                <div class="insight-stat__label">散射体高度</div>
                <div class="insight-stat__value">{{ fmt(insights.scatterer_height) }} m</div>
              </div>
            </div>
          </div>

          <h3 class="insight-title">高程剖面</h3>
          <div v-show="hasDenseSamples" class="insight-chart" ref="chartRef"></div>
          <div v-show="!hasDenseSamples" class="insight-image">
            <img v-if="imageUrl" :src="imageUrl" alt="高程剖面图" />
            <div v-else class="insight-empty">暂无剖面图</div>
          </div>
          <div class="insight-legend">
            <span><i class="dot is-elev"></i>高程</span>
            <span><i class="dot is-tx"></i>发射点</span>
            <span><i class="dot is-obs"></i>障碍物</span>
            <span><i class="dot is-scatter"></i>散射体</span>
            <span><i class="dot is-rx"></i>接收点</span>
          </div>

          <h3 class="insight-title">路径要点</h3>
          <div class="insight-points">
            <div>发射障碍 {{ fmt(txBarrierDistance, 2) }} km · {{ fmt(txBarrierElev) }} m</div>
            <div>散射体 {{ fmt(scattererDistance, 2) }} km · {{ fmt(insights.scatterer_height) }} m</div>
            <div>接收障碍 {{ fmt(rxBarrierFromStart, 2) }} km · {{ fmt(rxBarrierElev) }} m</div>
            <div>接收点 {{ fmt(insights.distance, 2) }} km · {{ fmt(insights.rx_height) }} m</div>
          </div>

          <h3 class="insight-title">信号质量</h3>
          <div class="insight-heat">
            <div class="insight-heat__row">
              <span>路径损耗</span>
              <div class="insight-heat__bar">
                <div class="insight-heat__track"></div>
                <i class="insight-heat__mark" :style="{ left: lossMark + '%' }"></i>
              </div>
              <em>{{ fmt(insights.median_loss, 1) }} dB</em>
            </div>
            <div class="insight-heat__row">
              <span>衰落余量</span>
              <div class="insight-heat__bar">
                <div class="insight-heat__track is-reverse"></div>
                <i class="insight-heat__mark" :style="{ left: residualMark + '%' }"></i>
              </div>
              <em>{{ fmt(insights.residual_value, 1) }} dB</em>
            </div>
          </div>

          <h3 class="insight-title">链路状态</h3>
          <div class="insight-status">
            <div class="insight-status__bar">
              <i :style="{ width: reliabilityMark + '%' }"></i>
            </div>
            <div class="insight-status__scale"><span>0</span><span>50</span><span>100</span></div>
            <div class="insight-status__legend">
              <span><i class="dot is-ok"></i>可靠度 {{ fmt(insights.reliability, 1) }}%</span>
              <span><i class="dot is-power"></i>接收功率 {{ fmt(insights.recv_power, 1) }} dBm</span>
            </div>
          </div>
        </section>

        <div class="station-config__footer">
          <div class="station-config__footer-left">
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
              取消
            </button>
          </div>
          <button
            class="station-config__btn station-config__btn--primary"
            type="button"
            @click="handleConfirm"
          >
            <span>链路计算</span>
            <span class="station-config__btn-arrow">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M9.5 6.5 15.5 12l-6 5.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  imageUrl: {
    type: String,
    default: "",
  },
  loading: {
    type: Boolean,
    default: false,
  },
  insights: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["update:visible", "confirm"]);

const panelRef = ref<HTMLElement | null>(null);
const chartRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 720;
let chart: echarts.ECharts | null = null;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const toNum = (value: any) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
};

const haversineKm = (lng1: number, lat1: number, lng2: number, lat2: number) => {
  if (![lng1, lat1, lng2, lat2].every((v) => Number.isFinite(v) && v !== 0)) return 0;
  const R = 6371;
  const rad = (d: number) => (d * Math.PI) / 180;
  const dLat = rad(lat2 - lat1);
  const dLng = rad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};

const denseSamples = computed(() => {
  const samples = Array.isArray(props.insights.samples) ? props.insights.samples : [];
  return samples.filter((p: any) => Array.isArray(p) && p.length >= 2).length >= 30 ? samples : [];
});

const hasDenseSamples = computed(() => denseSamples.value.length >= 30);

const scattererDistance = computed(() => {
  const given = toNum(props.insights.scatterer_distance);
  if (given > 0.01) return given;
  return haversineKm(
    toNum(props.insights.tx_lng),
    toNum(props.insights.tx_lat),
    toNum(props.insights.scatterer_lon),
    toNum(props.insights.scatterer_lat)
  );
});

const txBarrierDistance = computed(() => toNum(props.insights.tx_barrier_distance));

const txBarrierElev = computed(() => {
  const elev = toNum(props.insights.tx_barrier_elev);
  if (elev > 0) return elev;
  return toNum(props.insights.tx_height) + toNum(props.insights.tx_barrier_height);
});

const rxBarrierElev = computed(() => {
  const elev = toNum(props.insights.rx_barrier_elev);
  if (elev > 0) return elev;
  return toNum(props.insights.rx_height) + toNum(props.insights.rx_barrier_height);
});

const rxBarrierFromStart = computed(() => {
  const total = toNum(props.insights.distance);
  const fromRx = toNum(props.insights.rx_barrier_distance);
  return Math.max(0, total - fromRx);
});

const lossMark = computed(() => {
  const loss = Number(props.insights.median_loss) || 0;
  return Math.min(96, Math.max(4, ((loss - 100) / 200) * 100));
});

const residualMark = computed(() => {
  const residual = Number(props.insights.residual_value) || 0;
  return Math.min(96, Math.max(4, ((residual + 10) / 40) * 100));
});

const reliabilityMark = computed(() => {
  return Math.min(100, Math.max(0, Number(props.insights.reliability) || 0));
});

const fmt = (value: any, digits = 0) => {
  const num = Number(value);
  if (!Number.isFinite(num)) return "--";
  return digits ? num.toFixed(digits) : String(Math.round(num));
};

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 640;
  return {
    x: Math.max(24, Math.round((window.innerWidth - width) / 2)),
    y: Math.max(24, Math.round((window.innerHeight - height) / 2)),
  };
};

const centerPanel = async () => {
  panelPos.value = getDefaultPanelPos();
  await nextTick();
  const el = panelRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  panelPos.value = getDefaultPanelPos({ width: rect.width, height: rect.height });
};

const startDrag = (e: MouseEvent) => {
  if (e.button !== 0) return;
  dragging.value = true;
  dragOffset.value = {
    x: e.clientX - panelPos.value.x,
    y: e.clientY - panelPos.value.y,
  };
  window.addEventListener("mousemove", onDrag);
  window.addEventListener("mouseup", stopDrag);
};

const onDrag = (e: MouseEvent) => {
  if (!dragging.value) return;
  const width = Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(0, window.innerHeight - 80);
  panelPos.value = {
    x: Math.min(maxX, Math.max(0, e.clientX - dragOffset.value.x)),
    y: Math.min(maxY, Math.max(0, e.clientY - dragOffset.value.y)),
  };
};

const stopDrag = () => {
  dragging.value = false;
  window.removeEventListener("mousemove", onDrag);
  window.removeEventListener("mouseup", stopDrag);
};

const disposeChart = () => {
  chart?.dispose();
  chart = null;
};

const renderChart = async () => {
  if (!props.visible || !hasDenseSamples.value) return;
  await nextTick();
  const el = chartRef.value;
  if (!el) return;

  // v-if 关闭对话框会销毁容器，必须重新 init，否则第二次打开是空白
  if (chart && chart.getDom() !== el) {
    disposeChart();
  }
  if (!chart) chart = echarts.init(el);
  if (!chart) return;

  const samples = denseSamples.value;
  const path = [
    [0, toNum(props.insights.tx_height)],
    [txBarrierDistance.value, txBarrierElev.value],
    [scattererDistance.value, toNum(props.insights.scatterer_height)],
    [rxBarrierFromStart.value, rxBarrierElev.value],
    [toNum(props.insights.distance), toNum(props.insights.rx_height)],
  ].filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));

  chart.setOption({
    backgroundColor: "transparent",
    grid: { left: 36, right: 12, top: 16, bottom: 28 },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(26,34,44,0.92)",
      borderColor: "rgba(180,200,220,0.18)",
      textStyle: { color: "#e8e2d2", fontSize: 12 },
      valueFormatter: (v: number) => `${v} m`,
    },
    xAxis: {
      type: "value",
      name: "km",
      nameTextStyle: { color: "#8b8790" },
      axisLine: { lineStyle: { color: "#3a4552" } },
      axisLabel: { color: "#8b8790", fontSize: 10 },
      splitLine: { lineStyle: { color: "rgba(58,69,82,0.55)" } },
    },
    yAxis: {
      type: "value",
      min: 0,
      name: "m",
      nameTextStyle: { color: "#8b8790" },
      axisLine: { lineStyle: { color: "#3a4552" } },
      axisLabel: { color: "#8b8790", fontSize: 10 },
      splitLine: { lineStyle: { color: "rgba(58,69,82,0.55)" } },
    },
    series: [
      {
        name: "高程",
        type: "line",
        data: samples,
        showSymbol: false,
        smooth: false,
        lineStyle: { color: "#7ec8ff", width: 1.8 },
        areaStyle: {
          origin: 0,
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(90,168,255,0.55)" },
              { offset: 0.55, color: "rgba(90,168,255,0.22)" },
              { offset: 1, color: "rgba(90,168,255,0.02)" },
            ],
          },
        },
        z: 1,
      },
      {
        name: "传播路径",
        type: "line",
        data: path,
        showSymbol: false,
        lineStyle: { color: "#c45c4a", width: 1.4 },
        z: 2,
      },
      {
        name: "发射点",
        type: "scatter",
        data: [[0, toNum(props.insights.tx_height)]],
        symbolSize: 8,
        itemStyle: { color: "#5aa8ff" },
        z: 5,
      },
      {
        name: "障碍物",
        type: "scatter",
        data: [
          [txBarrierDistance.value, txBarrierElev.value],
          [rxBarrierFromStart.value, rxBarrierElev.value],
        ],
        symbolSize: 8,
        itemStyle: { color: "#c47a5a" },
        z: 5,
      },
      {
        name: "散射体",
        type: "scatter",
        data: [[scattererDistance.value, toNum(props.insights.scatterer_height)]],
        symbolSize: 9,
        itemStyle: { color: "#e8b52a" },
        z: 5,
      },
      {
        name: "接收点",
        type: "scatter",
        data: [[toNum(props.insights.distance), toNum(props.insights.rx_height)]],
        symbolSize: 8,
        itemStyle: { color: "#5a9e6f" },
        z: 5,
      },
    ],
  }, { notMerge: true });
  chart.resize();
  requestAnimationFrame(() => chart?.resize());
};

watch(
  () => props.visible,
  async (val) => {
    if (val) {
      await centerPanel();
      await renderChart();
    } else {
      disposeChart();
    }
  }
);

watch(
  () => [props.insights, hasDenseSamples.value],
  () => {
    if (props.visible) renderChart();
  },
  { deep: true }
);

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

const handleConfirm = () => {
  emit("confirm");
};

onBeforeUnmount(() => {
  stopDrag();
  disposeChart();
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 1200;
  pointer-events: all;
  box-sizing: border-box;

  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  &__panel {
    width: 100%;
    padding: 22px 24px 20px;
    border-radius: 14px;
    background: rgba(26, 34, 44, 0.72);
    border: 1px solid rgba(180, 200, 220, 0.18);
    box-shadow:
      0 18px 48px rgba(0, 0, 0, 0.38),
      inset 0 1px 0 rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(22px) saturate(1.15);
    -webkit-backdrop-filter: blur(22px) saturate(1.15);
    color: #ffffff;
    overflow: hidden;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    cursor: move;
    user-select: none;
  }

  &__title {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #ffffff;
  }

  &__close {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: rgba(210, 220, 230, 0.75);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 18px;
      height: 18px;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    gap: 12px;
    width: 100%;
  }

  &__footer-left {
    display: flex;
    gap: 10px;
  }

  &__btn {
    border: none;
    cursor: pointer;
    font-size: 12px;
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;

    &--ghost {
      min-width: 72px;
      height: 40px;
      padding: 0 16px;
      border-radius: 8px;
      background: rgba(38, 44, 53, 0.92);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: rgba(235, 240, 245, 0.92);

      &:hover {
        background: rgba(48, 56, 66, 0.95);
      }
    }

    &--primary {
      min-width: 120px;
      height: 44px;
      padding: 0 16px 0 20px;
      border-radius: 999px;
      background: linear-gradient(90deg, #00a2ff 0%, #3b82f6 100%);
      box-shadow: 0 8px 24px rgba(0, 162, 255, 0.38);
      font-weight: 600;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 28px rgba(59, 130, 246, 0.45);
      }
    }
  }

  &__btn-arrow {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.22);
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 14px;
      height: 14px;
    }
  }
}

.insight-card {
  padding: 14px 12px 12px;
  border-radius: 10px;
  background: rgba(18, 24, 31, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.insight-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
  margin-bottom: 16px;
}

.insight-stat {
  display: flex;
  align-items: center;
  gap: 10px;

  &__icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    svg {
      width: 16px;
      height: 16px;
    }

    &.is-tx { color: #5aa8ff; background: rgba(90, 168, 255, 0.16); }
    &.is-peak { color: #b388ff; background: rgba(179, 136, 255, 0.16); }
    &.is-dist { color: #5a9e6f; background: rgba(90, 158, 111, 0.16); }
    &.is-scatter { color: #e8b52a; background: rgba(232, 181, 42, 0.16); }
  }

  &__label {
    font-size: 11px;
    color: rgba(190, 200, 212, 0.72);
  }

  &__value {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    line-height: 1.2;
  }
}

.insight-title {
  margin: 14px 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
}

.insight-chart {
  width: 100%;
  height: 168px;
}

.insight-image {
  width: 100%;
  min-height: 168px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(26, 34, 44, 0.72);

  img {
    display: block;
    width: 100%;
    height: auto;
  }
}

.insight-empty {
  color: rgba(190, 200, 212, 0.7);
  font-size: 12px;
  text-align: center;
  padding: 48px 0;
}

.insight-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 12px;
  margin-top: 8px;
  font-size: 11px;
  color: rgba(190, 200, 212, 0.78);

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
    &.is-elev { background: #7ec8ff; }
    &.is-tx { background: #5aa8ff; }
    &.is-obs { background: #c47a5a; }
    &.is-scatter { background: #e8b52a; }
    &.is-rx { background: #5a9e6f; }
    &.is-ok { background: #5a9e6f; }
    &.is-power { background: #c47a5a; }
  }
}

.insight-points {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 10px;
  font-size: 11px;
  color: rgba(220, 226, 232, 0.86);
}

.insight-heat {
  display: flex;
  flex-direction: column;
  gap: 10px;

  &__row {
    display: grid;
    grid-template-columns: 64px 1fr 72px;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: rgba(220, 226, 232, 0.86);

    em {
      font-style: normal;
      text-align: right;
      color: #fff;
    }
  }

  &__bar {
    position: relative;
    height: 10px;
  }

  &__track {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(90deg, #5a9e6f 0%, #e8b52a 45%, #c45c4a 100%);

    &.is-reverse {
      background: linear-gradient(90deg, #c45c4a 0%, #e8b52a 45%, #5a9e6f 100%);
    }
  }

  &__mark {
    position: absolute;
    top: -2px;
    width: 2px;
    height: 12px;
    background: #fff;
    border-radius: 1px;
    transform: translateX(-1px);
  }
}

.insight-status {
  &__bar {
    height: 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    overflow: hidden;

    i {
      display: block;
      height: 100%;
      background: linear-gradient(90deg, #5a9e6f 0%, #e8b52a 55%, #c45c4a 100%);
    }
  }

  &__scale {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 10px;
    color: rgba(190, 200, 212, 0.6);
  }

  &__legend {
    display: flex;
    gap: 14px;
    margin-top: 8px;
    font-size: 11px;
    color: rgba(220, 226, 232, 0.86);
  }
}

.station-fade-enter-active,
.station-fade-leave-active {
  transition: opacity 0.2s ease;
}

.station-fade-enter-from,
.station-fade-leave-to {
  opacity: 0;
}

:deep(.el-loading-mask) {
  background: rgba(18, 24, 31, 0.55);
}
</style>
