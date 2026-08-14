<template>
  <div class="map-toolbar" :class="{ 'is-pick-locked': pickLocked, 'has-workflow': stationReady }">
    <div class="map-toolbar__row">
      <button
        class="map-toolbar__btn"
        type="button"
        title="站点配置"
        :disabled="pickLocked"
        @click="openStationConfig"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
            fill="currentColor"
          />
        </svg>
      </button>

      <div
        class="map-toolbar__workflow"
        :class="{ 'is-open': stationReady }"
        :aria-hidden="!stationReady"
      >
        <div class="map-toolbar__vdivider" aria-hidden="true"></div>

        <button
          class="map-toolbar__btn"
          type="button"
          title="单链路计算适配"
          :disabled="pickLocked || !stationReady"
          :tabindex="stationReady ? 0 : -1"
          :class="{ 'is-active': activeWorkflow === 'slp' }"
          @click="openSLP"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M7.5 8.5a3 3 0 1 1 0 6M16.5 8.5a3 3 0 1 0 0 6"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
            <path
              d="M9.2 10.2 14.8 13.8M9.2 13.8 14.8 10.2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <button
          class="map-toolbar__btn"
          type="button"
          title="剖面提取"
          :disabled="pickLocked || !stationReady"
          :tabindex="stationReady ? 0 : -1"
          :class="{ 'is-active': activeWorkflow === 'profile', 'is-loading': profileLoading }"
          @click="openProfile"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M4 18V6M4 18h16"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
            <path
              d="M6.5 14.5 10 9.5l3.2 3.8L17.5 7.5 20 11"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>

        <button
          class="map-toolbar__btn"
          type="button"
          title="区域覆盖计算适配"
          :disabled="pickLocked || !stationReady"
          :tabindex="stationReady ? 0 : -1"
          :class="{ 'is-active': activeWorkflow === 'coverage' }"
          @click="openCoverage"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect x="4.6" y="6.2" width="14.8" height="11.6" rx="2" fill="none" stroke="currentColor" stroke-width="1.6" />
            <circle cx="12" cy="12" r="2.1" fill="currentColor" />
            <path
              d="M12 7.8v8.4M7.8 12h8.4"
              fill="none"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linecap="round"
              opacity="0.7"
            />
          </svg>
        </button>

        <button
          class="map-toolbar__btn"
          type="button"
          title="传输损耗预测"
          :disabled="pickLocked || !stationReady"
          :tabindex="stationReady ? 0 : -1"
          :class="{ 'is-active': activeWorkflow === 'prediction' }"
          @click="openPrediction"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 18.2V8.2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
            <path
              d="M8.2 11.2a5.2 5.2 0 0 1 7.6 0M6.2 8.8a8.2 8.2 0 0 1 11.6 0"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
            <path d="M9.4 18.2h5.2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
          </svg>
        </button>

        <button
          class="map-toolbar__btn"
          type="button"
          title="聚类分析及站点推荐"
          :disabled="pickLocked || !stationReady"
          :tabindex="stationReady ? 0 : -1"
          :class="{ 'is-active': activeWorkflow === 'cluster' }"
          @click="openCluster"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="8" cy="8.2" r="2.1" fill="currentColor" />
            <circle cx="16.2" cy="9.2" r="2.1" fill="currentColor" />
            <circle cx="12" cy="16.4" r="2.1" fill="currentColor" />
            <path
              d="M9.6 9.4 14.4 10.2M9.2 10 11 14.6M14.8 10.8 13 14.6"
              fill="none"
              stroke="currentColor"
              stroke-width="1.4"
              stroke-linecap="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="map-toolbar__col">
    <button
      class="map-toolbar__btn"
      type="button"
      title="图层"
      :disabled="pickLocked"
      :class="{ 'is-active': layerPanelOpen }"
      @click="toggleLayerPanel"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M12 4.2 3.8 8.6 12 13l8.2-4.4L12 4.2Zm0 10.2L4.4 10.4 3.8 10.7 12 15.1l8.2-4.4-.6-.3L12 14.4Zm0 4.1L4.4 14.5l-.6.3L12 19.2l8.2-4.4-.6-.3L12 18.5Z"
          fill="currentColor"
        />
      </svg>
    </button>

    <button
      class="map-toolbar__btn map-toolbar__btn--mode"
      type="button"
      :title="is3D ? '切换到2D' : '切换到3D'"
      :disabled="pickLocked"
      :class="{ 'is-active': is3D }"
      @click="toggleViewMode"
    >
      {{ is3D ? "3D" : "2D" }}
    </button>

    <button
      class="map-toolbar__btn"
      type="button"
      title="测距"
      :disabled="pickLocked"
      :class="{ 'is-active': measuring }"
      @click="toggleMeasure"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M3.2 18.2 18.2 3.2a1.4 1.4 0 0 1 2 2L5.2 20.2a1.4 1.4 0 0 1-2-2Zm3.3-.7 1.1-1.1.8.8-1.1 1.1.3.3 1.1-1.1.8.8-1.1 1.1.3.3 1.1-1.1.8.8-1.1 1.1.4.3 1.1-1.1.8.8-1.1 1.1.9.2 10.4-10.4-.2-.9-1.1 1.1-.8-.8 1.1-1.1-.3-.4-1.1 1.1-.8-.8 1.1-1.1-.3-.3-1.1 1.1-.8-.8 1.1-1.1-.3-.3-1.1 1.1-.8-.8 1.1-1.1Z"
          fill="currentColor"
        />
      </svg>
    </button>

    <div class="map-toolbar__divider"></div>

    <button
      class="map-toolbar__btn"
      type="button"
      title="复位视角"
      :disabled="pickLocked"
      @click="resetView"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M12 3.5 14.2 7H9.8L12 3.5Zm0 17L9.8 17h4.4L12 20.5ZM3.5 12 7 9.8v4.4L3.5 12Zm17 0L17 14.2V9.8L20.5 12Z"
          fill="currentColor"
        />
        <circle cx="12" cy="12" r="2.2" fill="currentColor" />
        <path
          d="M7.2 7.2a6.8 6.8 0 0 1 9.6 0M16.8 16.8a6.8 6.8 0 0 1-9.6 0"
          fill="none"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linecap="round"
        />
      </svg>
    </button>

    <button
      class="map-toolbar__btn"
      type="button"
      title="放大"
      :disabled="pickLocked"
      @click="zoom(true)"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" stroke-width="1.7" />
        <path d="M15.2 15.2 20 20" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        <path d="M10.5 7.8v5.4M7.8 10.5h5.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
    </button>

    <button
      class="map-toolbar__btn"
      type="button"
      title="缩小"
      :disabled="pickLocked"
      @click="zoom(false)"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" stroke-width="1.7" />
        <path d="M15.2 15.2 20 20" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        <path d="M7.8 10.5h5.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
    </button>

    <button class="map-toolbar__btn" type="button" title="帮助" :disabled="pickLocked" @click="showHelp">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.6" />
        <path
          d="M9.6 9.4a2.4 2.4 0 1 1 3.5 2.1c-.7.4-1.1.9-1.1 1.7"
          fill="none"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
        />
        <circle cx="12" cy="16.4" r="1" fill="currentColor" />
      </svg>
    </button>

    <div v-if="layerPanelOpen" class="map-toolbar__panel">
      <button
        v-for="item in basemapOptions"
        :key="item.name"
        type="button"
        class="map-toolbar__panel-item"
        :class="{ 'is-active': item.name === activeBasemap }"
        @click="selectBasemap(item.name)"
      >
        {{ item.name }}
      </button>

      <div class="map-toolbar__panel-divider"></div>

      <button
        type="button"
        class="map-toolbar__panel-item map-toolbar__panel-item--toggle"
        :class="{ 'is-active': roadNetworkVisible }"
        @click="toggleRoadNetwork"
      >
        <span>路网</span>
        <span class="map-toolbar__toggle-state">{{ roadNetworkVisible ? "显示" : "隐藏" }}</span>
      </button>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getCurrentInstance, nextTick, onMounted, onUnmounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { getMapInstance } from "@/assets/util/index";
import { UseoperatingButton } from "@/view/layout/components/map/service/UseoperatingButton";
import { Tool } from "@/components/tool/service";
import { map3dConfig } from "@/view/layout/components/map/config/config";

const currentInstance = getCurrentInstance();
const $bus = currentInstance?.appContext.config.globalProperties.$bus;

const is3D = ref(true);
const measuring = ref(false);
const layerPanelOpen = ref(false);
const activeBasemap = ref("黑色底图");
const roadNetworkVisible = ref(true);
const pickLocked = ref(false);
const stationReady = ref(false);
const activeWorkflow = ref<"slp" | "profile" | "coverage" | "prediction" | "cluster" | "">("");
const profileLoading = ref(false);

const basemapOptions = (map3dConfig.basemaps || [])
  .filter((item: any) => item.type !== "group" || item.layers)
  .filter((item: any) => item.name && item.name !== "地图底图")
  .map((item: any) => ({ name: item.name }));

let operatingButton: UseoperatingButton | null = null;
let measureTool: Tool | null = null;

const waitForMap = async () => {
  for (let i = 0; i < 40; i++) {
    const map = getMapInstance();
    if (map) return map;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  return null;
};

const toggleLayerPanel = () => {
  if (pickLocked.value) return;
  layerPanelOpen.value = !layerPanelOpen.value;
};

const openStationConfig = () => {
  if (pickLocked.value) return;
  layerPanelOpen.value = false;
  $bus?.emit("openLaunchSiteConfig");
};

const openSLP = () => {
  if (pickLocked.value || !stationReady.value) return;
  activeWorkflow.value = "slp";
  $bus?.emit("openSLPComputedDialog");
};

const openProfile = () => {
  if (pickLocked.value || !stationReady.value || profileLoading.value) return;
  activeWorkflow.value = "profile";
  $bus?.emit("openProfileExtract");
};

const openCoverage = () => {
  if (pickLocked.value || !stationReady.value) return;
  activeWorkflow.value = "coverage";
  $bus?.emit("openCoverageDialog");
};

const openPrediction = () => {
  if (pickLocked.value || !stationReady.value) return;
  activeWorkflow.value = "prediction";
  $bus?.emit("runTransmissionLossPrediction");
};

const openCluster = () => {
  if (pickLocked.value || !stationReady.value) return;
  activeWorkflow.value = "cluster";
  $bus?.emit("openClusterDialog");
};

const selectBasemap = (name: string) => {
  if (pickLocked.value || !operatingButton) return;
  operatingButton.selectMap(name);
  activeBasemap.value = name;
  layerPanelOpen.value = false;
};

const toggleRoadNetwork = () => {
  if (pickLocked.value) return;
  roadNetworkVisible.value = !roadNetworkVisible.value;
  $bus?.emit("setMapLayerShow", {
    name: "路网",
    show: roadNetworkVisible.value,
  });
};

const toggleViewMode = () => {
  if (pickLocked.value) return;
  const map = getMapInstance();
  if (!map?.scene) return;
  is3D.value = !is3D.value;
  if (is3D.value) {
    map.scene.morphTo3D(1.2);
  } else {
    map.scene.morphTo2D(1.2);
  }
};

const toggleMeasure = () => {
  if (pickLocked.value || !measureTool) return;
  if (measuring.value) {
    measureTool.clear();
    measuring.value = false;
    return;
  }
  measuring.value = true;
  measureTool.distance();
  ElMessage.info("开始测距，右键或双击结束；再次点击按钮可清除");
};

const resetView = () => {
  if (pickLocked.value) return;
  const map = getMapInstance();
  if (!map) return;
  if (typeof (map as any).flyHome === "function") {
    (map as any).flyHome({ duration: 1.5 });
    return;
  }
  operatingButton?.flyToCenter({
    lng: 105.0,
    lat: 35.0,
    alt: 12000000,
  });
};

const zoom = (zoomIn: boolean) => {
  if (pickLocked.value) return;
  operatingButton?.handleCameraZoomIn(zoomIn);
};

const showHelp = () => {
  if (pickLocked.value) return;
  const helpBtn = document.querySelector(
    ".cesium-navigation-help-button, .cesium-viewer-navigationHelpButton-wrapper button"
  ) as HTMLButtonElement | null;
  if (helpBtn) {
    helpBtn.click();
    return;
  }
  ElMessage.info("鼠标左键旋转，右键平移，滚轮缩放");
};

const onMapPickMode = (active: boolean) => {
  pickLocked.value = !!active;
  if (!active) return;
  layerPanelOpen.value = false;
  if (measuring.value && measureTool) {
    measureTool.clear();
    measuring.value = false;
  }
};

const onStationReady = (ready: boolean) => {
  stationReady.value = !!ready;
  if (!ready) activeWorkflow.value = "";
};

const onProfileLoading = (loading: boolean) => {
  profileLoading.value = !!loading;
};

const onWorkflowActive = (name: "slp" | "profile" | "coverage" | "prediction" | "cluster" | "") => {
  activeWorkflow.value = name || "";
};

const onLogout = () => {
  pickLocked.value = false;
  stationReady.value = false;
  activeWorkflow.value = "";
  profileLoading.value = false;
  layerPanelOpen.value = false;
  if (measuring.value && measureTool) {
    measureTool.clear();
    measuring.value = false;
  } else {
    measureTool?.clear();
  }
};

onMounted(async () => {
  await nextTick();
  $bus?.on("mapPickMode", onMapPickMode);
  $bus?.on("workflowStationReady", onStationReady);
  $bus?.on("workflowProfileLoading", onProfileLoading);
  $bus?.on("workflowActive", onWorkflowActive);
  $bus?.on("Logout", onLogout);
  const map = await waitForMap();
  if (!map) return;
  operatingButton = new UseoperatingButton(map);
  measureTool = new Tool(map);

  const current = (map3dConfig.basemaps || []).find((item: any) => item.show && item.name);
  if (current?.name) activeBasemap.value = current.name;
});

onUnmounted(() => {
  $bus?.off("mapPickMode", onMapPickMode);
  $bus?.off("workflowStationReady", onStationReady);
  $bus?.off("workflowProfileLoading", onProfileLoading);
  $bus?.off("workflowActive", onWorkflowActive);
  $bus?.off("Logout", onLogout);
  measureTool?.destroy();
  measureTool = null;
});
</script>

<style scoped lang="scss">
.map-toolbar {
  --toolbar-ease: cubic-bezier(0.16, 1, 0.3, 1);
  --toolbar-spring: cubic-bezier(0.34, 1.45, 0.64, 1);
  position: absolute;
  left: 18px;
  top: 90px;
  z-index: 120;
  pointer-events: all;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 14px 8px;
  width: max-content;
  min-width: 48px;
  max-width: 48px;
  border-radius: 12px;
  background: rgba(42, 46, 54, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-sizing: border-box;
  transition:
    max-width 0.45s ease,
    padding 0.4s ease,
    gap 0.4s ease,
    background 0.35s ease,
    border-color 0.35s ease,
    box-shadow 0.35s ease,
    border-radius 0.3s ease;

  &.has-workflow {
    max-width: 520px;
    align-items: flex-start;
    padding: 0;
    gap: 12px;
    background: transparent;
    border-color: transparent;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-radius: 0;
    pointer-events: none;
    transition:
      max-width 0.85s var(--toolbar-ease),
      padding 0.7s 0.2s var(--toolbar-ease),
      gap 0.7s 0.18s var(--toolbar-ease),
      background 0.55s 0.22s ease,
      border-color 0.55s 0.22s ease,
      box-shadow 0.55s 0.22s ease,
      border-radius 0.5s 0.2s ease;
  }

  &.is-pick-locked {
    opacity: 0.45;
    pointer-events: none;
  }

  &__row,
  &__col,
  &__panel,
  &__btn {
    pointer-events: all;
  }

  &__row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 0;
    width: 32px;
    min-height: 32px;
    box-sizing: border-box;
    border: 1px solid transparent;
    transition:
      width 0.4s ease,
      background 0.3s ease,
      border-color 0.3s ease,
      box-shadow 0.3s ease,
      padding 0.3s ease,
      border-radius 0.3s ease,
      gap 0.3s ease;
  }

  &.has-workflow &__row,
  &.has-workflow &__col {
    box-sizing: border-box;
    background: rgba(42, 46, 54, 0.62);
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
  }

  &.has-workflow &__row {
    width: auto;
    justify-content: flex-start;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 12px;
    transition:
      width 0.85s var(--toolbar-ease),
      background 0.5s 0.2s ease,
      border-color 0.5s 0.2s ease,
      box-shadow 0.5s 0.2s ease,
      padding 0.55s 0.15s var(--toolbar-ease),
      border-radius 0.5s 0.15s ease,
      gap 0.55s 0.1s var(--toolbar-ease);
  }

  &__workflow {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 6px;
    max-width: 0;
    width: 0;
    min-width: 0;
    flex: 0 0 0;
    margin: 0;
    padding: 0;
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
    transform-origin: left center;
    transform: translateX(-24px);
    transition:
      max-width 0.4s ease,
      opacity 0.25s ease,
      transform 0.35s ease;

    > * {
      flex-shrink: 0;
      opacity: 0;
      transform: translateX(-20px) scale(0.35);
      filter: blur(6px);
      transition:
        opacity 0.2s ease,
        transform 0.25s ease,
        filter 0.2s ease;
    }

    &.is-open {
      max-width: 300px;
      width: auto;
      min-width: 0;
      flex: 0 1 auto;
      opacity: 1;
      transform: none;
      pointer-events: auto;
      transition:
        max-width 0.85s var(--toolbar-ease),
        opacity 0.45s ease,
        transform 0.7s var(--toolbar-ease);

      > * {
        opacity: 1;
        transform: none;
        filter: none;
        transition:
          opacity 0.4s ease,
          transform 0.55s var(--toolbar-spring),
          filter 0.4s ease;
      }

      > *:nth-child(1) { transition-delay: 0.1s; }
      > *:nth-child(2) { transition-delay: 0.2s; }
      > *:nth-child(3) { transition-delay: 0.3s; }
      > *:nth-child(4) { transition-delay: 0.4s; }
      > *:nth-child(5) { transition-delay: 0.5s; }
      > *:nth-child(6) { transition-delay: 0.6s; }
    }
  }

  &__col {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    width: 32px;
    flex-shrink: 0;
    box-sizing: border-box;
    border: 1px solid transparent;
    transition:
      width 0.35s ease,
      padding 0.35s ease,
      background 0.3s ease,
      border-color 0.3s ease,
      box-shadow 0.3s ease,
      border-radius 0.3s ease,
      transform 0.35s ease;
  }

  &.has-workflow &__col {
    width: 46px;
    padding: 8px 6px;
    border-radius: 12px;
    animation: toolbar-col-drop 0.7s 0.18s var(--toolbar-spring) both;
    transition:
      width 0.55s 0.15s var(--toolbar-ease),
      padding 0.55s 0.15s var(--toolbar-ease),
      background 0.5s 0.22s ease,
      border-color 0.5s 0.22s ease,
      box-shadow 0.5s 0.22s ease,
      border-radius 0.5s 0.15s ease,
      transform 0.7s 0.18s var(--toolbar-spring);
  }

  &__vdivider {
    width: 1px;
    height: 22px;
    background: rgba(255, 255, 255, 0.22);
    flex-shrink: 0;
  }

  &__btn {
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 6px;
    padding: 0;
    color: rgba(236, 240, 245, 0.92);
    background: transparent;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease, transform 0.15s ease;

    svg {
      width: 20px;
      height: 20px;
      display: block;
    }

    &:hover:not(:disabled) {
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
    }

    &:disabled {
      opacity: 0.45;
      cursor: default;
    }

    &.is-active {
      background: rgba(0, 162, 255, 0.28);
      color: #fff;
    }

    &.is-loading {
      opacity: 0.7;
    }

    &--mode {
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.02em;
      background: rgba(255, 255, 255, 0.12);

      &.is-active {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }

  &.has-workflow > .map-toolbar__col {
    align-self: flex-start;
  }

  &__divider {
    width: 22px;
    height: 1px;
    background: rgba(255, 255, 255, 0.22);
    margin: 2px 0;
    align-self: center;
  }

  &__panel {
    position: absolute;
    left: calc(100% + 12px);
    top: 0;
    min-width: 128px;
    padding: 8px;
    border-radius: 12px;
    background: rgba(32, 36, 44, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
  }

  &__panel-item {
    width: 100%;
    border: none;
    background: transparent;
    color: rgba(236, 240, 245, 0.9);
    text-align: left;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;

    &:hover,
    &.is-active {
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
    }

    &--toggle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
  }

  &__panel-divider {
    width: 100%;
    height: 1px;
    margin: 6px 0;
    background: rgba(255, 255, 255, 0.14);
  }

  &__toggle-state {
    font-size: 12px;
    color: rgba(126, 200, 255, 0.95);
  }
}

@keyframes toolbar-col-drop {
  0% {
    transform: translateY(-28px);
    opacity: 0.25;
  }
  68% {
    transform: translateY(6px);
    opacity: 1;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
