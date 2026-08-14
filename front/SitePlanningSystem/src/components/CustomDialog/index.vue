<template>
  <transition name="fade">
    <div
      class="custom-dialog-wrapper"
      v-if="visible"
      :style="{
        width: width + 'px',
      }"
    >
      <div class="dialog_header">
        <div class="dialog_header_icon">
          <img src="@/assets/images/layout/dialog_hd_icon.png" alt="" />
          <div class="dialog_header_icon_title">{{ title }}</div>
        </div>
        <div class="dialog_header_close" @click="handleClose">
          <el-icon color="#303133"><Close /></el-icon>
        </div>
      </div>
      <div class="dialog_body">
        <el-scrollbar max-height="60vh">
          <slot></slot>
        </el-scrollbar>
        <div class="bottom_btn">
          <!-- <div class="btn cancle" @click="handleClose">
            {{ cancelText }}
          </div> -->
          <el-button v-if="showClose" class="btn cancle" @click="handleClose">{{cancelText}}</el-button>

          <el-button type="primary" v-if="showConfirm" class="btn confirm" :loading="btnLoading" @click="handleConfirm">{{confirmText}}</el-button>
          <!-- <div class="btn confirm" @click="handleConfirm">
            <el-icon v-if="btnLoading"><Loading /></el-icon>
            {{ confirmText }}
          </div> -->
        </div>
      </div>
    </div>
  </transition>
</template>
  
  <script setup lang="ts">
import { useSlots, computed, watch } from "vue";
const props = defineProps({
  // 控制对话框显示/隐藏
  visible: {
    type: Boolean,
    default: false,
  },
  // 对话框标题
  title: {
    type: String,
    default: "",
  },
  // 对话框宽度
  width: {
    type: String,
    default: "50%",
  },
  // 对话框距离顶部的距离
  top: {
    type: String,
    default: "15vh",
  },
  left: {
    type: String,
    default: "15vw",
  },
  // 表头背景图
  headerBgImage: {
    type: String,
    default: "",
  },
  // 表头背景色
  headerBgColor: {
    type: String,
    default: "",
  },
  // 表头文字颜色
  headerTextColor: {
    type: String,
    default: "#fff",
  },
  // 主体背景图
  bodyBgImage: {
    type: String,
    default: "",
  },
  // 主体背景色
  bodyBgColor: {
    type: String,
    default: "#fff",
  },
  // 取消按钮文字
  cancelText: {
    type: String,
    default: "取消",
  },
  // 确认按钮文字
  confirmText: {
    type: String,
    default: "确认",
  },
  // 关闭时是否销毁内容
  destroyOnClose: {
    type: Boolean,
    default: false,
  },
  // 是否显示关闭按钮
  showClose: {
    type: Boolean,
    default: true,
  },
  // 是否显示确认按钮
  showConfirm: {
    type: Boolean,
    default: true,
  },
  // 是否将对话框插入body元素
  appendToBody: {
    type: Boolean,
    default: false,
  },
  // 自定义样式类
  dialogClass: {
    type: String,
    default: "",
  },
  // 确认按钮是否加载中
  btnLoading: {
    type: Boolean,
    default: false,
  },
});
watch(
  () => props.visible,
  (val) => {
    console.log("val", val);
  }
);
// 定义组件事件
const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "close"): void;
  (e: "confirm"): void;
}>();

// 获取插槽信息
const slots = useSlots();

// 计算属性：是否有表头内容（标题或自定义表头插槽）
const hasHeaderContent = computed(() => {
  return !!props.title || !!slots.header;
});
const customStyle = {
  position: "fixed",
  top: props.top + "px",
  left: props.left + "px",
};
// 计算属性：表头样式
const headerStyle = computed(() => {
  const style: Record<string, string> = {
    padding: "16px 20px",
    borderBottom: "1px solid var(--el-border-color)",
    position: "relative",
    minHeight: "60px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  // 应用背景图
  if (props.headerBgImage) {
    style.backgroundImage = `url(${props.headerBgImage})`;
    style.backgroundSize = "cover";
    style.backgroundPosition = "center";
    style.backgroundRepeat = "no-repeat";
  }

  // 应用背景色（如果没有背景图）
  if (!props.headerBgImage && props.headerBgColor) {
    style.backgroundColor = props.headerBgColor;
  }

  return style;
});

// 计算属性：主体样式
const bodyStyle = computed(() => {
  const style: Record<string, string> = {
    padding: "20px",
    maxHeight: "70vh",
    overflowY: "auto",
  };

  // 应用背景图
  if (props.bodyBgImage) {
    style.backgroundImage = `url(${props.bodyBgImage})`;
    style.backgroundSize = "cover";
    style.backgroundPosition = "center";
    style.backgroundRepeat = "no-repeat";
  }

  // 应用背景色（如果没有背景图）
  if (!props.bodyBgImage && props.bodyBgColor) {
    style.backgroundColor = props.bodyBgColor;
  }

  return style;
});
// 1. 初始化时打印
onMounted(() => {
  console.log("组件挂载时的visible值：", props.visible);
});
// 处理可见性变化
const handleVisibleChange = (value: boolean) => {
  emit("update:visible", value);
};

// 处理关闭事件
const handleClose = () => {
  emit("update:visible", false);
  emit("close");
};

// 处理确认事件
const handleConfirm = () => {
  emit("confirm");
  // handleClose();
};
</script>
  
  <style lang="scss" scoped>
.custom-dialog-wrapper {
  position: fixed;

  z-index: 1000; /* 确保在普通元素上方，但不阻塞交互 */
}
:deep(.el-dialog) {
  background-color: none !important;
  padding: 0 !important;
  pointer-events: all;
}
.dialog_header {
  width: 100%;
  height: 40px;
  background: url("@/assets/images/layout/dialog_hd_bg2.png") no-repeat;
  background-size: 100% 100% !important;
  // background-size: cover;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px 0px 24px;
  box-sizing: border-box;

  &_icon {
    display: flex;
    align-items: center;

    &_title {
      font-size: 16px;
      color: #1a2041;
      margin-left: 8px;
    }
  }

  &_close {
    cursor: pointer;
  }
}
.el-dialog {
  padding: 0 !important;
  background-color: transparent;
}
.el-dialog__header {
  padding-bottom: 0 !important;
}
.dialog_body {
  width: 100%;
  background: url("@/assets/images/layout/dialog_content_bg.png") no-repeat;
  background-size: cover;
  cursor: pointer;
  // padding: 0 20px;
  // transform: translate(6px, -10px);
  padding: 20px 16px !important;
  box-sizing: border-box;
  pointer-events: all;
  backdrop-filter: blur(10px);
  // box-shadow: 0px 2px 2px 0px rgba(141, 166, 208, 0.25);
}

.el-form-item {
  margin-right: 0 !important;
}

.bottom_btn {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 40px;

  .btn {
    padding: 0 24px;
    height: 28px;
    border-radius: 2px;
    font-size: 10px;
    font-weight: normal;
    line-height: 24px;
    cursor: pointer;
  }
  .cancle {
    background: linear-gradient(90deg, #ffffff 0%, #ebf4ff 100%),
      linear-gradient(
        180deg,
        rgba(0, 21, 41, 0.4) 0%,
        rgba(12, 34, 54, 0.4) 52%,
        rgba(0, 47, 91, 0.4) 100%
      );

    box-sizing: border-box;
    border: 1px solid #a0ceff;
    color: #1f87e9;
  }
  .confirm {
    background: linear-gradient(90deg, #6db0ff 0%, #60abff 100%),
      linear-gradient(
        180deg,
        rgba(0, 21, 41, 0.4) 0%,
        rgba(26, 71, 114, 0.4) 52%,
        rgba(0, 47, 91, 0.4) 100%
      );

    box-sizing: border-box;
    border: 1px solid #3796ff;
    color: #ffffff;
    margin-left: 12px;
  }
}

/* 淡入效果的CSS过渡 */
.fade-enter-from {
  opacity: 0; /* 初始状态：完全透明 */
}

.fade-enter-active {
  transition: opacity 0.5s ease; /* 过渡动画：0.5秒淡入 */
}

.fade-enter-to {
  opacity: 1; /* 结束状态：完全不透明 */
}
::deep(.el-dialog__body) {
  padding: 0 !important;
}

</style>
  