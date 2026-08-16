<template>
  <transition name="station-fade">
    <div
      v-if="showCommunicationAreaDialog"
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
                  d="M4 6.5h16v11H4zM8 10h8M8 14h5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="station-config__title">区域覆盖计算适配</h2>
              <p class="station-config__subtitle">Define coverage region for scatter analysis.</p>
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

        <div class="station-config__body">
          <div class="station-config__tabs">
            <button
              class="station-config__tab"
              :class="{ 'is-active': CommunicationArea.activeName === 'Rectangle' }"
              type="button"
              @click="CommunicationArea.activeName = 'Rectangle'"
            >
              矩形区域
            </button>
            <button
              class="station-config__tab"
              :class="{ 'is-active': CommunicationArea.activeName === 'Round' }"
              type="button"
              @click="CommunicationArea.activeName = 'Round'"
            >
              圆形区域
            </button>
          </div>

          <div v-show="CommunicationArea.activeName === 'Rectangle'">
            <el-form
              ref="RectangleFormRef"
              :rules="rules.Rectangle"
              :model="CommunicationArea"
              label-position="top"
              class="station-config__form"
              require-asterisk-position="right"
              :show-message="false"
            >
              <section class="station-config__card">
                <div class="station-config__section-head">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M5 5h14v14H5z" fill="none" stroke="currentColor" stroke-width="1.6" />
                  </svg>
                  <h3>Rectangle</h3>
                </div>

                <div class="station-config__coord-row">
                  <el-form-item label="起点经度" prop="initialPointLng">
                    <el-input v-model="CommunicationArea.initialPointLng" placeholder="请输入" />
                  </el-form-item>
                  <el-form-item label="起点纬度" prop="initialPointLat">
                    <el-input v-model="CommunicationArea.initialPointLat" placeholder="请输入" />
                  </el-form-item>
                </div>
                <div class="station-config__coord-row">
                  <el-form-item label="终点经度" prop="destinationPointLng">
                    <el-input v-model="CommunicationArea.destinationPointLng" placeholder="请输入" />
                  </el-form-item>
                  <el-form-item label="终点纬度" prop="destinationPointLat">
                    <el-input v-model="CommunicationArea.destinationPointLat" placeholder="请输入" />
                  </el-form-item>
                </div>

                <button class="station-config__map-pick" type="button" @click="drawGraph('Rectangle')">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                      fill="currentColor"
                    />
                  </svg>
                  <span>地图绘制</span>
                </button>
              </section>
            </el-form>
          </div>

          <div v-show="CommunicationArea.activeName === 'Round'">
            <el-form
              ref="roundFormRef"
              :rules="rules.round"
              :model="CommunicationArea"
              label-position="top"
              class="station-config__form"
              require-asterisk-position="right"
              :show-message="false"
            >
              <section class="station-config__card">
                <div class="station-config__section-head">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.6" />
                  </svg>
                  <h3>Circle</h3>
                </div>

                <div class="station-config__coord-row">
                  <el-form-item label="中心经度" prop="centerPointLng">
                    <el-input v-model="CommunicationArea.centerPointLng" placeholder="请输入" />
                  </el-form-item>
                  <el-form-item label="中心纬度" prop="centerPointLat">
                    <el-input v-model="CommunicationArea.centerPointLat" placeholder="请输入" />
                  </el-form-item>
                </div>

                <el-form-item label="目标区域半径" prop="radius">
                  <el-input v-model="CommunicationArea.radius" placeholder="请输入">
                    <template #suffix>
                      <span class="station-config__unit">km</span>
                    </template>
                  </el-input>
                </el-form-item>

                <button class="station-config__map-pick" type="button" @click="drawGraph('round')">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                      fill="currentColor"
                    />
                  </svg>
                  <span>地图绘制</span>
                </button>
              </section>
            </el-form>
          </div>
        </div>

        <div class="station-config__footer">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button
            class="station-config__btn station-config__btn--primary"
            type="button"
            @click="handleConfirmCommunicationArea"
          >
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
import { ElMessage } from "element-plus";
import {
  validateLongitude,
  validateLatitude,
  formatLongitude,
  formatLatitude,
  parseLongitude,
  parseLatitude,
} from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const RectangleRules = {
  initialPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  initialPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
  destinationPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  destinationPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
};
const RoundRules = {
  centerPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  centerPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
  radius: [{ required: true, message: "请输入半径", trigger: "change" }],
};
const rules = {
  Rectangle: RectangleRules,
  round: RoundRules,
};

const props = defineProps({
  showCommunicationAreaDialog: {
    type: Boolean,
    default: false,
  },
  CommunicationArea: {
    type: Object,
    default: () => ({
      activeName: "Rectangle",
      initialPointLng: "",
      initialPointLat: "",
      destinationPointLng: "",
      destinationPointLat: "",
      centerPointLng: "",
      centerPointLat: "",
      radius: "",
    }),
  },
  CommunicationAreaProhibited: {
    type: Object,
    default: () => ({
      activeProhibitedName: "Rectangle",
      initialPointLng: "",
      initialPointLat: "",
      destinationPointLng: "",
      destinationPointLat: "",
      centerPointLng: "",
      centerPointLat: "",
      radius: "",
    }),
  },
  launchSite: {
    type: Object,
    default: () => ({
      lng: "",
      lat: "",
    }),
  },
});

const emit = defineEmits(["update:visible", "update:drawLaunchSiteForm"]);

const RectangleFormRef = ref<any>(null);
const roundFormRef = ref<any>(null);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 560;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 420;
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

watch(
  () => props.showCommunicationAreaDialog,
  (val) => {
    if (val) centerPanel();
  }
);

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

const onDrawAreaEnd = (payload: { type?: string }) => {
  if (payload?.type && payload.type !== "Rectangle" && payload.type !== "round") return;
  finishPickMode();
};

const handleConfirmCommunicationArea = async () => {
  if (props.CommunicationArea.activeName === "Rectangle") {
    await RectangleFormRef.value?.validate((valid) => {
      if (valid) {
        $bus.emit("setCommunicationArea", props.CommunicationArea);
        setVisible(false);
      } else {
        shakeInvalidFormFields(RectangleFormRef.value);
      }
    });
  } else if (props.CommunicationArea.activeName === "Round") {
    await roundFormRef.value?.validate((valid) => {
      if (valid) {
        $bus.emit("setCommunicationArea", props.CommunicationArea);
        setVisible(false);
      } else {
        shakeInvalidFormFields(roundFormRef.value);
      }
    });
  }
};

const drawGraph = (type: string) => {
  pendingPickRestore.value = true;
  setVisible(false);

  const onEsc = (e: KeyboardEvent) => {
    if (e.key !== "Escape") return;
    $bus.emit("cancelDrawPoint");
    finishPickMode();
  };
  pickEscHandler = onEsc;
  window.addEventListener("keydown", onEsc);

  $bus.emit("drawCommunicationArea", type);
};

const getDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

const readLngLat = (point: any): [number, number] | null => {
  if (!point) return null;
  if (Array.isArray(point) && Number.isFinite(Number(point[0])) && Number.isFinite(Number(point[1]))) {
    return [Number(point[0]), Number(point[1])];
  }
  const lng = point.lng ?? point.lon ?? point.x;
  const lat = point.lat ?? point.y;
  if (Number.isFinite(Number(lng)) && Number.isFinite(Number(lat))) {
    return [Number(lng), Number(lat)];
  }
  return null;
};

const updateCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (!graphic) return;
  const json = graphic.toJSON?.() || {};
  const name = json.name || graphic.name;
  if (name === "Rectangle") {
    const start = readLngLat(json.positions?.[0]);
    const end = readLngLat(json.positions?.[1]);
    if (!start || !end) return;
    props.CommunicationArea.initialPointLng = formatLongitude(start[0]);
    props.CommunicationArea.initialPointLat = formatLatitude(start[1]);
    props.CommunicationArea.destinationPointLng = formatLongitude(end[0]);
    props.CommunicationArea.destinationPointLat = formatLatitude(end[1]);
    const launchLng = parseLongitude(props.launchSite.lng);
    const launchLat = parseLatitude(props.launchSite.lat);
    if (Number.isFinite(launchLng) && Number.isFinite(launchLat) && launchLng !== 0 && launchLat !== 0) {
      const minLng = Math.min(start[0], end[0]);
      const maxLng = Math.max(start[0], end[0]);
      const minLat = Math.min(start[1], end[1]);
      const maxLat = Math.max(start[1], end[1]);
      if (launchLng < minLng || launchLng > maxLng || launchLat < minLat || launchLat > maxLat) {
        ElMessage.error({
          message: "发射站点不在绘制区域内，请重新绘制",
          duration: 0,
          offset: 200,
          showClose: true,
        });
        graphic.remove();
        return;
      }
    }
  } else if (name === "round" || name === "Round") {
    const center = readLngLat(json.position || json.center);
    const radiusM = json.style?.radius;
    if (!center || !radiusM) return;
    props.CommunicationArea.centerPointLng = formatLongitude(center[0]);
    props.CommunicationArea.centerPointLat = formatLatitude(center[1]);
    props.CommunicationArea.radius = radiusM / 1000;
    const launchLng = parseLongitude(props.launchSite.lng);
    const launchLat = parseLatitude(props.launchSite.lat);
    if (Number.isFinite(launchLng) && Number.isFinite(launchLat) && launchLng !== 0 && launchLat !== 0) {
      const radius = radiusM / 1000;
      const distance = getDistance(launchLat, launchLng, center[1], center[0]);
      if (distance > radius) {
        ElMessage.error({
          message: "发射站点不在绘制区域内，请重新绘制",
          duration: 0,
          offset: 200,
          showClose: true,
        });
        graphic.remove();
        return;
      }
    }
  }
};

$bus.on("drawCommunicationAreaMsg", updateCommunicationAreaData);
$bus.on("drawCommunicationAreaEnd", onDrawAreaEnd);

const updateProhibitedCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.toJSON().name === "prohibitedRectangle") {
    props.CommunicationAreaProhibited.initialPointLng = graphic.toJSON().positions[0][0];
    props.CommunicationAreaProhibited.initialPointLat = graphic.toJSON().positions[0][1];
    props.CommunicationAreaProhibited.destinationPointLng = graphic.toJSON().positions[1][0];
    props.CommunicationAreaProhibited.destinationPointLat = graphic.toJSON().positions[1][1];
  } else if (graphic && graphic.toJSON().name === "prohibitedround") {
    props.CommunicationAreaProhibited.centerPointLng = graphic.toJSON().position[0];
    props.CommunicationAreaProhibited.centerPointLat = graphic.toJSON().position[1];
    props.CommunicationAreaProhibited.radius = graphic.toJSON().style.radius / 1000;
  }
};

$bus.on("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);

watch(
  () => props.CommunicationArea.activeName,
  (newVal) => {
    $bus.emit("showCommunicationArea", newVal);
  }
);
watch(
  () => props.CommunicationAreaProhibited.activeProhibitedName,
  (newVal) => {
    $bus.emit("showProhibitedCommunicationArea", newVal);
  }
);

onBeforeUnmount(() => {
  stopDrag();
  cleanupPickMode();
  $bus.off("drawCommunicationAreaMsg", updateCommunicationAreaData);
  $bus.off("drawCommunicationAreaEnd", onDrawAreaEnd);
  $bus.off("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 1200;
  width: min(560px, calc(100vw - 48px));
  pointer-events: all;
  box-sizing: border-box;

  &__panel {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow: hidden;
    border-radius: 0.75rem;
    background: rgba(12, 21, 16, 0.85);
    border: 1px solid rgba(64, 73, 69, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    color: #dae5dc;
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
    font-size: 22px !important;
    font-weight: 600 !important;
    line-height: 30px;
    color: #ffffff !important;
    white-space: nowrap;
  }

  &__subtitle {
    margin: 4px 0 0;
    font-family: Inter, sans-serif !important;
    font-size: 13px !important;
    line-height: 18px;
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
    padding: 20px 24px;
  }

  &__tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }

  &__tab {
    height: 32px;
    padding: 0 16px;
    border-radius: 9999px;
    border: 1px solid #404945;
    background: #18221c;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;
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

  &__card {
    width: 100%;
    min-width: 0;
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
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #ffffff !important;
    }
  }

  &__coord-row {
    --coord-h: 42px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 12px;
    width: 100%;
    margin-bottom: 4px;

    :deep(.el-form-item) {
      margin-bottom: 14px !important;
      width: 100% !important;
    }

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: 100% !important;
    }

    :deep(.el-input__wrapper) {
      height: var(--coord-h) !important;
      min-height: var(--coord-h) !important;
      box-sizing: border-box !important;
      padding: 8px 12px !important;
      background: #07100b !important;
      border: 1px solid rgba(64, 73, 69, 0.5) !important;
      border-radius: 0.5rem !important;
      box-shadow: none !important;
      outline: none !important;
    }

    :deep(.el-input__wrapper.is-focus) {
      border-color: #9ddf2e !important;
      border-width: 2px !important;
      box-shadow: none !important;
    }

    :deep(.el-input__inner) {
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 16px !important;
      color: #ffffff !important;
      white-space: pre !important;
    }
  }

  &__map-pick {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 24px;
    margin: 4px 0 0;
    padding: 0 14px;
    border-radius: 9999px;
    border: 1px dashed #8a938e;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;

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
    color: #a1d1bf !important;
    pointer-events: none;
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(64, 73, 69, 0.2) !important;
    background: rgba(45, 55, 49, 0.3) !important;
  }

  &__btn {
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
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
      box-shadow: 0 0 20px rgba(157, 223, 46, 0.4);

      &:hover {
        background: #b2f746;
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(157, 223, 46, 0.6);
      }
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;
    width: 100%;
  }

  :deep(.el-form-item__label) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    height: 20px;
    width: auto !important;
    margin-bottom: 6px !important;
    padding: 0;
    white-space: nowrap;
  }

  :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
  :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
    color: #ffb4ab !important;
  }

  :deep(.station-config__form .el-input__wrapper) {
    background: #07100b !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 40px;
  }

  :deep(.station-config__form .el-input__wrapper:hover) {
    border-color: rgba(180, 200, 220, 0.32) !important;
  }

  :deep(.station-config__form .el-input__wrapper.is-focus) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    box-shadow: none !important;
  }

  :deep(.station-config__form .el-input__inner) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 16px !important;
    color: #dae5dc !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder) {
    color: rgba(192, 200, 195, 0.7) !important;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper) {
    border-color: #ffb4ab !important;
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
</style>
