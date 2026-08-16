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
        <button class="station-config__nav is-prev" type="button" title="上一页" @click.stop="prevPage">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M14.5 6.5 8.5 12l6 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <button class="station-config__nav is-next" type="button" title="下一页" @click.stop="nextPage">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9.5 6.5 15.5 12l-6 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__heading">
            <div class="station-config__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M4 12h16M16 8l4 4-4 4M8 8l-4 4 4 4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="station-config__title">链路计算</h2>
              <p class="station-config__subtitle">{{ pageNames[pageIndex] }}</p>
            </div>
          </div>
          <div class="station-config__dots">
            <span v-for="(name, idx) in pageNames" :key="name" :class="{ 'is-active': pageIndex === idx }"></span>
          </div>
          <div class="station-config__header-actions">
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
        </div>

        <el-form :model="form" label-position="top" class="station-config__form">
          <div class="station-config__viewport">
            <transition :name="pageDir === 'next' ? 'page-next' : 'page-prev'">
              <section v-if="pageIndex === 0" key="input" class="station-config__card">
                <div class="station-config__section-head">
                  <h3>单链路输入</h3>
                </div>
                <div class="station-config__grid station-config__grid--5">
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
                      <template #suffix><span class="station-config__unit">dB</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收天线增益">
                    <el-input :model-value="display(form.rx_gain)" readonly>
                      <template #suffix><span class="station-config__unit">dB</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="信号频率">
                    <el-input :model-value="display(form.freq)" readonly>
                      <template #suffix><span class="station-config__unit">MHz</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="发射功率">
                    <el-input :model-value="display(form.trans_power)" readonly>
                      <template #suffix><span class="station-config__unit">W</span></template>
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
              </section>

              <section v-else-if="pageIndex === 1" key="output" class="station-config__card">
                <div class="station-config__section-head">
                  <h3>单链路输出</h3>
                </div>
                <div class="station-config__grid station-config__grid--5">
                  <el-form-item label="通信距离">
                    <el-input :model-value="display(form.distance)" readonly>
                      <template #suffix><span class="station-config__unit">km</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="散射角">
                    <el-input :model-value="display(form.theta_scatter)" readonly>
                      <template #suffix><span class="station-config__unit">°</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="区域类型">
                    <el-input :model-value="display(form.area)" readonly />
                  </el-form-item>
                  <el-form-item label="链路传播可靠度">
                    <el-input :model-value="display(form.reliability)" readonly>
                      <template #suffix><span class="station-config__unit">%</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="发射天线仰角">
                    <el-input :model-value="display(form.tx_theta)" readonly>
                      <template #suffix><span class="station-config__unit">°</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="发射点障碍物距离">
                    <el-input :model-value="display(form.tx_barrier_distance)" readonly>
                      <template #suffix><span class="station-config__unit">km</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="路径损耗中值">
                    <el-input :model-value="display(form.median_loss)" readonly>
                      <template #suffix><span class="station-config__unit">dB</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收天线仰角">
                    <el-input :model-value="display(form.rx_theta)" readonly>
                      <template #suffix><span class="station-config__unit">°</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收点障碍物距离">
                    <el-input :model-value="display(form.rx_barrier_distance)" readonly>
                      <template #suffix><span class="station-config__unit">km</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收功率">
                    <el-input :model-value="display(form.recv_power)" readonly>
                      <template #suffix><span class="station-config__unit">dBm</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="发射天线方位角">
                    <el-input :model-value="display(form.tx_azimuth)" readonly>
                      <template #suffix><span class="station-config__unit">°</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="发射点障碍物高差">
                    <el-input :model-value="display(form.tx_barrier_height)" readonly>
                      <template #suffix><span class="station-config__unit">m</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="信号衰落余值">
                    <el-input :model-value="display(form.residual_value)" readonly>
                      <template #suffix><span class="station-config__unit">dB</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收天线方位角">
                    <el-input :model-value="display(form.rx_azimuth)" readonly>
                      <template #suffix><span class="station-config__unit">°</span></template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="接收点障碍物高差">
                    <el-input :model-value="display(form.rx_barrier_height)" readonly>
                      <template #suffix><span class="station-config__unit">m</span></template>
                    </el-input>
                  </el-form-item>
                </div>
              </section>

              <section v-else key="profile" class="station-config__card">
                <div class="station-config__section-head">
                  <h3>剖面图</h3>
                </div>
                <div class="station-config__image-wrap">
                  <img v-if="form.image_url" :src="form.image_url + '?t=' + time" alt="剖面图" />
                  <div v-else class="station-config__empty">暂无剖面图</div>
                </div>
              </section>
            </transition>
          </div>
        </el-form>

        <div class="station-config__footer station-config__footer--split">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="$emit('export')">
            导出
          </button>
          <div class="station-config__footer-right">
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
              取消
            </button>
            <button class="station-config__btn station-config__btn--primary" type="button" @click="$emit('confirm')">
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
    </div>
  </transition>
</template>

<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { formatLongitude, formatLatitude } from "@/view/home/service/rules";

const props = defineProps({
  visible: { type: Boolean, default: false },
  form: { type: Object, default: () => ({}) },
  rxLng: { type: [String, Number], default: "" },
  rxLat: { type: [String, Number], default: "" },
  time: { type: [String, Number], default: "" },
});

const emit = defineEmits(["update:visible", "confirm", "export", "changeCommRate"]);

const commRateOptions = [
  "2.4kbps", "9.6kbps", "32kbps", "64kbps", "128kbps", "256kbps", "512kbps",
  "1024kbps", "2Mbps", "4Mbps", "8Mbps", "16Mbps", "34Mbps", "50Mbps",
  "78Mbps", "100Mbps", "155Mbps",
];

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 1120;
const pageNames = ["单链路输入", "单链路输出", "剖面图"];
const pageIndex = ref(0);
const pageDir = ref<"next" | "prev">("next");

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const prevPage = () => {
  pageDir.value = "prev";
  pageIndex.value = (pageIndex.value + pageNames.length - 1) % pageNames.length;
};

const nextPage = () => {
  pageDir.value = "next";
  pageIndex.value = (pageIndex.value + 1) % pageNames.length;
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
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 600;
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
      pageIndex.value = 0;
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
.station-config {
  position: fixed;
  z-index: 1200;
  width: min(1120px, calc(100vw - 48px));
  pointer-events: all;
  box-sizing: border-box;

  &__panel {
    position: relative;
    width: 100%;
    height: 600px;
    max-height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0 48px;
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

  &__nav {
    position: absolute;
    top: 50%;
    z-index: 2;
    width: 36px;
    height: 36px;
    transform: translateY(-50%);
    border: 1px solid rgba(64, 73, 69, 0.5);
    border-radius: 50%;
    background: rgba(12, 21, 16, 0.92);
    color: #c0c8c3;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }

    &.is-prev { left: 8px; }
    &.is-next { right: 8px; }

    &:hover {
      border-color: rgba(157, 223, 46, 0.45);
      color: #9ddf2e;
    }
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin: 0 -48px;
    padding: 18px 24px;
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
    margin: 2px 0 0;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 13px !important;
    color: #c0c8c3 !important;
    white-space: nowrap;
  }

  &__dots {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;

    span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.22);

      &.is-active {
        width: 16px;
        border-radius: 999px;
        background: #9ddf2e;
      }
    }
  }

  &__header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    flex: 1;
    flex-shrink: 0;
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

  &__form {
    width: 100%;
    min-width: 0;
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 16px 0 0;
  }

  &__viewport {
    position: relative;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  &__card {
    position: absolute;
    inset: 0;
    min-width: 0;
    overflow: auto;
    display: flex;
    flex-direction: column;
    padding: 4px 4px 8px;
  }

  &__section-head {
    display: flex;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(64, 73, 69, 0.2);

    h3 {
      margin: 0;
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #ffffff !important;
    }
  }

  &__grid {
    display: grid;
    gap: 0 12px;
    width: 100%;

    &--5 {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
  }

  &__unit {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 13px !important;
    color: #a1d1bf !important;
    pointer-events: none;
    white-space: nowrap;
  }

  &__image-wrap {
    width: 100%;
    flex: 1;
    min-height: 0;
    border-radius: 0.5rem;
    overflow: hidden;
    background: #07100b;
    border: 1px solid rgba(64, 73, 69, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      display: block;
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }

  &__empty {
    color: #c0c8c3;
    font-size: 13px;
    padding: 40px 0;
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    margin: 0 -48px;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(64, 73, 69, 0.2) !important;
    background: rgba(45, 55, 49, 0.3) !important;
    flex-shrink: 0;

    &--split {
      justify-content: space-between;
    }
  }

  &__footer-right {
    display: flex;
    align-items: center;
    gap: 16px;
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
    margin-bottom: 14px;
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

  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-select__wrapper) {
    background: #07100b !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 40px;
  }

  :deep(.station-config__form .el-input__wrapper.is-focus),
  :deep(.station-config__form .el-select__wrapper.is-focused) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    box-shadow: none !important;
  }

  :deep(.station-config__form .el-input__inner),
  :deep(.station-config__form .el-select__selected-item),
  :deep(.station-config__form .el-select__placeholder) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    color: #dae5dc !important;
  }
}

.page-next-enter-active,
.page-next-leave-active,
.page-prev-enter-active,
.page-prev-leave-active {
  transition: transform 0.38s cubic-bezier(0.22, 1, 0.36, 1);
}

.page-next-enter-from { transform: translateX(100%); }
.page-next-leave-to { transform: translateX(-100%); }
.page-prev-enter-from { transform: translateX(-100%); }
.page-prev-leave-to { transform: translateX(100%); }

.station-fade-enter-active,
.station-fade-leave-active {
  transition: opacity 0.2s ease;
}

.station-fade-enter-from,
.station-fade-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .station-config__grid--5 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
