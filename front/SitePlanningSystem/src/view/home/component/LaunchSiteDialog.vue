<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="station-config"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <div class="station-config__edge"></div>
        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__heading">
            <div class="station-config__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div>
              <h2 class="station-config__title">站点配置</h2>
              <p class="station-config__subtitle">Configure node parameters for propagation modeling.</p>
            </div>
          </div>
          <div class="station-config__header-actions">
            <button class="station-config__reset" type="button" title="重置" @click="handleReset" @mousedown.stop>
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M7.2 7.2a6.8 6.8 0 1 1 0 9.6"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
                <path
                  d="M7.2 3.8v4.2H11.4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              重置
            </button>
            <button class="station-config__icon-btn station-config__icon-btn--close" type="button" title="关闭" @click="setVisible(false)" @mousedown.stop>
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
        </div>

        <el-form
          ref="launchSiteForm"
          :model="drawLaunchSiteForm"
          :rules="rules"
          label-position="top"
          class="station-config__form"
          require-asterisk-position="right"
          :show-message="false"
        >
          <div class="station-config__body">
          <div class="station-config__columns">
            <!-- 基本设置 -->
            <section class="station-config__card">
              <div class="station-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <h3>Site Info</h3>
              </div>

              <el-form-item class="station-config__name-item" label="站点名称" prop="point_name">
                <el-input v-model="drawLaunchSiteForm.point_name" placeholder="请输入站点名称" />
              </el-form-item>

              <div class="station-config__coord-row">
                <el-form-item label="经度" prop="lng">
                  <el-input v-model="drawLaunchSiteForm.lng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="纬度" prop="lat">
                  <el-input v-model="drawLaunchSiteForm.lat" placeholder="请输入" />
                </el-form-item>
              </div>

              <button
                class="station-config__map-pick"
                type="button"
                @click="drawPoint('LaunchSite')"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图选点</span>
              </button>

              <el-form-item label="气候区选择" prop="climate_num">
                <div class="station-config__climate-pills">
                  <button
                    v-for="opt in climateOptions"
                    :key="`pill-${opt.value}`"
                    type="button"
                    class="station-config__pill"
                    :class="{ 'is-active': drawLaunchSiteForm.climate_num === opt.value }"
                    @click="drawLaunchSiteForm.climate_num = opt.value"
                  >
                    <span v-if="drawLaunchSiteForm.climate_num === opt.value" class="station-config__pill-dot" />
                    <span class="station-config__pill-text">{{ opt.label }}</span>
                  </button>
                </div>
              </el-form-item>
            </section>

            <!-- 无线电参数 -->
            <section class="station-config__card">
              <div class="station-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="12" cy="18.2" r="1.4" fill="currentColor" />
                  <path
                    d="M8.2 15.4a5.4 5.4 0 0 1 7.6 0M5.6 12.8a9 9 0 0 1 12.8 0M3.4 10.2a12.4 12.4 0 0 1 17.2 0"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <h3>Radio Parameters</h3>
              </div>

              <el-form-item class="station-config__freq-item" prop="freq">
                <div class="station-config__freq">
                  <div class="station-config__freq-head">
                    <span class="station-config__freq-label">
                      信号频率<span class="station-config__req">*</span>
                    </span>
                    <span class="station-config__freq-value">{{ freqGhzLabel }} GHz</span>
                  </div>
                  <el-slider
                    :model-value="freqSliderValue"
                    :min="FREQ_MIN_MHZ"
                    :max="FREQ_MAX_MHZ"
                    :step="FREQ_STEP_MHZ"
                    :show-tooltip="false"
                    @update:model-value="onFreqSlider"
                  />
                  <div class="station-config__freq-ends">
                    <span>4.4</span>
                    <span>5.0</span>
                  </div>
                </div>
              </el-form-item>

              <el-form-item label="发射功率" prop="trans_power">
                <el-input v-model="drawLaunchSiteForm.trans_power" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">W</span>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="通信速率" prop="comm_rate">
                <el-select
                  v-model="drawLaunchSiteForm.comm_rate"
                  placeholder="请选择"
                  popper-class="station-config-select-dropdown"
                >
                  <el-option label="2.4kbps" value="2.4kbps" />
                  <el-option label="9.6kbps" value="9.6kbps" />
                  <el-option label="32kbps" value="32kbps" />
                  <el-option label="64kbps" value="64kbps" />
                  <el-option label="128kbps" value="128kbps" />
                  <el-option label="256kbps" value="256kbps" />
                  <el-option label="512kbps" value="512kbps" />
                  <el-option label="1024kbps" value="1024kbps" />
                  <el-option label="2Mbps" value="2Mbps" />
                  <el-option label="4Mbps" value="4Mbps" />
                  <el-option label="8Mbps" value="8Mbps" />
                  <el-option label="16Mbps" value="16Mbps" />
                  <el-option label="34Mbps" value="34Mbps" />
                  <el-option label="50Mbps" value="50Mbps" />
                  <el-option label="78Mbps" value="78Mbps" />
                  <el-option label="100Mbps" value="100Mbps" />
                  <el-option label="155Mbps" value="155Mbps" />
                </el-select>
              </el-form-item>

              <el-form-item label="调整系数" prop="diversity_order">
                <el-input v-model="drawLaunchSiteForm.diversity_order" placeholder="请输入" />
              </el-form-item>
            </section>

            <!-- 天线参数 -->
            <section class="station-config__card">
              <div class="station-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 20.2V10.2M7.2 13.2a6.2 6.2 0 0 1 9.6 0M5 10.4a9.2 9.2 0 0 1 14 0"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                  <path d="M9.2 20.2h5.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
                </svg>
                <h3>Antenna Specs</h3>
              </div>

              <el-form-item label="发射天线增益" prop="tx_gain">
                <el-input v-model="drawLaunchSiteForm.tx_gain" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">dB</span>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="接收天线增益" prop="rx_gain">
                <el-input v-model="drawLaunchSiteForm.rx_gain" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">dB</span>
                  </template>
                </el-input>
              </el-form-item>
            </section>
          </div>
          </div>
        </el-form>

        <div class="station-config__footer">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button class="station-config__btn station-config__btn--primary" type="button" @click="handleConfirmVisible(launchSiteForm)">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M5.4 12.4 10 17l8.6-9.2"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            确认
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck

import { computed, getCurrentInstance, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { validateLongitude, validateLatitude, parseLongitude, parseLatitude, formatLongitude, formatLatitude } from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const climateOptions = [
  { label: "自动选择", value: "" },
  { label: "海洋气候区", value: "0" },
  { label: "赤道气候区", value: "1" },
  { label: "大陆性亚热带气候区", value: "2" },
  { label: "海洋性亚热带气候区", value: "3" },
  { label: "沙漠气候区", value: "4" },
  { label: "大陆性温带气候区", value: "5" },
  { label: "海洋性温带陆地气候区", value: "6" },
];

const FREQ_MIN_MHZ = 4400;
const FREQ_MAX_MHZ = 5000;
const FREQ_STEP_MHZ = 10;

const rules = ref({
  diversity_order: [{ required: true, message: "请输入调整系数", trigger: "change" }],
  tx_gain: [{ required: true, message: "请输入发射天线增益", trigger: "change" }],
  rx_gain: [{ required: true, message: "请输入接收天线增益", trigger: "change" }],
  freq: [{ required: true, message: "请选择信号频率", trigger: "change" }],
  trans_power: [{ required: true, message: "请输入发射功率", trigger: "change" }],
  point_name: [{ required: true, message: "请输入站点名称", trigger: "change" }],
  comm_rate: [{ required: true, message: "请选择通信速率", trigger: "change" }],
  lng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  lat: [{ required: true, validator: validateLatitude, trigger: "change" }],
});

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  drawLaunchSiteForm: {
    type: Object,
    default: () => ({
      name: "",
      diversity_order: "8",
      tx_gain: "38",
      rx_gain: "38",
      freq: "4700",
      trans_power: "400",
      lng: "11.2345°\u00A0E",
      lat: "45.8321°\u00A0N",
      height: 10,
      point_name: "",
      comm_rate: "2.4kbps",
      climate_num: "",
    }),
  },
});

const emit = defineEmits(["update:visible", "update:drawLaunchSiteForm", "update:isSelectStartPointOver"]);

const parseFreqMhz = () => {
  const n = Number(props.drawLaunchSiteForm.freq);
  return Number.isFinite(n) ? n : 4700;
};

const freqSliderValue = computed(() => {
  const n = parseFreqMhz();
  return Math.min(FREQ_MAX_MHZ, Math.max(FREQ_MIN_MHZ, n));
});

const freqGhzLabel = computed(() => (parseFreqMhz() / 1000).toFixed(1));

const onFreqSlider = (val: number) => {
  props.drawLaunchSiteForm.freq = String(val);
};

const launchSiteForm = ref(null);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 1120;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
}));

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 480;
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
  const width = Math.min(1080, window.innerWidth - 48);
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

watch(
  () => props.visible,
  (val) => {
    if (val) centerPanel();
  }
);

const handleConfirmVisible = async (formEl) => {
  if (!formEl) return;
  await formEl.validate((valid) => {
    if (valid) {
      $bus.emit("setLaunchSite", {
        type: "LaunchSite",
        lng: parseLongitude(props.drawLaunchSiteForm.lng),
        lat: parseLatitude(props.drawLaunchSiteForm.lat),
        height: props.drawLaunchSiteForm.height,
      });
      emit("update:visible", false);
      emit("update:isSelectStartPointOver", true);
    } else {
      shakeInvalidFormFields(formEl);
    }
  });
};

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

const pendingPickRestore = ref(false);
let pickEscHandler: ((e: KeyboardEvent) => void) | null = null;

const cleanupPickMode = () => {
  if (pickEscHandler) {
    window.removeEventListener("keydown", pickEscHandler);
    pickEscHandler = null;
  }
};

const finishPickMode = () => {
  if (!pendingPickRestore.value) return;
  pendingPickRestore.value = false;
  cleanupPickMode();
  setVisible(true);
};

const onDrawPointEnd = (payload: { type?: string }) => {
  if (payload?.type && payload.type !== "LaunchSite") return;
  finishPickMode();
};

const handleReset = () => {
  Object.assign(props.drawLaunchSiteForm, {
    name: "",
    diversity_order: "8",
    tx_gain: "38",
    rx_gain: "38",
    freq: "4700",
    trans_power: "400",
    lng: "11.2345°\u00A0E",
    lat: "45.8321°\u00A0N",
    height: 10,
    point_name: "",
    comm_rate: "2.4kbps",
    climate_num: "",
  });
  launchSiteForm.value?.clearValidate?.();
};

const drawPoint = (type: any) => {
  pendingPickRestore.value = true;
  setVisible(false);

  const onEsc = (e: KeyboardEvent) => {
    if (e.key !== "Escape") return;
    $bus.emit("cancelDrawPoint");
    finishPickMode();
  };
  pickEscHandler = onEsc;
  window.addEventListener("keydown", onEsc);

  $bus.emit("drawPoint", { type, name: props.drawLaunchSiteForm.point_name });
};

watch(
  () => props.drawLaunchSiteForm.point_name,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      $bus.emit("setLaunchSiteName", {
        type: "LaunchSite",
        point_name: newVal,
      });
    }
  }
);

const updateLaunchSiteData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.name === "LaunchSite") {
    props.drawLaunchSiteForm.lng = formatLongitude(graphic.point.lng);
    props.drawLaunchSiteForm.lat = formatLatitude(graphic.point.lat);
    props.drawLaunchSiteForm.height = graphic.point.alt;
  }
};

$bus.on("drawPointMsg", updateLaunchSiteData);
$bus.on("drawPointEnd", onDrawPointEnd);

const setLaunchSitePosition = (position: any) => {
  props.drawLaunchSiteForm.lng = formatLongitude(position.lng);
  props.drawLaunchSiteForm.lat = formatLatitude(position.lat);
  props.drawLaunchSiteForm.height = position.alt;
};
$bus.on("changeSingleLinkPoint", setLaunchSitePosition);

onBeforeUnmount(() => {
  stopDrag();
  cleanupPickMode();
  $bus.off("drawPointMsg", updateLaunchSiteData);
  $bus.off("drawPointEnd", onDrawPointEnd);
  $bus.off("changeSingleLinkPoint", setLaunchSitePosition);
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 1200;
  width: min(1120px, calc(100vw - 48px));
  box-sizing: border-box;
  pointer-events: all;
  /* 非模态浮层：不遮罩地球，可拖动标题栏 */

  &__panel {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0;
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
  }

  &__badge {
    width: 32px;
    height: 32px;
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
    }
  }

  &__title {
    margin: 0;
    font-family: Inter, sans-serif !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    line-height: 32px;
    letter-spacing: 0;
    color: #ffffff !important;
    word-break: normal;
  }

  &__subtitle {
    margin: 4px 0 0;
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 20px;
    color: #c0c8c3 !important;
    word-break: normal;
  }

  &__header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__reset {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    height: 32px;
    padding: 0 8px;
    border: none;
    border-radius: 0.375rem;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, sans-serif !important;
    font-size: 12px !important;
    font-weight: 500;
    line-height: 1;
    word-break: normal;
    cursor: pointer;

    svg {
      width: 14px;
      height: 14px;
    }

    &:hover {
      background: #2d3731;
      color: #dae5dc;
    }
  }

  &__icon-btn {
    width: 32px;
    height: 32px;
    padding: 6px;
    border: none;
    border-radius: 0.375rem;
    background: transparent;
    color: #c0c8c3;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 16px;
      height: 16px;
    }

    &:hover {
      background: #2d3731;
      color: #dae5dc;
    }

    &--close:hover {
      background: #93000a;
      color: #ffdad6;
    }
  }

  &__columns {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 24px;
    align-items: start;
    width: 100%;
    min-width: 0;
    box-sizing: border-box;
  }

  &__form {
    display: block !important;
    width: 100%;
    max-width: 100%;
    height: auto !important;
    flex: 0 0 auto !important;
    overflow: visible !important;
    margin: 0;
    padding: 24px;
    box-sizing: border-box;
  }

  &__body {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  &__card {
    padding: 0;
    border-radius: 0;
    background: transparent;
    border: none;
    min-width: 0;
    min-height: 0;
    height: auto;
    overflow: visible;
  }

  &__section-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(64, 73, 69, 0.2);
    color: #99d4ae;

    svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    h3 {
      margin: 0;
      font-family: Inter, sans-serif !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      line-height: 16px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #ffffff !important;
      word-break: normal;
    }
  }

  /* Match code.html Site Designation / Latitude / Longitude field widths */
  &__name-item {
    /* 与经纬度两框+间距对齐：132 + 12 + 132 */
    width: 276px !important;
    max-width: 276px !important;

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: 276px !important;
      max-width: 276px !important;
    }
  }

  &__coord-row {
    /* code.html Latitude/Longitude: ~114×41.6, bg #07100b, px-3 py-2, border-outline-variant/50, rounded-lg */
    --coord-h: 42px;
    --coord-w: 132px;
    display: grid;
    grid-template-columns: var(--coord-w) var(--coord-w);
    align-items: start;
    column-gap: 12px;
    width: max-content !important;
    max-width: 100%;
    margin-bottom: 10px;

    :deep(.el-form-item) {
      margin-bottom: 0 !important;
      width: var(--coord-w) !important;
      max-width: var(--coord-w) !important;
    }

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: var(--coord-w) !important;
      max-width: var(--coord-w) !important;
      line-height: normal;
    }

    :deep(.el-input),
    :deep(.el-input__wrapper) {
      height: var(--coord-h) !important;
      min-height: var(--coord-h) !important;
      max-height: var(--coord-h) !important;
    }

    :deep(.el-input__wrapper) {
      box-sizing: border-box !important;
      padding: 8px 12px !important;
      background: #07100b !important;
      background-color: #07100b !important;
      border: 1px solid rgba(64, 73, 69, 0.5) !important;
      outline: 1px solid rgba(64, 73, 69, 0.5);
      outline-offset: -1px;
      border-radius: 0.5rem !important;
      box-shadow: none !important;
    }

    :deep(.el-input__wrapper.is-focus),
    :deep(.el-input__wrapper.is-focus:hover) {
      border-color: #9ddf2e !important;
      border-width: 2px !important;
      outline: none !important;
      box-shadow: none !important;
      background: #07100b !important;
    }

    :deep(.el-input__inner) {
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 16px !important;
      font-weight: 400 !important;
      line-height: 20px !important;
      color: #ffffff !important;
      height: 100% !important;
      white-space: pre !important;
      word-break: keep-all !important;
      letter-spacing: 0 !important;
    }
  }

  /* code.html dashed terrain add pill */
  &__map-pick {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-sizing: border-box;
    height: 24px;
    margin: 0 0 16px;
    padding: 0 14px;
    border-radius: 9999px;
    border: 1px dashed #8a938e;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    line-height: 1 !important;
    cursor: pointer;
    transition: border-color 0.15s ease, color 0.15s ease, background-color 0.15s ease;

    svg {
      width: 14px;
      height: 14px;
      flex-shrink: 0;
    }

    span {
      transform: translateY(1px);
    }

    &:hover {
      border-color: #dae5dc;
      color: #dae5dc;
      background: rgba(45, 55, 49, 0.35);
    }
  }

  &__unit {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 20px !important;
    color: #a1d1bf !important;
    pointer-events: none;
    user-select: none;
    white-space: nowrap;
  }

  /* code.html Terrain pills: px-2.5 py-1 rounded-full font-label-sm 11px */
  &__climate-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0;
    width: 100%;
  }

  &__pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    height: 24px;
    margin: 0;
    padding: 0 14px;
    border-radius: 9999px;
    border: 1px solid #404945;
    background: #18221c;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    line-height: 1 !important;
    cursor: pointer;
    vertical-align: middle;
    gap: 4px;
    transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;

    &:hover {
      border-color: #8a938e;
      color: #dae5dc;
    }

    &.is-active {
      border-color: rgba(157, 223, 46, 0.4);
      background: rgba(157, 223, 46, 0.1);
      color: #9ddf2e;
    }
  }

  &__pill-dot {
    display: block;
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: #9ddf2e;
    flex-shrink: 0;
  }

  &__pill-text {
    display: block;
    font: inherit !important;
    color: inherit !important;
    line-height: 1 !important;
    /* 中文相对圆点视觉偏上，略下移对齐 */
    transform: translateY(1px);
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    flex: 0 0 auto !important;
    width: 100%;
    box-sizing: border-box;
    position: static !important;
    inset: auto !important;
    z-index: auto !important;
    margin: 0 !important;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(64, 73, 69, 0.2) !important;
    background: rgba(45, 55, 49, 0.3) !important;
    box-shadow: none !important;
    clear: both;
  }

  &__footer-left,
  &__footer-right {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }

  &__btn {
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
    line-height: 20px;
    word-break: normal;
    transition: all 0.2s ease;

    svg {
      width: 16px;
      height: 16px;
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
      padding: 10px 32px;
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

  &__freq-item {
    :deep(.el-form-item__label) {
      display: none !important;
      height: 0 !important;
      margin: 0 !important;
    }
  }

  &__freq {
    width: 100%;
    padding: 2px 2px 0;
  }

  &__freq-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
  }

  &__freq-label {
    font-family: Inter, sans-serif;
    color: #ffffff;
    font-size: 11px;
    font-weight: 500;
    line-height: 14px;
    white-space: nowrap;
  }

  &__req {
    margin-left: 2px;
    color: #ffb4ab;
  }

  &__freq-value {
    color: #9ddf2e;
    font-family: Inter, "IBM Plex Mono", sans-serif;
    font-size: 13px;
    font-weight: 600;
    line-height: 16px;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }

  &__freq-ends {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2px;
    color: #c0c8c3;
    font-family: Inter, sans-serif;
    font-size: 11px;
    line-height: 14px;
  }

  :deep(.station-config__freq .el-slider) {
    --el-slider-main-bg-color: transparent;
    --el-slider-runway-bg-color: rgba(180, 200, 220, 0.18);
    --el-slider-button-size: 14px;
    --el-slider-height: 4px;
    --el-slider-button-wrapper-size: 28px;
    --el-slider-button-wrapper-offset: -12px;
    height: 28px;
  }

  :deep(.station-config__freq .el-slider__runway) {
    background: rgba(180, 200, 220, 0.18);
  }

  :deep(.station-config__freq .el-slider__bar) {
    background: transparent;
  }

  :deep(.station-config__freq .el-slider__button) {
    border: none;
    background: #9ddf2e;
    box-shadow: 0 0 10px rgba(157, 223, 46, 0.45);
  }

  :deep(.station-config__freq .el-slider__button-wrapper) {
    top: -12px;
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;

    &:not(.station-config__name-item) {
      width: 100%;
      max-width: 100%;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(.el-form-item__label) {
    font-family: Inter, sans-serif !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    line-height: 14px;
    height: 20px;
    width: auto !important;
    max-width: 100% !important;
    margin-bottom: 6px !important;
    padding: 0;
    justify-content: flex-start;
    word-break: normal;
    white-space: nowrap;
  }

  :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
  :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
    color: #ffb4ab !important;
  }

  /* Match 调整系统 / gotham-panel edit borders:
     default rgba(180,200,220,0.18); focus pea-green like code.html */
  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-select__wrapper),
  :deep(.station-config__form .el-input .el-input__wrapper),
  :deep(.station-config__form .el-select .el-select__wrapper) {
    background: #07100b !important;
    background-color: #07100b !important;
    background-image: none !important;
    --el-input-bg-color: #07100b;
    --el-fill-color-blank: #07100b;
    --el-input-border-color: rgba(180, 200, 220, 0.18);
    --el-border-color: rgba(180, 200, 220, 0.18);
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    outline: 1px solid rgba(180, 200, 220, 0.18);
    outline-offset: -1px;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 40px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease, outline-color 0.15s ease;
  }

  :deep(.station-config__form .el-input),
  :deep(.station-config__form .el-select) {
    --el-input-bg-color: #07100b;
    --el-fill-color-blank: #07100b;
    --el-input-border-color: rgba(180, 200, 220, 0.18);
  }

  :deep(.station-config__form .el-input__wrapper:hover),
  :deep(.station-config__form .el-select__wrapper:hover) {
    border-color: rgba(180, 200, 220, 0.32) !important;
    outline-color: rgba(180, 200, 220, 0.32);
    box-shadow: none !important;
    background: #07100b !important;
    background-color: #07100b !important;
  }

  :deep(.station-config__form .el-input__wrapper.is-focus),
  :deep(.station-config__form .el-select__wrapper.is-focused),
  :deep(.station-config__form .el-input__wrapper.is-focus:hover),
  :deep(.station-config__form .el-select__wrapper.is-focused:hover) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    outline: none !important;
    box-shadow: none !important;
    background: #07100b !important;
    background-color: #07100b !important;
    background-image: none !important;
  }

  /* 与经纬度一致：Inter 16px */
  :deep(.station-config__form .el-input__inner),
  :deep(.station-config__form .el-select__placeholder),
  :deep(.station-config__form .el-select__selected-item),
  :deep(.station-config__form .el-select__wrapper),
  :deep(.station-config__form .el-input),
  :deep(.station-config__form .el-input__wrapper) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    line-height: 20px !important;
  }

  :deep(.station-config__form .el-input__inner),
  :deep(.station-config__form .el-select__placeholder),
  :deep(.station-config__form .el-select__selected-item) {
    color: #dae5dc !important;
    word-break: normal !important;
    user-select: text !important;
    -webkit-user-select: text !important;
  }

  :deep(.station-config__form .el-input__inner::selection),
  :deep(.station-config__form input::selection) {
    background: #9ddf2e !important;
    color: #213600 !important;
  }

  :deep(.station-config__form .el-input__inner::-moz-selection),
  :deep(.station-config__form input::-moz-selection) {
    background: #9ddf2e !important;
    color: #213600 !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder),
  :deep(.station-config__form .el-select__placeholder.is-transparent) {
    color: rgba(192, 200, 195, 0.7) !important;
  }

  :deep(.station-config__form .el-select__caret),
  :deep(.station-config__form .el-input__suffix) {
    color: #c0c8c3 !important;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper),
  :deep(.station-config__form .el-form-item.is-error .el-select__wrapper) {
    border-color: #ffb4ab !important;
    box-shadow: none !important;
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

@media (max-width: 960px) {
  .station-config__columns {
    grid-template-columns: 1fr;
  }

  .station-config__footer {
    justify-content: flex-end;
  }
}
</style>

<style lang="scss">
/* 非 scoped：输入 / 下拉与经纬度同一套字 */
.station-config .station-config__form .el-input__inner,
.station-config .station-config__form .el-select__selected-item,
.station-config .station-config__form .el-select__placeholder,
.station-config .station-config__form .el-select__wrapper {
  font-family: Inter, "Noto Sans SC", sans-serif !important;
  font-size: 16px !important;
  line-height: 20px !important;
  font-weight: 400 !important;
}

/* code.html Latitude / Longitude box: 114×42, #07100b, px-3 py-2, mono 14px */
.station-config .station-config__coord-row .el-input__wrapper {
  width: 132px !important;
  height: 42px !important;
  min-height: 42px !important;
  padding: 8px 12px !important;
  background: #07100b !important;
  background-color: #07100b !important;
  border: 1px solid rgba(64, 73, 69, 0.5) !important;
  border-radius: 0.5rem !important;
  box-shadow: none !important;
  box-sizing: border-box !important;
}

.station-config .station-config__coord-row .el-input__wrapper.is-focus {
  border-color: #9ddf2e !important;
  border-width: 2px !important;
  outline: none !important;
  box-shadow: none !important;
}

.station-config .station-config__coord-row .el-input__inner {
  font-size: 16px !important;
  line-height: 20px !important;
  font-family: Inter, "Noto Sans SC", sans-serif !important;
  font-weight: 400 !important;
  color: #ffffff !important;
  white-space: pre !important;
  word-break: keep-all !important;
}

/* el-select 下拉层挂到 body，需非 scoped 才能覆盖 */
.station-config-select-dropdown.el-popper,
.station-config-select-dropdown {
  background: rgba(26, 34, 44, 0.96) !important;
  border: 1px solid rgba(180, 200, 220, 0.18) !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4) !important;
  --el-font-size-base: 16px;
  font-family: Inter, "Noto Sans SC", sans-serif !important;
  font-size: 16px !important;
}

.station-config-select-dropdown *,
.station-config-select-dropdown .el-select-dropdown__item,
.station-config-select-dropdown .el-select-dropdown__item span {
  font-family: Inter, "Noto Sans SC", sans-serif !important;
  font-size: 16px !important;
  line-height: 20px !important;
}

.station-config-select-dropdown .el-select-dropdown__item {
  color: rgba(235, 240, 245, 0.92) !important;
  background: transparent !important;
  height: auto !important;
  min-height: 32px !important;
  padding: 6px 12px !important;
}

.station-config-select-dropdown .el-select-dropdown__item.is-hovering,
.station-config-select-dropdown .el-select-dropdown__item:hover {
  background: rgba(163, 230, 53, 0.18) !important;
  color: #ffffff !important;
}

.station-config-select-dropdown .el-select-dropdown__item.is-selected {
  color: #bef264 !important;
  font-weight: 600;
  background: rgba(163, 230, 53, 0.12) !important;
}

.station-config-select-dropdown .el-popper__arrow::before {
  background: rgba(26, 34, 44, 0.96) !important;
  border: 1px solid rgba(180, 200, 220, 0.18) !important;
}

.station-config-select-dropdown.el-popper.is-light,
.station-config-select-dropdown.el-popper.is-light .el-popper__arrow::before {
  background: rgba(26, 34, 44, 0.96) !important;
  border-color: rgba(180, 200, 220, 0.18) !important;
}
</style>
