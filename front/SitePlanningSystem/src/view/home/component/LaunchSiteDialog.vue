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
          <div class="station-config__title">站点配置</div>
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
              <h3 class="station-config__card-title">基本设置</h3>

              <el-form-item label="站点名称" prop="point_name">
                <el-input v-model="drawLaunchSiteForm.point_name" placeholder="请输入站点名称" clearable />
              </el-form-item>

              <el-form-item label="坐标" prop="coordinate">
                <div class="station-config__coord-row">
                  <el-input :model-value="coordDisplay" placeholder="经度, 纬度" readonly />
                  <button class="station-config__map-btn" type="button" title="地图选点" @click="drawPoint('LaunchSite')">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                </div>
              </el-form-item>

              <el-form-item label="发射站经度（°）" prop="lng">
                <el-input v-model="drawLaunchSiteForm.lng" placeholder="请输入" clearable />
              </el-form-item>

              <el-form-item label="发射站纬度（°）" prop="lat">
                <el-input v-model="drawLaunchSiteForm.lat" placeholder="请输入" clearable />
              </el-form-item>

              <el-form-item label="气候区选择" prop="climate_num">
                <el-select
                  v-model="drawLaunchSiteForm.climate_num"
                  placeholder="自动选择"
                  clearable
                  popper-class="station-config-select-dropdown"
                >
                  <el-option label="海洋气候区" value="0" />
                  <el-option label="赤道气候区" value="1" />
                  <el-option label="大陆性亚热带气候区" value="2" />
                  <el-option label="海洋性亚热带气候区" value="3" />
                  <el-option label="沙漠气候区" value="4" />
                  <el-option label="大陆性温带气候区" value="5" />
                  <el-option label="海洋性温带陆地气候区" value="6" />
                </el-select>
              </el-form-item>
            </section>

            <!-- 无线电参数 -->
            <section class="station-config__card">
              <h3 class="station-config__card-title">无线电参数</h3>

              <el-form-item label="信号频率（MHz）" prop="freq">
                <el-input v-model="drawLaunchSiteForm.freq" placeholder="请输入" clearable />
              </el-form-item>

              <el-form-item label="发射功率（W）" prop="trans_power">
                <el-input v-model="drawLaunchSiteForm.trans_power" placeholder="请输入" clearable />
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
                <el-input v-model="drawLaunchSiteForm.diversity_order" placeholder="请输入" clearable />
              </el-form-item>
            </section>

            <!-- 天线参数 -->
            <section class="station-config__card">
              <h3 class="station-config__card-title">天线参数</h3>

              <el-form-item label="发射天线增益（dB）" prop="tx_gain">
                <el-input v-model="drawLaunchSiteForm.tx_gain" placeholder="请输入" clearable />
              </el-form-item>

              <el-form-item label="接收天线增益（dB）" prop="rx_gain">
                <el-input v-model="drawLaunchSiteForm.rx_gain" placeholder="请输入" clearable />
              </el-form-item>
            </section>
          </div>
          </div>
        </el-form>

        <div class="station-config__footer">
          <div class="station-config__footer-left">
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="handleReset">
              重置
            </button>
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
              取消
            </button>
          </div>
          <button class="station-config__btn station-config__btn--primary" type="button" @click="handleConfirmVisible(launchSiteForm)">
            <span>确认</span>
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
//@ts-nocheck

import { computed, getCurrentInstance, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { validateLongitude, validateLatitude } from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const rules = ref({
  diversity_order: [{ required: true, message: "请输入调整系数", trigger: "change" }],
  tx_gain: [{ required: true, message: "请输入发射天线增益", trigger: "change" }],
  rx_gain: [{ required: true, message: "请输入接收天线增益", trigger: "change" }],
  freq: [{ required: true, message: "请输入信号频率", trigger: "change" }],
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
      lng: "",
      lat: "",
      height: 10,
      point_name: "",
      comm_rate: "2.4kbps",
      climate_num: "",
    }),
  },
});

const emit = defineEmits(["update:visible", "update:drawLaunchSiteForm", "update:isSelectStartPointOver"]);

const launchSiteForm = ref(null);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 1080;

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

const coordDisplay = computed(() => {
  const lng = props.drawLaunchSiteForm.lng;
  const lat = props.drawLaunchSiteForm.lat;
  if (lng === "" || lng === null || lng === undefined || lat === "" || lat === null || lat === undefined) {
    return "";
  }
  return `${lng}, ${lat}`;
});

const handleConfirmVisible = async (formEl) => {
  if (!formEl) return;
  await formEl.validate((valid) => {
    if (valid) {
      $bus.emit("setLaunchSite", {
        type: "LaunchSite",
        lng: props.drawLaunchSiteForm.lng,
        lat: props.drawLaunchSiteForm.lat,
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
    lng: "",
    lat: "",
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
    props.drawLaunchSiteForm.lng = graphic.point.lng;
    props.drawLaunchSiteForm.lat = graphic.point.lat;
    props.drawLaunchSiteForm.height = graphic.point.alt;
  }
};

$bus.on("drawPointMsg", updateLaunchSiteData);
$bus.on("drawPointEnd", onDrawPointEnd);

const setLaunchSitePosition = (position: any) => {
  props.drawLaunchSiteForm.lng = position.lng;
  props.drawLaunchSiteForm.lat = position.lat;
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
  width: min(1080px, calc(100vw - 48px));
  pointer-events: all;
  /* 非模态浮层：不遮罩地球，可拖动标题栏 */

  &__panel {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 22px 24px 22px;
    border-radius: 14px;
    background: rgba(26, 34, 44, 0.62);
    border: 1px solid rgba(180, 200, 220, 0.18);
    box-shadow:
      0 18px 48px rgba(0, 0, 0, 0.38),
      inset 0 1px 0 rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(18px) saturate(1.2);
    -webkit-backdrop-filter: blur(18px) saturate(1.2);
    color: #ffffff;
    overflow: visible;
    box-sizing: border-box;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    cursor: move;
    user-select: none;
    flex-shrink: 0;
  }

  &__title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #ffffff;
  }

  &__close {
    width: 32px;
    height: 32px;
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

  &__columns {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    align-items: start;
  }

  &__form {
    display: block !important;
    width: 100%;
    height: auto !important;
    flex: 0 0 auto !important;
    overflow: visible !important;
    margin: 0;
    padding: 0;
  }

  &__body {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  &__card {
    padding: 16px 14px 12px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.05);
    min-height: 0;
    height: auto;
  }

  &__card-title {
    margin: 0 0 14px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
  }

  &__coord-row {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
  }

  &__map-btn {
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    background: rgba(26, 34, 44, 0.72);
    color: #8ec8ff;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 18px;
      height: 18px;
    }

    &:hover {
      background: #303841;
      color: #b7dcff;
    }
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex: 0 0 auto !important;
    width: 100%;
    box-sizing: border-box;
    position: static !important;
    inset: auto !important;
    z-index: auto !important;
    margin: 32px 0 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    clear: both;
  }

  &__footer-left {
    display: flex;
    gap: 10px;
    flex-shrink: 0;
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
    transition: transform 0.15s ease, opacity 0.15s ease, box-shadow 0.15s ease;

    &--ghost {
      min-width: 88px;
      height: 40px;
      padding: 0 18px;
      border-radius: 8px;
      background: rgba(38, 44, 53, 0.92);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: rgba(235, 240, 245, 0.92);

      &:hover {
        background: rgba(48, 56, 66, 0.95);
      }
    }

    &--primary {
      min-width: 168px;
      height: 44px;
      padding: 0 18px 0 24px;
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

  :deep(.el-form-item) {
    margin-bottom: 14px;

    &:last-child {
      margin-bottom: 4px;
    }
  }

  :deep(.el-form-item__label) {
    color: rgba(190, 200, 212, 0.88);
    font-size: 10px;
    line-height: 1.2;
    margin-bottom: 6px !important;
    padding: 0;
  }

  :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
  :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
    color: #ff6b6b;
  }

  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-select__wrapper),
  :deep(.station-config__form .el-input .el-input__wrapper),
  :deep(.station-config__form .el-select .el-select__wrapper) {
    background: rgba(26, 34, 44, 0.72) !important;
    background-color: rgba(26, 34, 44, 0.72) !important;
    background-image: none !important;
    --el-input-bg-color: rgba(26, 34, 44, 0.72);
    --el-fill-color-blank: rgba(26, 34, 44, 0.72);
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 36px;
  }

  :deep(.station-config__form .el-input),
  :deep(.station-config__form .el-select) {
    --el-input-bg-color: rgba(26, 34, 44, 0.72);
    --el-fill-color-blank: rgba(26, 34, 44, 0.72);
  }

  :deep(.station-config__form .el-input__wrapper:hover),
  :deep(.station-config__form .el-select__wrapper:hover),
  :deep(.station-config__form .el-input__wrapper.is-focus),
  :deep(.station-config__form .el-select__wrapper.is-focused) {
    border-color: rgba(0, 162, 255, 0.45) !important;
    box-shadow: none !important;
    background: rgba(26, 34, 44, 0.72) !important;
    background-color: rgba(26, 34, 44, 0.72) !important;
    background-image: none !important;
  }

  :deep(.station-config__form .el-input__inner),
  :deep(.station-config__form .el-select__placeholder),
  :deep(.station-config__form .el-select__selected-item) {
    color: #ffffff !important;
    font-size: 12px !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder),
  :deep(.station-config__form .el-select__placeholder.is-transparent) {
    color: #6b7280 !important;
  }

  :deep(.station-config__form .el-select__caret),
  :deep(.station-config__form .el-input__suffix) {
    color: rgba(180, 190, 200, 0.75) !important;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper),
  :deep(.station-config__form .el-form-item.is-error .el-select__wrapper) {
    border-color: rgba(248, 113, 113, 0.7) !important;
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
    flex-direction: column;
    align-items: stretch;
  }

  .station-config__footer-left {
    justify-content: flex-start;
  }

  .station-config__btn--primary {
    width: 100%;
  }
}
</style>

<style lang="scss">
/* el-select 下拉层挂到 body，需非 scoped 才能覆盖 */
.station-config-select-dropdown.el-popper,
.station-config-select-dropdown {
  background: rgba(26, 34, 44, 0.96) !important;
  border: 1px solid rgba(180, 200, 220, 0.18) !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4) !important;
  --el-font-size-base: 12px;
  font-family: 'IBM Plex Mono', 'Cascadia Mono', 'Noto Sans SC', monospace !important;
  font-size: 12px !important;
}

.station-config-select-dropdown *,
.station-config-select-dropdown .el-select-dropdown__item,
.station-config-select-dropdown .el-select-dropdown__item span {
  font-family: 'IBM Plex Mono', 'Cascadia Mono', 'Noto Sans SC', monospace !important;
  font-size: 12px !important;
  line-height: 1.45 !important;
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
  background: rgba(0, 162, 255, 0.18) !important;
  color: #ffffff !important;
}

.station-config-select-dropdown .el-select-dropdown__item.is-selected {
  color: #7ec8ff !important;
  font-weight: 600;
  background: rgba(0, 162, 255, 0.12) !important;
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
