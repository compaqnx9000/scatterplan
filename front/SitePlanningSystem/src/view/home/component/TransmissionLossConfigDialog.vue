<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="loss-config"
      :style="panelStyle"
    >
      <div class="loss-config__panel">
        <div class="loss-config__header" @mousedown="startDrag">
          <div class="loss-config__title">传输损耗配置</div>
          <button class="loss-config__close" type="button" title="关闭" @click="handleCancel" @mousedown.stop>
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

        <div class="loss-config__body">
          <div class="loss-config__main">
            <section class="loss-config__card">
              <h3 class="loss-config__card-title">通用控制</h3>
              <div class="loss-config__controls">
                <button
                  class="loss-config__shot"
                  type="button"
                  :disabled="!canScreenshot"
                  @click="$emit('screenshot')"
                >
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="3.2" y="4.2" width="17.6" height="12.4" rx="1.8" fill="none" stroke="currentColor" stroke-width="1.7" />
                    <path d="M8 20.2h8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
                    <path d="M12 16.6v3.6" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
                  </svg>
                  <span>截图 (Screenshot)</span>
                </button>
                <div class="loss-config__divider"></div>
                <div class="loss-config__toggle">
                  <el-switch
                    :model-value="lossMapVisible"
                    :disabled="!canToggleLossMap"
                    @change="$emit('toggleLossMap', $event)"
                  />
                  <span>损耗图显隐 (Loss Map Visibility)</span>
                </div>
              </div>
            </section>

            <section class="loss-config__card">
              <h3 class="loss-config__card-title">色条配置</h3>
              <div class="loss-config__ribbons">
                <button
                  v-for="(item, index) in colorBarList"
                  :key="index"
                  class="loss-config__ribbon"
                  :class="{ 'is-active': draftRadio === index }"
                  type="button"
                  @click="selectRibbon(index)"
                >
                  <span class="loss-config__ribbon-bar" :style="ribbonStyle(item)"></span>
                </button>
              </div>
              <div class="loss-config__gradient-labels">
                <span>低损耗</span>
                <span>高损耗</span>
              </div>
            </section>

            <section class="loss-config__card">
              <h3 class="loss-config__card-title">传输损耗阈值 (Transmission Loss dB)</h3>
              <div class="loss-config__range">
                <label class="loss-config__field">
                  <span class="loss-config__field-label">Min</span>
                  <el-input v-model="draftThresholdStart" />
                </label>
                <span class="loss-config__dash">—</span>
                <label class="loss-config__field">
                  <span class="loss-config__field-label">Max</span>
                  <el-input v-model="draftThresholdEnd" />
                </label>
              </div>
            </section>
          </div>

          <aside v-if="!hideLegend" class="loss-config__legend">
            <div class="loss-config__legend-title">传输损耗(dB)</div>
            <div class="loss-config__legend-body">
              <div class="loss-config__legend-bar" :style="verticalGradientStyle"></div>
              <div class="loss-config__legend-scale">
                <div v-for="(scale, index) in scales" :key="index" class="loss-config__legend-item">
                  <span class="loss-config__legend-line"></span>
                  <span>{{ scale }}</span>
                </div>
              </div>
            </div>
          </aside>
        </div>

        <div class="loss-config__footer">
          <div class="loss-config__footer-left">
            <button class="loss-config__btn loss-config__btn--ghost" type="button" @click="handleCancel">
              取消
            </button>
          </div>
          <button
            class="loss-config__btn loss-config__btn--primary"
            type="button"
            :disabled="btnLoading"
            @click="handleConfirm"
          >
            <span>{{ btnLoading ? "处理中" : "确认" }}</span>
            <span class="loss-config__btn-arrow">
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

const props = defineProps({
  visible: { type: Boolean, default: false },
  colorBarList: { type: Array as () => any[], default: () => [] },
  radio: { type: Number, default: 0 },
  selectIndex: { type: [String, Number], default: "1-1" },
  panelColor: { type: String, default: "" },
  thresholdStart: { type: [String, Number], default: 180 },
  thresholdEnd: { type: [String, Number], default: 300 },
  scales: { type: Array as () => Array<string | number>, default: () => [] },
  btnLoading: { type: Boolean, default: false },
  canScreenshot: { type: Boolean, default: false },
  canToggleLossMap: { type: Boolean, default: false },
  lossMapVisible: { type: Boolean, default: true },
  hideLegend: { type: Boolean, default: true },
  anchorSelector: { type: String, default: ".fixed-color-bar" },
});

const emit = defineEmits([
  "update:visible",
  "update:radio",
  "update:selectIndex",
  "update:panelColor",
  "update:thresholdStart",
  "update:thresholdEnd",
  "confirm",
  "screenshot",
  "toggleLossMap",
]);

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

const draftRadio = ref(Number(props.radio) || 0);
const draftThresholdStart = ref(props.thresholdStart);
const draftThresholdEnd = ref(props.thresholdEnd);

const activeColors = computed(() => {
  const item = props.colorBarList[draftRadio.value] as any;
  return item?.colors || [];
});

const colorStops = computed(() => {
  const colors = activeColors.value;
  if (!colors.length) return "";
  return colors
    .map((color: any, index: number) => {
      const position = (index / Math.max(colors.length - 1, 1)) * 100;
      return `${color.color} ${position}%`;
    })
    .join(", ");
});

const horizontalGradientStyle = computed(() => ({
  background: colorStops.value ? `linear-gradient(to right, ${colorStops.value})` : "transparent",
}));

const verticalGradientStyle = computed(() => ({
  background: colorStops.value ? `linear-gradient(to bottom, ${colorStops.value})` : "transparent",
}));

const ribbonStyle = (item: any) => {
  const colors = item?.colors || [];
  if (!colors.length) return {};
  const stops = colors
    .map((color: any, index: number) => {
      const position = (index / Math.max(colors.length - 1, 1)) * 100;
      return `${color.color} ${position}%`;
    })
    .join(", ");
  return { background: `linear-gradient(to right, ${stops})` };
};

const selectRibbon = (index: number) => {
  draftRadio.value = index;
};

const handleCancel = () => {
  setVisible(false);
};

const handleConfirm = () => {
  emit("update:radio", draftRadio.value);
  emit("update:thresholdStart", draftThresholdStart.value);
  emit("update:thresholdEnd", draftThresholdEnd.value);
  emit("confirm", {
    radio: draftRadio.value,
    thresholdStart: draftThresholdStart.value,
    thresholdEnd: draftThresholdEnd.value,
  });
};

const syncDrafts = () => {
  draftRadio.value = Number(props.radio) || 0;
  draftThresholdStart.value = props.thresholdStart;
  draftThresholdEnd.value = props.thresholdEnd;
};

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 520;
  const gap = 12;
  const anchor = document.querySelector(props.anchorSelector) as HTMLElement | null;
  if (anchor) {
    const rect = anchor.getBoundingClientRect();
    const x = Math.max(16, Math.round(rect.left - width - gap));
    const y = Math.max(16, Math.min(
      window.innerHeight - height - 16,
      Math.round(rect.top + rect.height / 2 - height / 2)
    ));
    return { x, y };
  }
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
  () => props.visible,
  (val) => {
    if (val) {
      syncDrafts();
      centerPanel();
    }
  }
);

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

onBeforeUnmount(() => {
  stopDrag();
});
</script>

<style lang="scss" scoped>
.loss-config {
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
    display: flex;
    flex-direction: column;
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
    font-size: 20px;
    font-weight: 600;
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

    svg { width: 18px; height: 18px; }

    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
  }

  &__body {
    display: flex;
    gap: 16px;
    min-width: 0;
  }

  &__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  &__card {
    padding: 14px 14px 12px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  &__card-title {
    margin: 0 0 12px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    white-space: nowrap;
  }

  &__controls {
    display: flex;
    align-items: center;
    gap: 20px;
    min-height: 52px;
    padding: 8px 18px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(180, 200, 220, 0.12);
  }

  &__shot {
    height: 36px;
    padding: 0 18px;
    border-radius: 999px;
    border: 1px solid rgba(180, 200, 220, 0.22);
    background: rgba(26, 34, 44, 0.72);
    color: rgba(235, 240, 245, 0.95);
    font-size: 13px;
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;

    svg { width: 16px; height: 16px; flex-shrink: 0; }

    &:hover:not(:disabled) {
      background: rgba(48, 56, 66, 0.95);
      color: #ffffff;
    }

    &:disabled {
      opacity: 0.4;
      cursor: default;
    }
  }

  &__divider {
    width: 1px;
    height: 22px;
    background: rgba(255, 255, 255, 0.16);
    flex-shrink: 0;
  }

  &__toggle {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    line-height: 1;
    color: rgba(235, 240, 245, 0.92);
    white-space: nowrap;
  }

  &__ribbons {
    max-height: 156px;
    overflow-y: auto;
    padding: 2px;
    border: 1px solid rgba(180, 200, 220, 0.16);
    border-radius: 8px;
    background: rgba(8, 12, 16, 0.35);
    display: flex;
    flex-direction: column;
    gap: 2px;

    scrollbar-width: thin;
    scrollbar-color: rgba(90, 96, 104, 0.95) rgba(18, 22, 28, 0.9);

    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background: rgba(18, 22, 28, 0.9);
      border-radius: 8px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(72, 78, 86, 0.95);
      border-radius: 8px;
      border: 1px solid rgba(0, 0, 0, 0.35);

      &:hover {
        background: rgba(96, 102, 110, 0.98);
      }
    }
  }

  &__ribbon {
    width: 100%;
    padding: 0;
    border: 1px solid transparent;
    background: transparent;
    cursor: pointer;
    display: block;
    line-height: 0;

    &.is-active .loss-config__ribbon-bar {
      box-shadow: inset 0 0 0 1px #00a2ff;
    }
  }

  &__ribbon-bar {
    display: block;
    width: 100%;
    height: 12px;
    border-radius: 1px;
  }

  &__gradient-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11px;
    color: rgba(190, 200, 212, 0.75);
  }

  &__range {
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 0;
  }

  &__field {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
    min-width: 0;
    font-size: 13px;
    color: rgba(235, 240, 245, 0.92);
  }

  &__field-label {
    flex: 0 0 auto;
    white-space: nowrap;
    line-height: 1;
  }

  &__dash {
    flex: 0 0 auto;
    color: rgba(190, 200, 212, 0.55);
    line-height: 1;
  }

  &__field :deep(.el-input) {
    flex: 1;
    min-width: 0;
  }

  &__field :deep(.el-input__wrapper) {
    border-radius: 999px !important;
    min-height: 36px;
    padding: 0 16px;
  }

  &__legend {
    width: 112px;
    flex-shrink: 0;
    padding: 12px 10px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__legend-title {
    font-size: 12px;
    font-weight: 600;
    color: rgba(235, 240, 245, 0.92);
    margin-bottom: 10px;
    text-align: center;
  }

  &__legend-body {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
  }

  &__legend-bar {
    width: 18px;
    height: 280px;
    border-radius: 999px;
    border: 1px solid rgba(180, 200, 220, 0.18);
  }

  &__legend-scale {
    height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  &__legend-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: rgba(235, 240, 245, 0.75);
  }

  &__legend-line {
    width: 6px;
    height: 1px;
    background: rgba(235, 240, 245, 0.35);
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    gap: 12px;
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

    &:disabled {
      opacity: 0.6;
      cursor: default;
    }

    &--ghost {
      min-width: 72px;
      height: 40px;
      padding: 0 16px;
      border-radius: 8px;
      background: rgba(38, 44, 53, 0.92);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: rgba(235, 240, 245, 0.92);

      &:hover { background: rgba(48, 56, 66, 0.95); }
    }

    &--primary {
      min-width: 120px;
      height: 44px;
      padding: 0 16px 0 20px;
      border-radius: 999px;
      background: linear-gradient(90deg, #00a2ff 0%, #3b82f6 100%);
      box-shadow: 0 8px 24px rgba(0, 162, 255, 0.38);
      font-weight: 600;

      &:hover:not(:disabled) {
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

    svg { width: 14px; height: 14px; }
  }

  :deep(.el-input__wrapper) {
    background: rgba(26, 34, 44, 0.72) !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 36px;
  }

  :deep(.el-input__inner) {
    color: #ffffff !important;
    font-size: 12px !important;
  }

  :deep(.el-switch.is-checked .el-switch__core) {
    background-color: #00a2ff !important;
    border-color: #00a2ff !important;
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
