<template>
  <teleport to="body">
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="station-config"
      :class="{ 'is-wide': detailsOpen, 'is-resizing': layoutAnimating }"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <div class="station-config__edge"></div>
        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__heading">
            <div class="station-config__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M4 18h16v2H4zm2-3 4-5 3 4 4-6 3 7H6z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div>
              <h2 class="station-config__title">链路计算</h2>
              <p class="station-config__subtitle">{{ detailsOpen ? "剖面与单链路详情" : "地形剖面与链路质量概览" }}</p>
            </div>
          </div>
          <button
            class="station-config__icon-btn"
            type="button"
            title="关闭"
            @click="setVisible(false)"
            @mousedown.stop
          >
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

        <div class="station-config__body" :class="{ 'is-split': detailsOpen }">
          <section class="insight-card" v-loading="loading">
            <div class="insight-stats">
              <div class="insight-stat">
                <span class="insight-stat__icon is-tx">
                  <svg viewBox="0 0 24 24"><path d="M4 18h16v2H4zm2-3 4-5 3 4 4-6 3 7H6z" fill="currentColor"/></svg>
                </span>
                <div>
                  <div class="insight-stat__label">发射点高程</div>
                  <div class="insight-stat__value">{{ fmt(txHeight) }} m</div>
                </div>
              </div>
              <div class="insight-stat">
                <span class="insight-stat__icon is-peak">
                  <svg viewBox="0 0 24 24"><path d="M3 19 9 9l3 4 4-6 5 12H3z" fill="currentColor"/></svg>
                </span>
                <div>
                  <div class="insight-stat__label">地形最高</div>
                  <div class="insight-stat__value">{{ fmt(maxHeight) }} m</div>
                </div>
              </div>
              <div class="insight-stat">
                <span class="insight-stat__icon is-dist">
                  <svg viewBox="0 0 24 24"><path d="M4 12h16M16 8l4 4-4 4M8 8l-4 4 4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                  <div class="insight-stat__label">通信距离</div>
                  <div class="insight-stat__value">{{ fmt(pathDistance, 2) }} km</div>
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

            <div class="insight-section-head">
              <h3>高程剖面</h3>
            </div>
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

            <div class="insight-section-head">
              <h3>路径要点</h3>
            </div>
            <div class="insight-points">
              <div>发射障碍 {{ fmt(txBarrierDistance, 2) }} km · {{ fmt(txBarrierElev) }} m</div>
              <div>散射体 {{ fmt(scattererDistance, 2) }} km · {{ fmt(insights.scatterer_height) }} m</div>
              <div>接收障碍 {{ fmt(rxBarrierFromStart, 2) }} km · {{ fmt(rxBarrierElev) }} m</div>
              <div>接收点 {{ fmt(pathDistance, 2) }} km · {{ fmt(rxHeight) }} m</div>
            </div>

            <div class="insight-section-head">
              <h3>信号质量</h3>
            </div>
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

            <div class="insight-section-head">
              <h3>链路状态</h3>
            </div>
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

          <aside v-if="detailsOpen" class="insight-details">
            <el-form :model="form" label-position="top" class="insight-details__form">
              <div class="insight-section-head">
                <h3>单链路输入</h3>
              </div>
              <div class="insight-details__grid">
                <el-form-item label="通信速率">
                  <el-select
                    v-model="form.comm_rate"
                    placeholder="请选择"
                    popper-class="station-config-select-dropdown"
                    @change="$emit('changeCommRate', $event)"
                  >
                    <el-option v-for="item in commRateOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
                <el-form-item label="调整系数">
                  <el-input :model-value="display(form.diversity_order)" readonly />
                </el-form-item>
                <el-form-item label="发射天线增益">
                  <el-input :model-value="display(form.tx_gain)" readonly>
                    <template #suffix><span class="insight-details__unit">dB</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收天线增益">
                  <el-input :model-value="display(form.rx_gain)" readonly>
                    <template #suffix><span class="insight-details__unit">dB</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="信号频率">
                  <el-input :model-value="display(form.freq)" readonly>
                    <template #suffix><span class="insight-details__unit">MHz</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射功率">
                  <el-input :model-value="display(form.trans_power)" readonly>
                    <template #suffix><span class="insight-details__unit">W</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射经度">
                  <el-input :model-value="displayLng(form.lng)" readonly />
                </el-form-item>
                <el-form-item label="发射纬度">
                  <el-input :model-value="displayLat(form.lat)" readonly />
                </el-form-item>
                <el-form-item label="接收经度">
                  <el-input :model-value="displayLng(rxLng)" readonly />
                </el-form-item>
                <el-form-item label="接收纬度">
                  <el-input :model-value="displayLat(rxLat)" readonly />
                </el-form-item>
              </div>

              <div class="insight-section-head">
                <h3>单链路输出</h3>
              </div>
              <div class="insight-details__grid">
                <el-form-item label="通信距离">
                  <el-input :model-value="display(form.distance)" readonly>
                    <template #suffix><span class="insight-details__unit">km</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="散射角">
                  <el-input :model-value="display(form.theta_scatter)" readonly>
                    <template #suffix><span class="insight-details__unit">°</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="区域类型">
                  <el-input :model-value="display(form.area)" readonly />
                </el-form-item>
                <el-form-item label="链路传播可靠度">
                  <el-input :model-value="display(form.reliability)" readonly>
                    <template #suffix><span class="insight-details__unit">%</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射天线仰角">
                  <el-input :model-value="display(form.tx_theta)" readonly>
                    <template #suffix><span class="insight-details__unit">°</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射点障碍物距离">
                  <el-input :model-value="display(form.tx_barrier_distance)" readonly>
                    <template #suffix><span class="insight-details__unit">km</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="路径损耗中值">
                  <el-input :model-value="display(form.median_loss)" readonly>
                    <template #suffix><span class="insight-details__unit">dB</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收天线仰角">
                  <el-input :model-value="display(form.rx_theta)" readonly>
                    <template #suffix><span class="insight-details__unit">°</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收点障碍物距离">
                  <el-input :model-value="display(form.rx_barrier_distance)" readonly>
                    <template #suffix><span class="insight-details__unit">km</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收功率">
                  <el-input :model-value="display(form.recv_power)" readonly>
                    <template #suffix><span class="insight-details__unit">dBm</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射天线方位角">
                  <el-input :model-value="display(form.tx_azimuth)" readonly>
                    <template #suffix><span class="insight-details__unit">°</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="发射点障碍物高差">
                  <el-input :model-value="display(form.tx_barrier_height)" readonly>
                    <template #suffix><span class="insight-details__unit">m</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="信号衰落余值">
                  <el-input :model-value="display(form.residual_value)" readonly>
                    <template #suffix><span class="insight-details__unit">dB</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收天线方位角">
                  <el-input :model-value="display(form.rx_azimuth)" readonly>
                    <template #suffix><span class="insight-details__unit">°</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="接收点障碍物高差">
                  <el-input :model-value="display(form.rx_barrier_height)" readonly>
                    <template #suffix><span class="insight-details__unit">m</span></template>
                  </el-input>
                </el-form-item>
              </div>
            </el-form>
          </aside>
        </div>

        <div class="station-config__footer station-config__footer--split">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="$emit('export')">
            导出
          </button>
          <div class="station-config__footer-right">
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="toggleDetails">
              {{ detailsOpen ? "收起" : "详情" }}
            </button>
            <button class="station-config__btn station-config__btn--primary" type="button" @click="setVisible(false)">
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
  </teleport>
</template>

<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts";
import { formatLongitude, formatLatitude } from "@/view/home/service/rules";
import { ECHARTS_CJK_FONT, echartsTextStyle, waitEchartsFonts } from "@/view/home/service/echartsFont";

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
  form: {
    type: Object,
    default: () => ({}),
  },
  rxLng: {
    type: [String, Number],
    default: "",
  },
  rxLat: {
    type: [String, Number],
    default: "",
  },
});

const emit = defineEmits(["update:visible", "export", "changeCommRate"]);

const commRateOptions = [
  "2.4kbps", "9.6kbps", "32kbps", "64kbps", "128kbps", "256kbps", "512kbps",
  "1024kbps", "2Mbps", "4Mbps", "8Mbps", "16Mbps", "34Mbps", "50Mbps",
  "78Mbps", "100Mbps", "155Mbps",
];

const panelRef = ref<HTMLElement | null>(null);
const chartRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const detailsOpen = ref(false);
const layoutAnimating = ref(false);
const PANEL_WIDTH = 800;
const DETAILS_WIDTH = 720;
const LAYOUT_MS = 280;
let layoutAnimTimer: ReturnType<typeof setTimeout> | null = null;
let chart: echarts.ECharts | null = null;
let chartResizeObs: ResizeObserver | null = null;

const currentWidth = () => {
  const width = detailsOpen.value ? PANEL_WIDTH + DETAILS_WIDTH : PANEL_WIDTH;
  return Math.min(width, window.innerWidth - 48);
};

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${currentWidth()}px`,
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

const sampleStats = computed(() => {
  const samples = denseSamples.value;
  if (!samples.length) return { tx: 0, rx: 0, max: 0, dist: 0 };
  const heights = samples.map((p: any) => toNum(p[1]));
  return {
    tx: toNum(samples[0][1]),
    rx: toNum(samples[samples.length - 1][1]),
    max: Math.max(...heights),
    dist: toNum(samples[samples.length - 1][0]),
  };
});

const txHeight = computed(() => toNum(props.insights.tx_height) || sampleStats.value.tx);
const rxHeight = computed(() => toNum(props.insights.rx_height) || sampleStats.value.rx);
const maxHeight = computed(() => toNum(props.insights.max_height) || sampleStats.value.max);
const pathDistance = computed(() => toNum(props.insights.distance) || sampleStats.value.dist);

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
  const total = pathDistance.value;
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

const display = (val: unknown) => (val === null || val === undefined ? "" : String(val));

const displayLng = (val: unknown) => {
  if (val === null || val === undefined || val === "") return "";
  const s = String(val);
  if (/[EW°]/.test(s)) return s;
  return formatLongitude(val as any);
};

const displayLat = (val: unknown) => {
  if (val === null || val === undefined || val === "") return "";
  const s = String(val);
  if (/[NS°]/.test(s)) return s;
  return formatLatitude(val as any);
};

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? currentWidth();
  const height = size?.height ?? 640;
  return {
    x: Math.max(24, Math.round((window.innerWidth - width) / 2)),
    y: Math.max(24, Math.round((window.innerHeight - height) / 2)),
  };
};

const clampPanelPos = () => {
  const width = currentWidth();
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(0, window.innerHeight - 80);
  panelPos.value = {
    x: Math.min(maxX, Math.max(0, panelPos.value.x)),
    y: Math.min(maxY, Math.max(0, panelPos.value.y)),
  };
};

const resizeChart = () => {
  const el = chartRef.value;
  if (!chart || !el) return;
  const width = Math.max(1, el.clientWidth);
  const height = Math.max(1, el.clientHeight);
  chart.resize({ width, height });
};

const unbindChartResize = () => {
  chartResizeObs?.disconnect();
  chartResizeObs = null;
};

const bindChartResize = () => {
  unbindChartResize();
  const el = chartRef.value;
  if (!el || typeof ResizeObserver === "undefined") return;
  chartResizeObs = new ResizeObserver(() => resizeChart());
  chartResizeObs.observe(el);
};

const toggleDetails = () => {
  const next = !detailsOpen.value;
  const nextWidth = Math.min(next ? PANEL_WIDTH + DETAILS_WIDTH : PANEL_WIDTH, window.innerWidth - 48);
  const height = panelRef.value?.offsetHeight || 640;
  const target = getDefaultPanelPos({ width: nextWidth, height });
  if (layoutAnimTimer) {
    clearTimeout(layoutAnimTimer);
    layoutAnimTimer = null;
  }
  layoutAnimating.value = true;
  requestAnimationFrame(() => {
    detailsOpen.value = next;
    panelPos.value = target;
  });
  layoutAnimTimer = window.setTimeout(() => {
    layoutAnimating.value = false;
    layoutAnimTimer = null;
    resizeChart();
  }, LAYOUT_MS);
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
  layoutAnimating.value = false;
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
  const width = currentWidth();
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
  unbindChartResize();
  chart?.dispose();
  chart = null;
};

const renderChart = async () => {
  if (!props.visible || !hasDenseSamples.value) return;
  await waitEchartsFonts();
  await nextTick();
  const el = chartRef.value;
  if (!el) return;

  // SVG 用页面 CSS 字体回退，避免 Canvas 在 Linux/未加载完的 Noto 子集上画出方框
  if (chart) disposeChart();
  chart = echarts.init(el, undefined, {
    renderer: "svg",
    width: Math.max(1, el.clientWidth),
    height: Math.max(1, el.clientHeight),
  });
  bindChartResize();
  if (!chart) return;

  const samples = denseSamples.value;
  const path = [
    [0, txHeight.value],
    [txBarrierDistance.value, txBarrierElev.value],
    [scattererDistance.value, toNum(props.insights.scatterer_height)],
    [rxBarrierFromStart.value, rxBarrierElev.value],
    [pathDistance.value, rxHeight.value],
  ].filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));

  const axisText = { color: "#8b8790", fontFamily: ECHARTS_CJK_FONT };

  chart.setOption({
    backgroundColor: "transparent",
    textStyle: echartsTextStyle,
    title: {
      text: "高程剖面",
      left: "center",
      top: 4,
      textStyle: { color: "#c0c8c3", fontSize: 12, fontWeight: 500, fontFamily: ECHARTS_CJK_FONT },
    },
    legend: {
      show: true,
      top: 22,
      left: 100,
      itemWidth: 10,
      itemHeight: 8,
      itemGap: 10,
      textStyle: { color: "#c0c8c3", fontSize: 11, fontFamily: ECHARTS_CJK_FONT },
      data: ["高程", "发射点", "障碍物", "散射体", "接收点"],
    },
    grid: { left: 52, right: 16, top: 52, bottom: 32 },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(26,34,44,0.92)",
      borderColor: "rgba(180,200,220,0.18)",
      textStyle: { color: "#e8e2d2", fontSize: 12, fontFamily: ECHARTS_CJK_FONT },
      valueFormatter: (v: number) => `${v} m`,
    },
    xAxis: {
      type: "value",
      name: "距离 (km)",
      nameTextStyle: axisText,
      axisLine: { lineStyle: { color: "#3a4552" } },
      axisLabel: { ...axisText, fontSize: 10 },
      splitLine: { lineStyle: { color: "rgba(58,69,82,0.55)" } },
    },
    yAxis: {
      type: "value",
      min: 0,
      name: "高程 (m)",
      nameLocation: "end",
      nameGap: 8,
      nameTextStyle: { ...axisText, align: "left" },
      axisLine: { lineStyle: { color: "#3a4552" } },
      axisLabel: { ...axisText, fontSize: 10 },
      splitLine: { lineStyle: { color: "rgba(58,69,82,0.55)" } },
    },
    series: [
      {
        name: "高程",
        type: "line",
        data: samples,
        showSymbol: false,
        smooth: false,
        lineStyle: { color: "#bef264", width: 1.8 },
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
        data: [[0, txHeight.value]],
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
        data: [[pathDistance.value, rxHeight.value]],
        symbolSize: 8,
        itemStyle: { color: "#5a9e6f" },
        z: 5,
      },
    ],
  }, { notMerge: true });
  resizeChart();
  bindChartResize();
};

watch(
  () => props.visible,
  async (val) => {
    if (val) {
      detailsOpen.value = false;
      await centerPanel();
      await renderChart();
    } else {
      detailsOpen.value = false;
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

onBeforeUnmount(() => {
  if (layoutAnimTimer) clearTimeout(layoutAnimTimer);
  stopDrag();
  disposeChart();
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 2400;
  width: min(800px, calc(100vw - 48px));
  pointer-events: all;
  box-sizing: border-box;
  transition: none;

  &.is-wide {
    width: min(1520px, calc(100vw - 48px));
  }

  &.is-resizing {
    transition: width 0.28s ease, left 0.28s ease, top 0.28s ease;
  }

  &__panel {
    position: relative;
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 48px);
    padding: 0;
    overflow: hidden;
    border-radius: 0.75rem;
    background: rgba(12, 21, 16, 0.85);
    border: 1px solid rgba(64, 73, 69, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    color: #dae5dc;
    box-sizing: border-box;
  }

  &__edge {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.1), transparent);
    pointer-events: none;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(64, 73, 69, 0.2);
    background: rgba(45, 55, 49, 0.5);
    cursor: move;
    user-select: none;
    flex-shrink: 0;
  }

  &__heading {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
    flex: 1;
  }

  &__badge {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 9999px;
    background: rgba(45, 90, 76, 0.3);
    border: 1px solid rgba(161, 209, 191, 0.2);
    color: #a1d1bf;

    svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }
  }

  &__title {
    margin: 0;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    line-height: 32px;
    color: #ffffff !important;
    white-space: nowrap;
  }

  &__subtitle {
    margin: 4px 0 0;
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 20px;
    color: #c0c8c3 !important;
    white-space: nowrap;
  }

  &__icon-btn {
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
      flex-shrink: 0;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
  }

  &__body {
    flex: 1 1 auto;
    min-height: 0;
    padding: 20px 24px;
    max-height: min(70vh, 720px);
    overflow-x: hidden;
    overflow-y: auto;

    &.is-split {
      display: flex;
      align-items: stretch;
      gap: 0;
      padding: 0;
      height: min(76vh, 820px);
      max-height: min(76vh, 820px);
      overflow: hidden;
    }
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    flex: 0 0 auto !important;
    width: 100%;
    box-sizing: border-box;
    margin: 0 !important;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(64, 73, 69, 0.2) !important;
    background: rgba(45, 55, 49, 0.3) !important;

    &--split {
      justify-content: space-between;
    }
  }

  &__footer-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  &__btn {
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    white-space: nowrap;
    transition: all 0.2s ease;

    svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    &--ghost {
      min-width: 88px;
      padding: 10px 20px;
      border-radius: 0.5rem;
      background: transparent;
      border: 1px solid #404945;
      color: #c0c8c3 !important;
      font-weight: 500;

      &:hover {
        color: #ffffff !important;
        background: rgba(45, 55, 49, 0.5);
      }
    }

    &--primary {
      min-width: 120px;
      padding: 10px 28px;
      border-radius: 0.5rem;
      background: #9ddf2e;
      color: #213600 !important;
      font-weight: 700;
      gap: 8px;
      box-shadow: 0 0 20px rgba(157, 223, 46, 0.4);

      &:hover {
        background: #b2f746;
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(157, 223, 46, 0.6);
      }
    }
  }
}

.insight-card {
  padding: 0;
  background: transparent;
  border: none;
  max-width: 100%;
  overflow-x: hidden;
}

.station-config__body.is-split .insight-card {
  flex: 1 1 760px;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
  padding: 20px 24px;
  overflow-x: hidden;
  overflow-y: auto;
  box-sizing: border-box;
}

.insight-details {
  flex: 1 1 640px;
  width: auto;
  min-width: 420px;
  max-width: 760px;
  min-height: 0;
  padding: 20px 24px 28px;
  overflow-x: hidden;
  overflow-y: auto;
  border-left: 1px solid rgba(64, 73, 69, 0.28);
  background: rgba(7, 16, 11, 0.35);
  box-sizing: border-box;
  scrollbar-gutter: stable;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(157, 223, 46, 0.55);
    border-radius: 999px;
  }

  &__form {
    :deep(.el-form-item) {
      margin-bottom: 10px;
    }

    :deep(.el-form-item__label) {
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 12px !important;
      font-weight: 500 !important;
      line-height: 16px;
      color: #c0c8c3 !important;
      margin-bottom: 4px;
    }

    :deep(.el-input__wrapper),
    :deep(.el-select__wrapper) {
      background: #07100b;
      box-shadow: none;
      border: 1px solid rgba(64, 73, 69, 0.55);
      border-radius: 8px;
    }

    :deep(.el-input__inner),
    :deep(.el-select__selected-item) {
      color: #ffffff;
      font-size: 12px;
    }

    :deep(.el-input.is-disabled .el-input__wrapper) {
      background: #07100b;
    }
  }

  &__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 16px;
  }

  &__unit {
    color: #8b8790;
    font-size: 11px;
  }
}

.insight-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.insight-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 0.5rem;
  background: #07100b;
  border: 1px solid rgba(64, 73, 69, 0.5);

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
      flex-shrink: 0;
    }

    &.is-tx { color: #5aa8ff; background: rgba(90, 168, 255, 0.16); }
    &.is-peak { color: #b388ff; background: rgba(179, 136, 255, 0.16); }
    &.is-dist { color: #9ddf2e; background: rgba(157, 223, 46, 0.12); }
    &.is-scatter { color: #e8b52a; background: rgba(232, 181, 42, 0.16); }
  }

  &__label {
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 11px;
    font-weight: 500;
    color: #c0c8c3;
  }

  &__value {
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    line-height: 1.2;
  }
}

.insight-section-head {
  display: flex;
  align-items: center;
  margin: 18px 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(64, 73, 69, 0.2);

  h3 {
    margin: 0;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    line-height: 16px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #ffffff !important;
  }
}

.insight-chart {
  width: 100%;
  max-width: 100%;
  height: 220px;
  border-radius: 0.5rem;
  background: #07100b;
  border: 1px solid rgba(64, 73, 69, 0.5);
  overflow: hidden;
  box-sizing: border-box;
  font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", "Noto Sans SC", sans-serif;

  :deep(text) {
    font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", "Noto Sans SC", sans-serif !important;
  }

  :deep(> div) {
    width: 100% !important;
    height: 100% !important;
    overflow: hidden;
  }
}

.insight-image {
  width: 100%;
  min-height: 180px;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #07100b;
  border: 1px solid rgba(64, 73, 69, 0.5);

  img {
    display: block;
    width: 100%;
    height: auto;
  }
}

.insight-empty {
  color: #c0c8c3;
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-size: 13px;
  text-align: center;
  padding: 56px 0;
}

.insight-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  margin-top: 10px;
  max-width: 100%;
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-size: 11px;
  color: #c0c8c3;

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
    &.is-elev { background: #bef264; }
    &.is-tx { background: #5aa8ff; }
    &.is-obs { background: #c47a5a; }
    &.is-scatter { background: #e8b52a; }
    &.is-rx { background: #5a9e6f; }
    &.is-ok { background: #9ddf2e; }
    &.is-power { background: #c47a5a; }
  }
}

.insight-points {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-size: 13px;
  color: #dae5dc;
}

.insight-heat {
  display: flex;
  flex-direction: column;
  gap: 12px;

  &__row {
    display: grid;
    grid-template-columns: 72px minmax(0, 1fr) 80px;
    align-items: center;
    gap: 10px;
    min-width: 0;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 12px;
    color: #c0c8c3;

    em {
      font-style: normal;
      text-align: right;
      color: #ffffff;
      white-space: nowrap;
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
    font-family: Inter, sans-serif;
    font-size: 10px;
    color: rgba(192, 200, 195, 0.7);
  }

  &__legend {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 10px;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 12px;
    color: #dae5dc;
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
  background: rgba(12, 21, 16, 0.55);
}
</style>
