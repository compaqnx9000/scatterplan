<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="loss-config"
      :style="panelStyle"
    >
      <div class="loss-config__panel">
        <div class="loss-config__edge"></div>
        <div class="loss-config__header" @mousedown="startDrag">
          <div class="loss-config__heading">
            <div class="loss-config__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M4 18h16M6 14l3-4 3 3 4-6 4 7"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="loss-config__title">传输损耗配置</h2>
              <p class="loss-config__subtitle">Color bar and threshold for loss map.</p>
            </div>
          </div>
          <button class="loss-config__icon-btn" type="button" title="关闭" @click="handleCancel" @mousedown.stop>
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
            <section class="loss-config__section">
              <div class="loss-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M5 7h14M5 12h14M5 17h10"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <h3>通用控制</h3>
              </div>
              <div class="loss-config__fields">
                <div class="loss-config__range-grid">
                  <div class="loss-config__field-block">
                    <div class="loss-config__label">截图</div>
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
                      <span>截图</span>
                    </button>
                  </div>
                  <div class="loss-config__field-block">
                    <div class="loss-config__label">损耗图显隐</div>
                    <button
                      class="loss-config__toggle-btn"
                      :class="{ 'is-active': lossMapVisible }"
                      type="button"
                      :disabled="!canToggleLossMap"
                      @click="$emit('toggleLossMap', !lossMapVisible)"
                    >
                      {{ lossMapVisible ? "显示" : "隐藏" }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <section class="loss-config__section">
              <div class="loss-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M4 7h16v3H4zm0 5h16v3H4zm0 5h16v3H4z"
                    fill="currentColor"
                    opacity="0.85"
                  />
                </svg>
                <h3>色条配置</h3>
              </div>
              <div class="loss-config__fields">
                <div class="loss-config__field-block">
                  <div class="loss-config__label loss-config__label--row">
                    <span>色条方案</span>
                    <span class="loss-config__label-hint">{{ draftRadio + 1 }} / {{ colorBarList.length || 0 }}</span>
                  </div>
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
                </div>
              </div>
            </section>

            <section class="loss-config__section">
              <div class="loss-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M6 18V9l4 3 4-5 4 4v7H6z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linejoin="round"
                  />
                </svg>
                <h3>传输损耗阈值</h3>
              </div>
              <div class="loss-config__fields">
                <div class="loss-config__range-grid">
                  <div class="loss-config__field-block">
                    <div class="loss-config__label">Min</div>
                    <el-input v-model="draftThresholdStart">
                      <template #suffix><span class="loss-config__unit">dB</span></template>
                    </el-input>
                  </div>
                  <div class="loss-config__field-block">
                    <div class="loss-config__label">Max</div>
                    <el-input v-model="draftThresholdEnd">
                      <template #suffix><span class="loss-config__unit">dB</span></template>
                    </el-input>
                  </div>
                </div>
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
          <button class="loss-config__btn loss-config__btn--ghost" type="button" @click="handleCancel">
            取消
          </button>
          <button
            class="loss-config__btn loss-config__btn--primary"
            type="button"
            :disabled="btnLoading"
            @click="handleConfirm"
          >
            <svg v-if="!btnLoading" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M5.4 12.4 10 17l8.6-9.2"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            {{ btnLoading ? "处理中" : "确认" }}
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
const PANEL_WIDTH = 640;

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
  width: min(640px, calc(100vw - 48px));
  pointer-events: all;
  box-sizing: border-box;

  &__panel {
    position: relative;
    width: 100%;
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
    display: flex;
    gap: 16px;
    min-width: 0;
    padding: 20px 24px;
  }

  &__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  &__section {
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
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #ffffff !important;
      white-space: nowrap;
    }
  }

  &__fields {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  &__field-block {
    min-width: 0;
  }

  &__label {
    display: block;
    margin-bottom: 6px;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 11px;
    font-weight: 500;
    line-height: 14px;
    color: #c0c8c3;

    &--row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 0;
      color: #ffffff;
      min-height: 28px;
    }
  }

  &__label-hint {
    font-family: Inter, sans-serif;
    font-size: 12px;
    color: #9ddf2e;
    white-space: nowrap;
  }

  &__shot {
    width: 100%;
    height: 40px;
    padding: 0 12px;
    border-radius: 0.5rem;
    border: 1px solid #404945;
    background: transparent;
    color: #c0c8c3 !important;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s ease;

    svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    &:hover:not(:disabled) {
      color: #ffffff !important;
      background: rgba(45, 55, 49, 0.5);
      border-color: #404945;
    }

    &:disabled {
      opacity: 0.4;
      cursor: default;
    }
  }

  &__toggle-btn {
    width: 100%;
    height: 40px;
    padding: 0 12px;
    border-radius: 0.5rem;
    border: 1px solid #404945;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;
    transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;

    &:hover:not(:disabled):not(.is-active) {
      color: #dae5dc;
      border-color: #8a938e;
    }

    &.is-active {
      border-color: rgba(157, 223, 46, 0.55);
      background: rgba(157, 223, 46, 0.1);
      color: #9ddf2e;
      font-weight: 600 !important;
    }

    &:disabled {
      opacity: 0.4;
      cursor: default;
    }
  }

  &__ribbons {
    max-height: 168px;
    overflow-y: auto;
    padding: 6px;
    border: 1px solid rgba(64, 73, 69, 0.5);
    border-radius: 0.5rem;
    background: #07100b;
    display: flex;
    flex-direction: column;
    gap: 4px;
    scrollbar-width: thin;
    scrollbar-color: rgba(90, 96, 104, 0.95) rgba(18, 22, 28, 0.9);

    &::-webkit-scrollbar { width: 8px; }
    &::-webkit-scrollbar-track {
      background: rgba(18, 22, 28, 0.9);
      border-radius: 8px;
    }
    &::-webkit-scrollbar-thumb {
      background: rgba(72, 78, 86, 0.95);
      border-radius: 8px;
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
      box-shadow: inset 0 0 0 1px #9ddf2e;
    }
  }

  &__ribbon-bar {
    display: block;
    width: 100%;
    height: 12px;
    border-radius: 2px;
  }

  &__gradient-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 11px;
    color: #c0c8c3;
  }

  &__range-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  &__unit {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 13px !important;
    color: #a1d1bf !important;
    pointer-events: none;
  }

  &__field-block :deep(.el-input__wrapper) {
    border-radius: 0.5rem !important;
    min-height: 42px;
    padding: 0 12px;
    background: #07100b !important;
    border: 1px solid rgba(64, 73, 69, 0.5) !important;
    box-shadow: none !important;
  }

  &__field-block :deep(.el-input__wrapper.is-focus) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    box-shadow: none !important;
  }

  &__field-block :deep(.el-input__inner) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    color: #dae5dc !important;
    font-size: 16px !important;
  }

  &__legend {
    width: 112px;
    flex-shrink: 0;
    padding: 12px 10px;
    border-radius: 0.5rem;
    background: #07100b;
    border: 1px solid rgba(64, 73, 69, 0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__legend-title {
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #ffffff;
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
    border: 1px solid rgba(64, 73, 69, 0.5);
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
    color: #c0c8c3;
  }

  &__legend-line {
    width: 6px;
    height: 1px;
    background: rgba(192, 200, 195, 0.45);
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

    &:disabled {
      opacity: 0.6;
      cursor: default;
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

      &:hover:not(:disabled) {
        background: #b2f746;
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(157, 223, 46, 0.6);
      }
    }
  }

  :deep(.el-input__inner) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    color: #dae5dc !important;
    font-size: 14px !important;
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
