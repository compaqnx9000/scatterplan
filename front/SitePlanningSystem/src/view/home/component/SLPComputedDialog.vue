<template>
  <transition name="station-fade">
    <div
      v-if="showSLPComputedDialog"
      ref="panelRef"
      class="station-config"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__title">单链路计算配置</div>
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
          ref="SLPCompute"
          :model="SLPComputeForm"
          :rules="rules"
          label-position="top"
          class="station-config__form"
          require-asterisk-position="right"
        >
          <div class="station-config__columns station-config__columns--single">
            <section class="station-config__card">
              <h3 class="station-config__card-title">接收站点</h3>

              <el-form-item label="站点名称" prop="point_name">
                <el-input v-model="SLPComputeForm.point_name" placeholder="请输入" clearable />
              </el-form-item>

              <el-form-item label="坐标" prop="coordinate">
                <div class="station-config__coord-row">
                  <el-input :model-value="coordDisplay" placeholder="经度, 纬度" readonly />
                  <button
                    class="station-config__map-btn"
                    type="button"
                    title="地图选点"
                    @click="drawPoint('SLPCompute')"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                </div>
              </el-form-item>

              <div class="station-config__row-2">
                <el-form-item label="站点经度（°）" prop="lng">
                  <el-input v-model="SLPComputeForm.lng" placeholder="请输入" clearable />
                </el-form-item>
                <el-form-item label="站点纬度（°）" prop="lat">
                  <el-input v-model="SLPComputeForm.lat" placeholder="请输入" clearable />
                </el-form-item>
              </div>
            </section>
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
          <button
            class="station-config__btn station-config__btn--primary"
            type="button"
            @click="handleConfirmSLPComputed(SLPCompute)"
          >
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
import { ElMessage } from "element-plus";
import { validateLongitude, validateLatitude } from "@/view/home/service/rules";

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
  lng: [{ required: true, validator: validateLongitude, trigger: ["focus", "change"] }],
  lat: [{ required: true, validator: validateLatitude, trigger: ["focus", "change"] }],
  point_name: [{ required: true, message: "请输入站点名称", trigger: ["focus", "change"] }],
};

const SLPCompute = ref(null);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 520;

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

const coordDisplay = computed(() => {
  const lng = props.SLPComputeForm.lng;
  const lat = props.SLPComputeForm.lat;
  if (lng === "" || lng === null || lng === undefined || lat === "" || lat === null || lat === undefined) {
    return "";
  }
  return `${lng}, ${lat}`;
});

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

const updateSLPComputeData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.name === "SLPCompute") {
    props.SLPComputeForm.lng = graphic.point.lng;
    props.SLPComputeForm.lat = graphic.point.lat;
    props.SLPComputeForm.height = graphic.point.alt;
  }
};

$bus.on("drawSLPPointMsg", updateSLPComputeData);
$bus.on("drawPointEnd", onDrawPointEnd);

const updateSLPComputePoint = (position: mars3d.LngLatPoint) => {
  props.SLPComputeForm.lng = position.lng;
  props.SLPComputeForm.lat = position.lat;
  props.SLPComputeForm.height = position.alt;
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
      $bus.emit("setSLPCompute", {
        type: "SLPCompute",
        lng: props.SLPComputeForm.lng,
        lat: props.SLPComputeForm.lat,
        height: props.SLPComputeForm.height,
      });
      emit("update:visible", false);
    } else {
      ElMessage.error("请填写完整信息");
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
    margin-bottom: 18px;
    cursor: move;
    user-select: none;
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

  &__columns {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    width: 100%;

    &--single {
      grid-template-columns: minmax(0, 1fr);
    }
  }

  &__row-2 {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 12px;
    width: 100%;
  }

  &__card {
    width: 100%;
    min-width: 0;
    padding: 16px 14px 8px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
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
    min-width: 0;

    :deep(.el-input) {
      flex: 1;
      min-width: 0;
      width: auto !important;
    }
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 18px;
    gap: 12px;
    width: 100%;
    min-width: 0;
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
      flex-shrink: 0;

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

  &__form {
    width: 100%;
    min-width: 0;
  }

  :deep(.el-form-item) {
    margin-bottom: 14px;
    width: 100%;
    max-width: 100%;
  }

  :deep(.el-form-item__content) {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
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

  :deep(.station-config__form .el-input),
  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-input .el-input__wrapper) {
    width: 100% !important;
    max-width: 100% !important;
  }

  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-input .el-input__wrapper) {
    background: rgba(26, 34, 44, 0.72) !important;
    background-color: rgba(26, 34, 44, 0.72) !important;
    background-image: none !important;
    --el-input-bg-color: rgba(26, 34, 44, 0.72);
    --el-fill-color-blank: rgba(26, 34, 44, 0.72);
    --el-input-width: 100%;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 36px;
  }

  :deep(.station-config__form .el-input) {
    --el-input-bg-color: rgba(26, 34, 44, 0.72);
    --el-fill-color-blank: rgba(26, 34, 44, 0.72);
    --el-input-width: 100%;
  }

  :deep(.station-config__form .el-input__wrapper:hover),
  :deep(.station-config__form .el-input__wrapper.is-focus) {
    border-color: rgba(0, 162, 255, 0.45) !important;
    box-shadow: none !important;
    background: rgba(26, 34, 44, 0.72) !important;
    background-color: rgba(26, 34, 44, 0.72) !important;
    background-image: none !important;
  }

  :deep(.station-config__form .el-input__inner) {
    color: #ffffff !important;
    font-size: 12px !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder) {
    color: #6b7280 !important;
  }

  :deep(.station-config__form .el-form-item__error) {
    color: #ff7b7b;
    font-size: 11px;
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
