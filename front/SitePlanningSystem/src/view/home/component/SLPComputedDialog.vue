<template>
  <transition name="station-fade">
    <div
      v-if="showSLPComputedDialog"
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
              <h2 class="station-config__title">单链路计算配置</h2>
              <p class="station-config__subtitle">Configure receive site for single-link analysis.</p>
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
            <button
              class="station-config__icon-btn station-config__icon-btn--close"
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
        </div>

        <el-form
          ref="SLPCompute"
          :model="SLPComputeForm"
          :rules="rules"
          label-position="top"
          class="station-config__form"
          require-asterisk-position="right"
          :show-message="false"
        >
          <div class="station-config__body">
            <section class="station-config__card">
              <div class="station-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <h3>Receive Site</h3>
              </div>

              <div class="station-config__site-fields">
                <el-form-item class="station-config__name-item" label="站点名称" prop="point_name">
                  <el-input v-model="SLPComputeForm.point_name" placeholder="请输入站点名称" />
                </el-form-item>

                <div class="station-config__coord-row">
                  <el-form-item label="经度" prop="lng">
                    <el-input v-model="SLPComputeForm.lng" placeholder="请输入" />
                  </el-form-item>
                  <el-form-item label="纬度" prop="lat">
                    <el-input v-model="SLPComputeForm.lat" placeholder="请输入" />
                  </el-form-item>
                </div>

                <button class="station-config__map-pick" type="button" @click="drawPoint('SLPCompute')">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                      fill="currentColor"
                    />
                  </svg>
                  <span>地图选点</span>
                </button>
              </div>
            </section>
          </div>
        </el-form>

        <div class="station-config__footer">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button
            class="station-config__btn station-config__btn--primary"
            type="button"
            @click="handleConfirmSLPComputed(SLPCompute)"
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

const props = defineProps({
  showSLPComputedDialog: {
    type: Boolean,
    default: false,
  },
  SLPComputeForm: {
    type: Object,
    default: () => ({
      lng: "",
      lat: "",
      height: 0,
      point_name: "",
    }),
  },
});

const emit = defineEmits(["update:visible", "update:drawLaunchSiteForm"]);

const rules = {
  lng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  lat: [{ required: true, validator: validateLatitude, trigger: "change" }],
  point_name: [{ required: true, message: "请输入站点名称", trigger: "change" }],
};

const SLPCompute = ref(null);

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
  () => props.showSLPComputedDialog,
  (val) => {
    if (val) centerPanel();
  }
);

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
  if (payload?.type && payload.type !== "SLPCompute") return;
  finishPickMode();
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

  $bus.emit("drawSLPPoint", { type, name: props.SLPComputeForm.point_name });
};

watch(
  () => props.SLPComputeForm.point_name,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      $bus.emit("setSLPComputeName", {
        type: "SLPCompute",
        point_name: newVal,
      });
    }
  }
);

const applyPoint = (lng: any, lat: any, alt: any) => {
  props.SLPComputeForm.lng = formatLongitude(lng);
  props.SLPComputeForm.lat = formatLatitude(lat);
  props.SLPComputeForm.height = alt;
};

const updateSLPComputeData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.name === "SLPCompute") {
    applyPoint(graphic.point.lng, graphic.point.lat, graphic.point.alt);
  }
};

$bus.on("drawSLPPointMsg", updateSLPComputeData);
$bus.on("drawPointEnd", onDrawPointEnd);

const updateSLPComputePoint = (position: mars3d.LngLatPoint) => {
  applyPoint(position.lng, position.lat, position.alt);
};

$bus.on("changeSLPPoint", updateSLPComputePoint);

const handleReset = () => {
  Object.assign(props.SLPComputeForm, {
    lng: "",
    lat: "",
    height: 0,
    point_name: "",
  });
  SLPCompute.value?.clearValidate?.();
};

const handleConfirmSLPComputed = async (formEl: any) => {
  if (!formEl) return;
  await formEl.validate((valid) => {
    if (valid) {
      const lng = parseLongitude(props.SLPComputeForm.lng);
      const lat = parseLatitude(props.SLPComputeForm.lat);
      $bus.emit("setSLPCompute", {
        type: "SLPCompute",
        lng,
        lat,
        height: props.SLPComputeForm.height,
      });
      emit("update:visible", false);
    } else {
      shakeInvalidFormFields(formEl);
    }
  });
};

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

onBeforeUnmount(() => {
  stopDrag();
  cleanupPickMode();
  $bus.off("drawSLPPointMsg", updateSLPComputeData);
  $bus.off("drawPointEnd", onDrawPointEnd);
  $bus.off("changeSLPPoint", updateSLPComputePoint);
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 1200;
  width: min(560px, calc(100vw - 48px));
  box-sizing: border-box;
  pointer-events: all;

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
    font-family: Inter, sans-serif !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 28px;
    color: #ffffff !important;
    word-break: normal;
  }

  &__subtitle {
    margin: 4px 0 0;
    font-family: Inter, sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    line-height: 18px;
    color: #c0c8c3 !important;
    word-break: normal;
    white-space: nowrap;
  }

  &__header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  &__reset {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    height: 28px;
    padding: 0 10px;
    border: 1px solid rgba(64, 73, 69, 0.5);
    border-radius: 0.5rem;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    flex-shrink: 0;
    cursor: pointer;
    transition: border-color 0.15s ease, color 0.15s ease, background-color 0.15s ease;

    svg {
      width: 14px;
      height: 14px;
      flex-shrink: 0;
    }

    &:hover {
      border-color: rgba(163, 230, 53, 0.45);
      color: #9ddf2e;
      background: rgba(157, 223, 46, 0.08);
    }
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
    }

    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
  }

  &__body {
    padding: 20px 24px;
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
      line-height: 16px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #ffffff !important;
      word-break: normal;
    }
  }

  &__site-fields {
    width: 100%;
    max-width: 100%;
  }

  &__name-item {
    width: 100% !important;
    max-width: 100% !important;

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: 100% !important;
      max-width: 100% !important;
    }
  }

  &__coord-row {
    --coord-h: 42px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: start;
    column-gap: 12px;
    width: 100% !important;
    max-width: 100%;
    margin-bottom: 10px;

    :deep(.el-form-item) {
      margin-bottom: 0 !important;
      width: 100% !important;
      max-width: 100% !important;
    }

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: 100% !important;
      max-width: 100% !important;
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
      outline: none !important;
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

  &__map-pick {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-sizing: border-box;
    height: 24px;
    margin: 0;
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
  }

  &__btn {
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
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

  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-input .el-input__wrapper) {
    background: #07100b !important;
    background-color: #07100b !important;
    background-image: none !important;
    --el-input-bg-color: #07100b;
    --el-fill-color-blank: #07100b;
    --el-input-border-color: rgba(180, 200, 220, 0.18);
    --el-border-color: rgba(180, 200, 220, 0.18);
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    outline: none !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 40px;
    transition: border-color 0.15s ease;
  }

  :deep(.station-config__form .el-input__wrapper:hover) {
    border-color: rgba(180, 200, 220, 0.32) !important;
    box-shadow: none !important;
    background: #07100b !important;
  }

  :deep(.station-config__form .el-input__wrapper.is-focus),
  :deep(.station-config__form .el-input__wrapper.is-focus:hover) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    outline: none !important;
    box-shadow: none !important;
    background: #07100b !important;
  }

  :deep(.station-config__form .el-input__inner) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    line-height: 20px !important;
    color: #dae5dc !important;
  }

  :deep(.station-config__form .el-input__inner::selection),
  :deep(.station-config__form input::selection) {
    background: #9ddf2e !important;
    color: #213600 !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder) {
    color: rgba(192, 200, 195, 0.7) !important;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper) {
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
</style>
