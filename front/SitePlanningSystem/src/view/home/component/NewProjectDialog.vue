<template>
  <transition name="station-fade">
    <div
      v-if="visible"
      ref="panelRef"
      class="new-project"
      :style="panelStyle"
    >
      <div class="new-project__panel">
        <div class="new-project__edge"></div>

        <div class="new-project__header" @mousedown="startDrag">
          <div class="new-project__heading">
            <div class="new-project__badge">
              <span class="material-symbols-outlined icon-fill">create_new_folder</span>
            </div>
            <div>
              <h2 class="new-project__title">新建工程</h2>
              <p class="new-project__subtitle">Create a new project for propagation planning.</p>
            </div>
          </div>
          <button class="new-project__icon-btn new-project__icon-btn--close" type="button" title="关闭" @click="setVisible(false)" @mousedown.stop>
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="new-project__form"
          require-asterisk-position="right"
          :show-message="false"
          @submit.prevent
        >
          <div class="new-project__section-head">
            <svg class="new-project__section-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M4 6.5A2.5 2.5 0 0 1 6.5 4H10l1.8 1.8H17.5A2.5 2.5 0 0 1 20 8.3v9.2A2.5 2.5 0 0 1 17.5 20h-11A2.5 2.5 0 0 1 4 17.5V6.5Z"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linejoin="round"
              />
            </svg>
            <h3>Project Info</h3>
          </div>
          <el-form-item label="工程名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入工程名称"
              clearable
              @keyup.enter="handleConfirm"
            />
          </el-form-item>
        </el-form>

        <div class="new-project__footer">
          <button class="new-project__btn new-project__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button class="new-project__btn new-project__btn--primary" type="button" @click="handleConfirm">
            <span class="material-symbols-outlined">check</span>
            确认
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
const PANEL_WIDTH = 560;

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
    position: relative;
    width: 100%;
    display: flex;
    flex-direction: column;
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
    padding: 20px 24px;
    border-bottom: 1px solid rgba(64, 73, 69, 0.2);
    background: rgba(45, 55, 49, 0.5);
    cursor: move;
    user-select: none;
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

    .material-symbols-outlined {
      font-size: 14px;
    }
  }

  &__title {
    margin: 0;
    font-family: Inter, sans-serif;
    font-size: 24px;
    font-weight: 600;
    line-height: 32px;
    color: #dae5dc;
  }

  &__subtitle {
    margin: 4px 0 0;
    font-family: Inter, sans-serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    color: #c0c8c3;
    word-break: normal;
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

    .material-symbols-outlined {
      font-size: 14px;
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

  &__form {
    padding: 24px;
  }

  &__section-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(64, 73, 69, 0.2);
    color: #99d4ae;

    .new-project__section-icon {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
      display: block;
    }

    h3 {
      margin: 0;
      font-family: Inter, sans-serif;
      font-size: 12px;
      font-weight: 600;
      line-height: 16px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #dae5dc;
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    padding: 16px 24px;
    border-top: 1px solid rgba(64, 73, 69, 0.2);
    background: rgba(45, 55, 49, 0.3);
  }

  &__btn {
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Inter, sans-serif;
    font-size: 14px;
    line-height: 20px;
    word-break: normal;

    &--ghost {
      padding: 10px 20px;
      border-radius: 0.5rem;
      background: transparent;
      border: 1px solid #404945;
      color: #c0c8c3;
      font-weight: 500;

      &:hover {
        color: #dae5dc;
        background: rgba(45, 55, 49, 0.5);
      }
    }

    &--primary {
      padding: 10px 32px;
      border-radius: 0.5rem;
      background: #9ddf2e;
      color: #213600;
      font-weight: 700;
      gap: 8px;
      box-shadow: 0 0 20px rgba(157, 223, 46, 0.4);
      transition: all 0.2s ease;

      .material-symbols-outlined {
        font-size: 14px;
      }

      &:hover {
        background: #b2f746;
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(157, 223, 46, 0.6);
      }
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 0;
  }

  :deep(.el-form-item__label) {
    font-family: Inter, sans-serif;
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 500;
    line-height: 14px;
    margin-bottom: 6px !important;
    padding: 0;
  }

  :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
  :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
    color: #ffb4ab;
  }

  :deep(.new-project__form .el-input__wrapper) {
    background: #07100b !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    outline: 1px solid rgba(180, 200, 220, 0.18);
    outline-offset: -1px;
    border-radius: 8px !important;
    box-shadow: none !important;
    min-height: 40px;
    padding: 8px 12px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease, outline-color 0.15s ease;
  }

  :deep(.new-project__form .el-input__wrapper:hover) {
    border-color: rgba(180, 200, 220, 0.32) !important;
    outline-color: rgba(180, 200, 220, 0.32);
    box-shadow: none !important;
  }

  :deep(.new-project__form .el-input__wrapper.is-focus),
  :deep(.new-project__form .el-input__wrapper.is-focus:hover) {
    border-color: #9ddf2e !important;
    outline-color: #9ddf2e;
    box-shadow: 0 0 0 1px #9ddf2e, 0 0 0 3px rgba(157, 223, 46, 0.35) !important;
  }

  :deep(.new-project__form .el-form-item.is-error .el-input__wrapper) {
    border-color: #ffb4ab !important;
    box-shadow: none !important;
  }

  :deep(.el-input__inner) {
    color: #dae5dc !important;
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 20px !important;
    word-break: normal !important;
    user-select: text !important;
    -webkit-user-select: text !important;

    &::placeholder {
      color: rgba(192, 200, 195, 0.7) !important;
      -webkit-text-fill-color: rgba(192, 200, 195, 0.7) !important;
      opacity: 1 !important;
    }

    &::selection {
      background: #9ddf2e !important;
      color: #213600 !important;
    }

    &::-moz-selection {
      background: #9ddf2e !important;
      color: #213600 !important;
    }
  }

  :deep(.new-project__form .el-input),
  :deep(.new-project__form .el-input__wrapper) {
    font-family: Inter, sans-serif !important;
    font-size: 14px !important;
  }

  :deep(.el-input__inner::-webkit-input-placeholder) {
    color: rgba(192, 200, 195, 0.7) !important;
    -webkit-text-fill-color: rgba(192, 200, 195, 0.7) !important;
    opacity: 1 !important;
  }

  :deep(input::placeholder) {
    color: rgba(192, 200, 195, 0.7) !important;
    opacity: 1 !important;
  }

  :deep(.el-input__suffix) {
    color: #c0c8c3;
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
