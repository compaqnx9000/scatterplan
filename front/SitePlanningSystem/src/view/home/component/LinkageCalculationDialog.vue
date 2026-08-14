<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="station-config"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <button
          class="station-config__nav is-prev"
          type="button"
          title="上一页"
          @click.stop="prevPage"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M14.5 6.5 8.5 12l6 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <button
          class="station-config__nav is-next"
          type="button"
          title="下一页"
          @click.stop="nextPage"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9.5 6.5 15.5 12l-6 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__title">链路计算</div>
          <div class="station-config__dots">
            <span v-for="(name, idx) in pageNames" :key="name" :class="{ 'is-active': pageIndex === idx }"></span>
          </div>
          <div class="station-config__header-actions">
            <button class="station-config__export" type="button" title="导出" @click="$emit('export')" @mousedown.stop>
              导出
            </button>
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
        </div>

        <el-form :model="form" label-position="top" class="station-config__form">
          <div class="station-config__viewport">
            <transition :name="pageDir === 'next' ? 'page-next' : 'page-prev'">
              <section v-if="pageIndex === 0" key="input" class="station-config__card">
            <h3 class="station-config__card-title">单链路输入</h3>
            <div class="station-config__grid">
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
              <el-form-item label="发射天线增益（dB）">
                <el-input :model-value="display(form.tx_gain)" readonly />
              </el-form-item>
              <el-form-item label="接收天线增益（dB）">
                <el-input :model-value="display(form.rx_gain)" readonly />
              </el-form-item>
              <el-form-item label="信号频率（MHz）">
                <el-input :model-value="display(form.freq)" readonly />
              </el-form-item>
              <el-form-item label="发射功率（W）">
                <el-input :model-value="display(form.trans_power)" readonly />
              </el-form-item>
              <el-form-item label="发射经度（°）">
                <el-input :model-value="display(form.lng)" readonly />
              </el-form-item>
              <el-form-item label="发射纬度（°）">
                <el-input :model-value="display(form.lat)" readonly />
              </el-form-item>
              <el-form-item label="接收经度（°）">
                <el-input :model-value="display(rxLng)" readonly />
              </el-form-item>
              <el-form-item label="接收纬度（°）">
                <el-input :model-value="display(rxLat)" readonly />
              </el-form-item>
            </div>
              </section>

              <section v-else-if="pageIndex === 1" key="output" class="station-config__card">
            <h3 class="station-config__card-title">单链路输出</h3>
            <div class="station-config__grid">
              <el-form-item label="通信距离（km）">
                <el-input :model-value="display(form.distance)" readonly />
              </el-form-item>
              <el-form-item label="散射角（°）">
                <el-input :model-value="display(form.theta_scatter)" readonly />
              </el-form-item>
              <el-form-item label="区域类型">
                <el-input :model-value="display(form.area)" readonly />
              </el-form-item>
              <el-form-item label="链路传播可靠度（%）">
                <el-input :model-value="display(form.reliability)" readonly />
              </el-form-item>
              <el-form-item label="发射天线仰角（°）">
                <el-input :model-value="display(form.tx_theta)" readonly />
              </el-form-item>
              <el-form-item label="发射点障碍物距离（km）">
                <el-input :model-value="display(form.tx_barrier_distance)" readonly />
              </el-form-item>
              <el-form-item label="路径损耗中值（dB）">
                <el-input :model-value="display(form.median_loss)" readonly />
              </el-form-item>
              <el-form-item label="接收天线仰角（°）">
                <el-input :model-value="display(form.rx_theta)" readonly />
              </el-form-item>
              <el-form-item label="接收点障碍物距离（km）">
                <el-input :model-value="display(form.rx_barrier_distance)" readonly />
              </el-form-item>
              <el-form-item label="接收功率（dBm）">
                <el-input :model-value="display(form.recv_power)" readonly />
              </el-form-item>
              <el-form-item label="发射天线方位角（°）">
                <el-input :model-value="display(form.tx_azimuth)" readonly />
              </el-form-item>
              <el-form-item label="发射点障碍物高差（m）">
                <el-input :model-value="display(form.tx_barrier_height)" readonly />
              </el-form-item>
              <el-form-item label="信号衰落余值（dB）">
                <el-input :model-value="display(form.residual_value)" readonly />
              </el-form-item>
              <el-form-item label="接收天线方位角（°）">
                <el-input :model-value="display(form.rx_azimuth)" readonly />
              </el-form-item>
              <el-form-item label="接收点障碍物高差（m）">
                <el-input :model-value="display(form.rx_barrier_height)" readonly />
              </el-form-item>
            </div>
              </section>

              <section v-else key="profile" class="station-config__card">
            <h3 class="station-config__card-title">剖面图</h3>
            <div class="station-config__image-wrap">
              <img v-if="form.image_url" :src="form.image_url + '?t=' + time" alt="剖面图" />
              <div v-else class="station-config__empty">暂无剖面图</div>
            </div>
              </section>
            </transition>
          </div>
        </el-form>

        <div class="station-config__footer">
          <div class="station-config__footer-left">
            <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
              取消
            </button>
          </div>
          <button class="station-config__btn station-config__btn--primary" type="button" @click="$emit('confirm')">
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
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

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
const PANEL_WIDTH = 1080;
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
  pointer-events: all;
  box-sizing: border-box;

  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  &__nav {
    position: absolute;
    top: 50%;
    z-index: 2;
    width: 40px;
    height: 40px;
    transform: translateY(-50%);
    border: 1px solid rgba(180, 200, 220, 0.18);
    border-radius: 50%;
    background: rgba(26, 34, 44, 0.92);
    color: rgba(235, 240, 245, 0.92);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 18px;
      height: 18px;
    }

    &.is-prev {
      left: 8px;
    }

    &.is-next {
      right: 8px;
    }

    &:hover {
      border-color: rgba(0, 162, 255, 0.45);
      color: #ffffff;
    }
  }

  &__dots {
    display: flex;
    align-items: center;
    gap: 6px;

    span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.22);
      transition: width 0.28s ease, background 0.28s ease, border-radius 0.28s ease;

      &.is-active {
        width: 16px;
        border-radius: 999px;
        background: #00a2ff;
      }
    }
  }

  &__panel {
    position: relative;
    width: 100%;
    height: 600px;
    max-height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 22px 52px 20px;
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
    margin-bottom: 18px;
    cursor: move;
    user-select: none;
    gap: 12px;
    flex-shrink: 0;
  }

  &__title {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    min-width: 0;
    flex: 1;
  }

  &__header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    flex: 1;
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

    svg { width: 18px; height: 18px; }

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
    padding: 14px 14px 10px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  &__card-title {
    margin: 0 0 10px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
  }

  &__export {
    height: 28px;
    padding: 0 12px;
    border-radius: 8px;
    border: 1px solid rgba(180, 200, 220, 0.18);
    background: rgba(26, 34, 44, 0.72);
    color: #8ec8ff;
    font-size: 12px;
    cursor: pointer;
    flex-shrink: 0;

    &:hover {
      background: rgba(48, 56, 66, 0.95);
      color: #b7dcff;
    }
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0 12px;
    width: 100%;
  }

  &__image-wrap {
    width: 100%;
    flex: 1;
    min-height: 0;
    border-radius: 8px;
    overflow: hidden;
    background: rgba(26, 34, 44, 0.72);
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      display: block;
      max-width: 100%;
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
    }
  }

  &__empty {
    color: rgba(190, 200, 212, 0.7);
    font-size: 12px;
    padding: 40px 0;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    gap: 12px;
    flex-shrink: 0;
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

    svg { width: 14px; height: 14px; }
  }

  :deep(.el-form-item) {
    margin-bottom: 12px;
    width: 100%;
  }

  :deep(.el-form-item__content) {
    width: 100% !important;
    margin-left: 0 !important;
  }

  :deep(.el-form-item__label) {
    color: rgba(190, 200, 212, 0.88);
    font-size: 10px;
    line-height: 1.2;
    margin-bottom: 6px !important;
    padding: 0;
  }

  :deep(.station-config__form .el-input),
  :deep(.station-config__form .el-select),
  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-select__wrapper) {
    width: 100% !important;
    max-width: 100% !important;
  }

  :deep(.station-config__form .el-input__wrapper),
  :deep(.station-config__form .el-select__wrapper) {
    background: rgba(26, 34, 44, 0.72) !important;
    background-image: none !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 36px;
  }

  :deep(.station-config__form .el-input__inner),
  :deep(.station-config__form .el-select__selected-item),
  :deep(.station-config__form .el-select__placeholder) {
    color: #ffffff !important;
    font-size: 12px !important;
  }
}

.page-next-enter-active,
.page-next-leave-active,
.page-prev-enter-active,
.page-prev-leave-active {
  transition: transform 0.38s cubic-bezier(0.22, 1, 0.36, 1);
}

.page-next-enter-from {
  transform: translateX(100%);
}

.page-next-leave-to {
  transform: translateX(-100%);
}

.page-prev-enter-from {
  transform: translateX(-100%);
}

.page-prev-leave-to {
  transform: translateX(100%);
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
  .station-config__grid {
    grid-template-columns: 1fr;
  }
}
</style>
