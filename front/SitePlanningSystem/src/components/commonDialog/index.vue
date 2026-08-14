<template>
  <el-dialog
    v-model="dialogVisible"
    :width="dialogWidth"
    :height="dialogHeight"
    append-to-body
    draggable
    align-center
    custom-class="transparent-dialog"
    :show-close="false"
    :modal="true"
    :modal-class="'transparent-modal'"
    @opened="dialogOpened"
    style="background: #000"
  >
    <!-- style="background: rgba(7, 7, 8, 0.8)" -->
    <!-- 自定义头部（含白色关闭按钮） -->
    <template #header>
      <div class="dialog-header">
        <el-icon class="close-icon" @click="closeDialog" :size="40">
          <Close />
        </el-icon>
      </div>
    </template>
    <div class="dialog-content">
      <div v-if="!props.defined" class="chart-container" ref="chartRef"></div>
      <div v-else class="chart-container">
        <slot name="content"></slot>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref } from "vue";
  import { Close } from "@element-plus/icons-vue";
  import * as echarts from "echarts";
  const props = defineProps({
    defined: {
      type: Boolean,
      default: false,
    },
  });
  const emits = defineEmits(["onOpenOpened"]);
  const chartRef = ref<any>(null);
  const dialogVisible = ref(false);
  //   const dialogWidth = computed(() => `${window.innerWidth * 0.6}px`) // 宽度为视口60%
  //   const dialogHeight = computed(() => `${window.innerHeight * 0.6}px`) // 高度为视口60%
  const dialogWidth = ref("70vw");
  const dialogHeight = ref("80vh");
  const options = ref({});
  // 暴露打开/关闭方法
  const openDialog = () => (dialogVisible.value = true);
  const closeDialog = () => (dialogVisible.value = false);
  const dialogOpened = () => {
    emits("onOpenOpened");
    if (props.defined) return;
    const chart = echarts.init(chartRef.value);
    chart.setOption(options.value);
  };
  const initCharts = (option: any) => {
    options.value = option;
  };
  defineExpose({ openDialog, closeDialog, initCharts });
</script>

<style scoped>
  /* 头部样式 */
  .dialog-header {
    display: flex;
    justify-content: flex-end;
    padding: 12px;
  }
  .dialog-content {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .chart-container {
    width: 70vh;
    height: 70vh;
  }
  .close-icon {
    color: white; /* 白色关闭按钮 */
    font-size: 40px;
    cursor: pointer;
  }
</style>
