<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="new-project"
      :style="panelStyle"
    >
      <div class="new-project__panel">
        <div class="new-project__header" @mousedown="startDrag">
          <div class="new-project__title">新建工程</div>
          <button class="new-project__close" type="button" title="关闭" @click="setVisible(false)" @mousedown.stop>
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
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="station-config__form"
          require-asterisk-position="right"
          :show-message="false"
          @submit.prevent
        >
          <section class="new-project__card">
            <el-form-item label="工程名称" prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入工程名称"
                clearable
                @keyup.enter="handleConfirm"
              />
            </el-form-item>
          </section>
        </el-form>

        <div class="new-project__footer">
          <button class="new-project__btn new-project__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button class="new-project__btn new-project__btn--primary" type="button" @click="handleConfirm">
            <span>确认</span>
            <span class="new-project__btn-arrow">
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
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from "vue";
import { validateFileName } from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

const props = defineProps({
  visible: { type: Boolean, default: false },
});

const emit = defineEmits(["update:visible", "confirm"]);

const formRef = ref(null);
const form = reactive({ name: "" });
const rules = {
  name: [
    { required: true, message: "请输入工程名称", trigger: "change" },
    { validator: validateFileName, trigger: ["blur", "change"] },
  ],
};

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 420;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 240;
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

const handleConfirm = async () => {
  const formEl = formRef.value as any;
  if (!formEl) return;
  try {
    await formEl.validate();
  } catch {
    shakeInvalidFormFields(formEl);
    return;
  }
  emit("confirm", form.name.trim());
};

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

watch(
  () => props.visible,
  (val) => {
    if (val) {
      form.name = "";
      nextTick(() => formElClear());
      centerPanel();
    }
  }
);

const formElClear = () => {
  (formRef.value as any)?.clearValidate?.();
};

onBeforeUnmount(() => {
  stopDrag();
});
</script>

<style lang="scss" scoped>
.new-project {
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

  &__card {
    padding: 14px 14px 4px;
    border-radius: 10px;
    background: rgba(18, 24, 31, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    gap: 12px;
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

  :deep(.station-config__form .el-input__wrapper) {
    background: rgba(26, 34, 44, 0.72) !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 36px;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper) {
    border-color: rgba(248, 113, 113, 0.7) !important;
  }

  :deep(.el-input__inner) {
    color: #ffffff !important;
    font-size: 12px !important;
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
