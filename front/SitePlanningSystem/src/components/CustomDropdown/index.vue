<template>
  <div class="custom-dropdown" ref="dropdownRef">
    <!-- 触发元素 -->
    <div 
      class="custom-dropdown__trigger"
      :class="triggerClass"
      @click="handleTriggerClick"
      @mouseenter="handleTriggerMouseEnter"
      @mouseleave="handleTriggerMouseLeave"
      :disabled="disabled"
      :style="disabled ? { cursor: 'not-allowed', opacity: 0.7 } : {}"
    >
      <slot />
      <i class="custom-dropdown__icon" :class="iconClass"></i>
    </div>
    
    <!-- 下拉菜单 -->
    <div 
      ref="menuRef"
      class="custom-dropdown__menu"
      :class="[menuClass, placement, { 'is-visible': isVisible }]"
      :style="menuStyles"
      @click.stop
    >
      <slot name="menu" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

// 定义 props
const props = defineProps<{
  /** 触发方式：click 或 hover */
  trigger?: 'click' | 'hover';
  /** 下拉菜单位置：bottom、top、left、right */
  placement?: 'bottom' | 'top' | 'left' | 'right';
  /** 是否禁用下拉菜单 */
  disabled?: boolean;
  /** 自定义菜单类名 */
  menuClass?: string;
  /** 自定义触发元素类名 */
  triggerClass?: string;
}>();

// 定义 emits
const emit = defineEmits<{
  /** 选择菜单项时触发 */
  (e: 'select', value: any): void;
  /** 菜单打开时触发 */
  (e: 'open'): void;
  /** 菜单关闭时触发 */
  (e: 'close'): void;
}>();

// 状态管理
const isVisible = ref(false);
const dropdownRef = ref<any>(null);
const menuRef = ref<any>(null);
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

// 计算属性 - 箭头图标类名
const iconClass = computed(() => {
  switch (props.placement) {
    case 'top':
      return 'arrow-up';
    case 'bottom':
      return 'arrow-down';
    case 'left':
      return 'arrow-left';
    case 'right':
      return 'arrow-right';
    default:
      return 'arrow-down';
  }
});

// 计算属性 - 菜单样式
const menuStyles = computed(() => {
  return {};
});

// 切换菜单显示状态
const toggleMenu = (show?: boolean) => {
  if (props.disabled) return;
  
  const shouldShow = show !== undefined ? show : !isVisible.value;
  
  if (shouldShow && !isVisible.value) {
    isVisible.value = true;
    emit('open');
    setupClickOutsideListener();
  } else if (!shouldShow && isVisible.value) {
    isVisible.value = false;
    emit('close');
    removeClickOutsideListener();
  }
};

// 处理点击触发
const handleTriggerClick = () => {
  if (props.trigger === 'click' || !props.trigger) {
    toggleMenu();
  }
};

// 处理鼠标进入（悬停触发）
const handleTriggerMouseEnter = () => {
  if (props.trigger === 'hover') {
    toggleMenu(true);
  }
};

// 处理鼠标离开（悬停触发）
const handleTriggerMouseLeave = () => {
  if (props.trigger === 'hover') {
    toggleMenu(false);
  }
};

// 设置点击外部关闭菜单的监听
const setupClickOutsideListener = () => {
  clickOutsideHandler = (e: MouseEvent) => {
    const dropdownEl = dropdownRef.value;
    const menuEl = menuRef.value;
    
    if (dropdownEl && menuEl && 
        !dropdownEl.contains(e.target as Node) && 
        !menuEl.contains(e.target as Node)) {
      toggleMenu(false);
    }
  };
  
  document.addEventListener('click', clickOutsideHandler);
};

// 移除点击外部监听
const removeClickOutsideListener = () => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
    clickOutsideHandler = null;
  }
};

// 生命周期 - 组件卸载时清理
onUnmounted(() => {
  removeClickOutsideListener();
});

// 暴露方法给父组件
defineExpose({
  toggleMenu,
  show: () => toggleMenu(true),
  hide: () => toggleMenu(false)
});
</script>

<style scoped>
.custom-dropdown {
  position: relative;
  display: inline-block;
}

.custom-dropdown__trigger {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.custom-dropdown__icon {
  margin-left: 4px;
  transition: transform 0.2s;
  font-style: normal;
}

/* 箭头图标样式 */
.arrow-down::before {
  content: "▼";
  font-size: 0.8em;
}

.arrow-up::before {
  content: "▲";
  font-size: 0.8em;
}

.arrow-left::before {
  content: "◀";
  font-size: 0.8em;
}

.arrow-right::before {
  content: "▶";
  font-size: 0.8em;
}

/* 菜单基础样式 */
.custom-dropdown__menu {
  position: absolute;
  z-index: 1000;
  display: none;
  min-width: 120px;
  padding: 6px 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: opacity 0.2s, transform 0.2s;
}

/* 菜单显示状态 */
.custom-dropdown__menu.is-visible {
  display: block;
  animation: fadeIn 0.2s ease-in-out;
}

/* 位置相关样式 */
.custom-dropdown__menu.bottom {
  top: 100%;
  left: 0;
  margin-top: 4px;
}

.custom-dropdown__menu.top {
  bottom: 100%;
  left: 0;
  margin-bottom: 4px;
}

.custom-dropdown__menu.left {
  top: 0;
  right: 100%;
  margin-right: 4px;
}

.custom-dropdown__menu.right {
  top: 0;
  left: 100%;
  margin-left: 4px;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
