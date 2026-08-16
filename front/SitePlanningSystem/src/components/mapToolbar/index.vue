<template>
  <div
    ref="toolbarRef"
    class="map-toolbar has-workflow"
    :class="{ 'is-pick-locked': pickLocked, 'is-dragging': toolbarDragging }"
    :style="toolbarPosStyle"
  >
    <div
      ref="colRef"
      class="map-toolbar__col"
      :class="{ 'is-charging': colPhase === 'charge', 'is-bursting': colPhase === 'burst' }"
    >
      <div class="map-toolbar__hub-wrap">
        <div
          class="map-toolbar__hub"
          title="拖动工具栏"
          @pointerdown="onHubPointerDown"
        >
          <span class="material-symbols-outlined icon-fill">hub</span>
        </div>
      </div>

      <nav class="map-toolbar__project-nav" aria-label="工程与业务">
        <button
          class="map-toolbar__tab"
          type="button"
          title="新建工程"
          :disabled="pickLocked"
          @click="openNewProject"
        >
          <span class="material-symbols-outlined">note_add</span>
          <span class="map-toolbar__tab-label">新建</span>
        </button>

        <div ref="projectListRef" class="map-toolbar__open map-toolbar__open--rail">
          <button
            class="map-toolbar__tab"
            type="button"
            title="打开工程"
            :disabled="pickLocked"
            :class="{ 'is-active': projectListOpen }"
            @click.stop="toggleProjectList"
          >
            <span class="material-symbols-outlined" :class="{ 'icon-fill': projectListOpen }">folder_open</span>
            <span class="map-toolbar__tab-label">打开</span>
          </button>
        </div>

        <button
          class="map-toolbar__tab"
          type="button"
          title="关闭当前工程"
          :disabled="pickLocked || !projectOpen"
          @click="closeCurrentProject"
        >
          <span class="material-symbols-outlined">folder_off</span>
          <span class="map-toolbar__tab-label">关闭</span>
        </button>

        <TransitionGroup name="rail-unlock" tag="div" class="map-toolbar__analysis">
          <button
            v-if="showCoreTools"
            key="station"
            class="map-toolbar__tab"
            type="button"
            title="配置发射点"
            :disabled="pickLocked || !projectOpen"
            @click="openStationConfig"
          >
            <span class="material-symbols-outlined">cell_tower</span>
            <span class="map-toolbar__tab-label">发射点</span>
          </button>

          <button
            v-if="showCoreTools"
            key="link"
            class="map-toolbar__tab"
            type="button"
            title="配置接收点"
            :disabled="pickLocked || !projectOpen"
            :class="{ 'is-active': activeWorkflow === 'slp' }"
            @click="openSLP"
          >
            <span class="material-symbols-outlined">settings_input_antenna</span>
            <span class="map-toolbar__tab-label">接收点</span>
          </button>

          <button
            v-if="showProfileTool"
            key="profile"
            class="map-toolbar__tab"
            type="button"
            title="链路计算"
            :disabled="pickLocked || profileLoading || (!profileReady && !railFull)"
            :class="{ 'is-active': activeWorkflow === 'profile' || activeWorkflow === 'linkage', 'is-loading': profileLoading }"
            @click="openLinkCompute"
          >
            <span class="material-symbols-outlined">show_chart</span>
            <span class="map-toolbar__tab-label">链路计算</span>
          </button>

          <button
            v-if="showAnalysisTools"
            key="coverage"
            class="map-toolbar__tab"
            type="button"
            title="区域覆盖"
            :disabled="pickLocked"
            :class="{ 'is-active': activeWorkflow === 'coverage' }"
            @click="openCoverage"
          >
            <span class="material-symbols-outlined">grid_on</span>
            <span class="map-toolbar__tab-label">区域覆盖</span>
          </button>

          <button
            v-if="showAnalysisTools"
            key="prediction"
            class="map-toolbar__tab"
            type="button"
            title="损耗计算"
            :disabled="pickLocked"
            :class="{ 'is-active': activeWorkflow === 'prediction' }"
            @click="openPrediction"
          >
            <span class="material-symbols-outlined">wifi_tethering</span>
            <span class="map-toolbar__tab-label">损耗计算</span>
          </button>

          <button
            v-if="showAnalysisTools"
            key="cluster"
            class="map-toolbar__tab"
            type="button"
            title="聚类分析"
            :disabled="pickLocked"
            :class="{ 'is-active': activeWorkflow === 'cluster' }"
            @click="openCluster"
          >
            <span class="material-symbols-outlined">scatter_plot</span>
            <span class="map-toolbar__tab-label">聚类分析</span>
          </button>
        </TransitionGroup>
      </nav>

      <div class="map-toolbar__rail-divider" aria-hidden="true"></div>

      <nav class="map-toolbar__nav" aria-label="地图工具">
        <button
          class="map-toolbar__tab"
          type="button"
          title="图层"
          :disabled="pickLocked"
          :class="{ 'is-active': layerPanelOpen }"
          @click="toggleLayerPanel"
        >
          <span class="material-symbols-outlined" :class="{ 'icon-fill': layerPanelOpen }">layers</span>
          <span class="map-toolbar__tab-label">图层</span>
        </button>

        <button
          class="map-toolbar__tab"
          type="button"
          title="测量长度"
          :disabled="pickLocked"
          :class="{ 'is-active': measureMode === 'distance' }"
          @click="toggleMeasureDistance"
        >
          <span class="material-symbols-outlined">straighten</span>
          <span class="map-toolbar__tab-label">测量长度</span>
        </button>

        <button
          class="map-toolbar__tab"
          type="button"
          title="测量面积"
          :disabled="pickLocked"
          :class="{ 'is-active': measureMode === 'area' }"
          @click="toggleMeasureArea"
        >
          <span class="material-symbols-outlined">square_foot</span>
          <span class="map-toolbar__tab-label">测量面积</span>
        </button>
      </nav>

      <div class="map-toolbar__footer">
        <button
          class="map-toolbar__tab map-toolbar__tab--icon"
          type="button"
          title="Help"
          :disabled="pickLocked"
          @click="showHelp"
        >
          <span class="material-symbols-outlined">help</span>
        </button>

        <button
          class="map-toolbar__tab map-toolbar__tab--icon map-toolbar__tab--status"
          type="button"
          title="连接状态"
          :class="{ 'is-ws-live': wsConnected }"
          :disabled="pickLocked"
          @click="showStatus"
        >
          <svg
            class="map-toolbar__ws-icon"
            :class="{ 'is-live': wsConnected }"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle class="map-toolbar__ws-dot" cx="12" cy="12" r="1.6" />
            <path
              class="map-toolbar__ws-arc map-toolbar__ws-arc--inner"
              d="M8.2 8.2a5.4 5.4 0 0 0 0 7.6"
            />
            <path
              class="map-toolbar__ws-arc map-toolbar__ws-arc--inner"
              d="M15.8 8.2a5.4 5.4 0 0 1 0 7.6"
            />
            <path
              class="map-toolbar__ws-arc map-toolbar__ws-arc--outer"
              d="M5.2 5.2a9.6 9.6 0 0 0 0 13.6"
            />
            <path
              class="map-toolbar__ws-arc map-toolbar__ws-arc--outer"
              d="M18.8 5.2a9.6 9.6 0 0 1 0 13.6"
            />
          </svg>
        </button>
      </div>

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

    <Teleport to="body">
      <transition name="station-fade">
        <div
          v-if="projectListOpen"
          class="open-project-dialog"
        >
          <div ref="projectsPanelRef" class="open-project-dialog__panel" @click.stop>
            <div class="open-project-dialog__edge"></div>
            <div class="open-project-dialog__header">
              <div class="open-project-dialog__heading">
                <div class="open-project-dialog__badge">
                  <span class="material-symbols-outlined icon-fill">folder_open</span>
                </div>
                <div>
                  <h2 class="open-project-dialog__title">打开工程</h2>
                  <p class="open-project-dialog__subtitle">
                    {{ projectListLoading ? "Loading projects…" : `${projectList.length} projects available.` }}
                  </p>
                </div>
              </div>
              <button
                class="open-project-dialog__icon-btn"
                type="button"
                title="关闭"
                @click="closeProjectList"
              >
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>

            <div class="open-project-dialog__body">
              <div class="open-project-dialog__section-head">
                <span class="material-symbols-outlined">list</span>
                <h3>工程列表</h3>
                <em v-if="!projectListLoading">{{ projectList.length }} 个</em>
              </div>

              <div v-if="projectListLoading" class="open-project-dialog__empty">加载中…</div>
              <div v-else-if="!projectList.length" class="open-project-dialog__empty">暂无工程，请先新建</div>
              <div v-else class="open-project-dialog__list">
                <div
                  v-for="row in projectList"
                  :key="row.id"
                  class="open-project-dialog__item"
                  :class="{
                    'is-current': String(row.id) === currentProjectId,
                    'is-selected': String(row.id) === selectedProjectId,
                  }"
                  @click="selectProject(row)"
                >
                  <div class="open-project-dialog__main">
                    <div class="open-project-dialog__name" @dblclick.stop="openProject(row)">
                      {{ row.name }}
                      <span v-if="String(row.id) === currentProjectId" class="open-project-dialog__tag">当前</span>
                    </div>
                    <div class="open-project-dialog__meta">{{ projectMeta(row) }}</div>
                  </div>
                  <div class="open-project-dialog__side">
                    <span class="open-project-dialog__time">{{ formatProjectTime(row.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="open-project-dialog__footer">
              <button class="open-project-dialog__btn open-project-dialog__btn--ghost" type="button" @click="closeProjectList">
                取消
              </button>
              <button class="open-project-dialog__btn open-project-dialog__btn--primary" type="button" @click="confirmOpenProject">
                <span class="material-symbols-outlined">check</span>
                确认
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getMapInstance } from "@/assets/util/index";
import { UseoperatingButton } from "@/view/layout/components/map/service/UseoperatingButton";
import { Tool } from "@/components/tool/service";
import { map3dConfig } from "@/view/layout/components/map/config/config";
import { listProjects } from "@/request/sitePlanting";

const currentInstance = getCurrentInstance();
const $bus = currentInstance?.appContext.config.globalProperties.$bus;
const router = useRouter();
const route = useRoute();

const measureMode = ref<"" | "distance" | "area">("");
const layerPanelOpen = ref(false);
const activeBasemap = ref("天地图影像");
const roadNetworkVisible = ref(true);
const pickLocked = ref(false);
const projectOpen = ref(false);
const projectListOpen = ref(false);
const selectedProjectId = ref("");
const projectListLoading = ref(false);
const projectList = ref<any[]>([]);
const projectListRef = ref<HTMLElement | null>(null);
const projectsPanelRef = ref<HTMLElement | null>(null);
const currentProjectId = ref("");
const stationReady = ref(false);
const linkReady = ref(false);
const profileReady = ref(false);
const linkAnalysisReady = ref(false);
const railFull = ref(false);
const activeWorkflow = ref<"slp" | "profile" | "linkage" | "coverage" | "prediction" | "cluster" | "">("");
const profileLoading = ref(false);
const wsConnected = ref(false);

const showCoreTools = computed(() => projectOpen.value || railFull.value);
const showProfileTool = computed(() => profileReady.value || railFull.value);
const showAnalysisTools = computed(() => stationReady.value || railFull.value);

const colRef = ref<HTMLElement | null>(null);
const colPhase = ref<"idle" | "charge" | "burst">("idle");
const toolbarRef = ref<HTMLElement | null>(null);
const toolbarLeft = ref(24);
const toolbarTop = ref(96);
const toolbarDragging = ref(false);
const toolbarPosStyle = computed(() => ({
  left: `${toolbarLeft.value}px`,
  top: `${toolbarTop.value}px`,
}));

const TOOLBAR_POS_KEY = "map-toolbar-pos";
let dragOffsetX = 0;
let dragOffsetY = 0;

const clampToolbarPos = (left: number, top: number) => {
  const el = toolbarRef.value;
  const w = el?.offsetWidth ?? 80;
  const h = el?.offsetHeight ?? 240;
  const pad = 8;
  return {
    left: Math.min(Math.max(pad, window.innerWidth - w - pad), Math.max(pad, left)),
    top: Math.min(Math.max(pad, window.innerHeight - h - pad), Math.max(pad, top)),
  };
};

const persistToolbarPos = () => {
  try {
    localStorage.setItem(
      TOOLBAR_POS_KEY,
      JSON.stringify({ left: toolbarLeft.value, top: toolbarTop.value })
    );
  } catch {
    /* ignore */
  }
};

const restoreToolbarPos = () => {
  try {
    const raw = localStorage.getItem(TOOLBAR_POS_KEY);
    if (!raw) return;
    const pos = JSON.parse(raw);
    if (typeof pos?.left !== "number" || typeof pos?.top !== "number") return;
    const next = clampToolbarPos(pos.left, pos.top);
    toolbarLeft.value = next.left;
    toolbarTop.value = next.top;
  } catch {
    /* ignore */
  }
};

const onHubPointerMove = (e: PointerEvent) => {
  if (!toolbarDragging.value) return;
  const next = clampToolbarPos(e.clientX - dragOffsetX, e.clientY - dragOffsetY);
  toolbarLeft.value = next.left;
  toolbarTop.value = next.top;
};

const onHubPointerUp = (e: PointerEvent) => {
  toolbarDragging.value = false;
  window.removeEventListener("pointermove", onHubPointerMove);
  window.removeEventListener("pointerup", onHubPointerUp);
  try {
    (e.target as HTMLElement)?.releasePointerCapture?.(e.pointerId);
  } catch {
    /* ignore */
  }
  persistToolbarPos();
};

const onHubPointerDown = (e: PointerEvent) => {
  if (e.button !== 0 || pickLocked.value) return;
  e.preventDefault();
  e.stopPropagation();
  const el = toolbarRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  dragOffsetX = e.clientX - rect.left;
  dragOffsetY = e.clientY - rect.top;
  toolbarDragging.value = true;
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  window.addEventListener("pointermove", onHubPointerMove);
  window.addEventListener("pointerup", onHubPointerUp);
};

let burstGen = 0;
let activeColAnim: Animation | null = null;

const CHARGE_MS = 520;
const BURST_MS = 180;

const readNaturalHeight = (el: HTMLElement) => {
  const prev = el.style.height;
  el.style.height = "auto";
  const h = Math.max(Math.ceil(el.scrollHeight), Math.ceil(el.getBoundingClientRect().height));
  el.style.height = prev;
  return h;
};

const playColHeight = async (el: HTMLElement, keyframes: Keyframe[], duration: number) => {
  activeColAnim?.cancel();
  const anim = el.animate(keyframes, {
    duration,
    fill: "forwards",
  });
  activeColAnim = anim;
  try {
    await anim.finished;
  } catch {
    return false;
  }
  anim.cancel();
  return true;
};

const burstColHeight = async () => {
  const el = colRef.value;
  if (!el) return;
  const gen = ++burstGen;

  const from = Math.ceil(el.getBoundingClientRect().height);
  await nextTick();
  await nextTick();
  if (gen !== burstGen) return;

  const to = readNaturalHeight(el);
  if (Math.abs(to - from) < 2) {
    el.style.height = "";
    colPhase.value = "idle";
    return;
  }

  el.style.height = `${from}px`;
  void el.offsetHeight;

  if (to <= from) {
    colPhase.value = "burst";
    const done = await playColHeight(
      el,
      [
        { height: `${from}px` },
        { height: `${to}px` },
      ],
      280
    );
    if (!done || gen !== burstGen) return;
    el.style.height = "";
    colPhase.value = "idle";
    return;
  }

  const crouch = Math.max(36, Math.min(64, Math.round(from * 0.14)));
  const charged = Math.max(96, from - crouch);
  const total = CHARGE_MS + BURST_MS;
  colPhase.value = "charge";

  window.setTimeout(() => {
    if (gen === burstGen) colPhase.value = "burst";
  }, CHARGE_MS);

  const done = await playColHeight(
    el,
    [
      { height: `${from}px`, offset: 0, easing: "cubic-bezier(0.45, 0.02, 0.55, 1)" },
      { height: `${charged}px`, offset: CHARGE_MS / total, easing: "cubic-bezier(0.2, 0.85, 0.25, 1)" },
      { height: `${to}px`, offset: 1 },
    ],
    total
  );
  if (!done || gen !== burstGen) return;
  el.style.height = "";
  colPhase.value = "idle";
};

watch([showCoreTools, showProfileTool, showAnalysisTools], () => {
  burstColHeight();
});

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

const closeProjectList = () => {
  projectListOpen.value = false;
  selectedProjectId.value = "";
};

const toggleProjectList = async () => {
  if (pickLocked.value) return;
  layerPanelOpen.value = false;
  if (projectListOpen.value) {
    closeProjectList();
    return;
  }
  projectListOpen.value = true;
  await loadProjects();
  selectedProjectId.value = currentProjectId.value || "";
};

const toggleLayerPanel = () => {
  if (pickLocked.value) return;
  closeProjectList();
  layerPanelOpen.value = !layerPanelOpen.value;
};

const emitOnHome = (event: string) => {
  const go = () => $bus?.emit(event);
  if (route.name === "home" || route.path === "/") {
    go();
    return;
  }
  router.push("/").then(() => {
    window.setTimeout(go, 80);
  });
};

const formatProjectTime = (value: string) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value).replace("T", " ").slice(0, 16);
  }
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

const projectMeta = (row: any) => {
  const parts = [row.username].filter(Boolean);
  parts.push(row.single_link_count ? `${row.single_link_count}条链路` : "无链路");
  parts.push(row.has_coverage ? "有覆盖" : "无覆盖");
  if (row.station_count) parts.push(`${row.station_count}个站点`);
  return parts.join(" · ");
};

const loadProjects = async () => {
  projectListLoading.value = true;
  try {
    const all: any[] = [];
    let page = 1;
    while (page <= 50) {
      const res: any = await listProjects({ page });
      const batch = res?.results || [];
      all.push(...batch);
      if (!res?.next || !batch.length) break;
      page += 1;
    }
    projectList.value = all;
  } catch {
    projectList.value = [];
    ElMessage.error("加载工程列表失败");
  } finally {
    projectListLoading.value = false;
  }
};

const selectProject = (row: any) => {
  if (!row?.id) return;
  selectedProjectId.value = String(row.id);
};

const confirmOpenProject = () => {
  const row = projectList.value.find((item) => String(item.id) === selectedProjectId.value);
  if (!row) {
    ElMessage.warning("请先选择一个工程");
    return;
  }
  openProject(row);
};

const openProject = (row: any) => {
  if (!row?.id) return;
  closeProjectList();
  if (route.name === "home" || route.path === "/") {
    $bus?.emit("openProjectById", row.id);
    return;
  }
  router.push({ path: "/", query: { project: String(row.id) } });
};

const openNewProject = () => {
  if (pickLocked.value) return;
  layerPanelOpen.value = false;
  closeProjectList();
  emitOnHome("requestNewProject");
};

const closeCurrentProject = () => {
  if (pickLocked.value || !projectOpen.value) return;
  layerPanelOpen.value = false;
  closeProjectList();
  emitOnHome("requestCloseProject");
};

const openStationConfig = () => {
  if (pickLocked.value || !projectOpen.value) return;
  layerPanelOpen.value = false;
  closeProjectList();
  emitOnHome("openLaunchSiteConfig");
};

const openSLP = () => {
  if (pickLocked.value || !projectOpen.value) return;
  closeProjectList();
  activeWorkflow.value = "slp";
  emitOnHome("openSLPComputedDialog");
};

const openLinkCompute = () => {
  if (pickLocked.value || profileLoading.value) return;
  if (!profileReady.value && !railFull.value) return;
  closeProjectList();
  activeWorkflow.value = "profile";
  emitOnHome("openProfileExtract");
};

const openCoverage = () => {
  if (pickLocked.value || (!stationReady.value && !railFull.value)) return;
  closeProjectList();
  activeWorkflow.value = "coverage";
  emitOnHome("openCoverageDialog");
};

const openPrediction = () => {
  if (pickLocked.value || (!stationReady.value && !railFull.value)) return;
  closeProjectList();
  activeWorkflow.value = "prediction";
  emitOnHome("runTransmissionLossPrediction");
};

const openCluster = () => {
  if (pickLocked.value || (!stationReady.value && !railFull.value)) return;
  closeProjectList();
  activeWorkflow.value = "cluster";
  emitOnHome("openClusterDialog");
};

const stopMeasure = () => {
  measureTool?.clear();
  measureMode.value = "";
};

const toggleMeasureDistance = async () => {
  if (pickLocked.value || !measureTool) return;
  closeProjectList();
  layerPanelOpen.value = false;
  if (measureMode.value === "distance") {
    stopMeasure();
    return;
  }
  measureTool.clear();
  measureMode.value = "distance";
  ElMessage.info("开始测量长度，右键或双击结束；再次点击按钮可清除");
  try {
    await measureTool.distance();
  } catch {
    /* cancelled */
  }
  if (measureMode.value === "distance") measureMode.value = "";
};

const toggleMeasureArea = async () => {
  if (pickLocked.value || !measureTool) return;
  closeProjectList();
  layerPanelOpen.value = false;
  if (measureMode.value === "area") {
    stopMeasure();
    return;
  }
  measureTool.clear();
  measureMode.value = "area";
  ElMessage.info("开始测量面积，左键加点，右键或双击结束；再次点击按钮可清除");
  try {
    await measureTool.area();
  } catch {
    /* cancelled */
  }
  if (measureMode.value === "area") measureMode.value = "";
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

const showStatus = () => {
  if (pickLocked.value) return;
  ElMessage.info(wsConnected.value ? "前后端连接正常" : "前后端连接未就绪");
};

const onWsConnectionStatus = (connected: boolean) => {
  wsConnected.value = !!connected;
};

const onMapPickMode = (active: boolean) => {
  pickLocked.value = !!active;
  if (!active) return;
  layerPanelOpen.value = false;
  closeProjectList();
  if (measureMode.value && measureTool) {
    stopMeasure();
  }
};

const onProjectOpen = (open: boolean) => {
  projectOpen.value = !!open;
  if (!open) {
    stationReady.value = false;
    linkReady.value = false;
    profileReady.value = false;
    linkAnalysisReady.value = false;
    railFull.value = false;
    activeWorkflow.value = "";
  }
};

const onStationReady = (ready: boolean) => {
  const next = !!ready;
  const unlocked = next && !stationReady.value;
  stationReady.value = next;
  if (!next) {
    if (!railFull.value) activeWorkflow.value = "";
  }
  if (unlocked && !railFull.value) {
    ElMessage.info("发射点就绪，可进行区域覆盖 / 损耗计算 / 聚类分析");
  }
};

const onLinkReady = (ready: boolean) => {
  linkReady.value = !!ready;
};

const onProfileReady = (ready: boolean) => {
  const next = !!ready;
  const unlocked = next && !profileReady.value;
  profileReady.value = next;
  if (unlocked && !railFull.value) {
    ElMessage.info("收发点就绪，可进行链路计算");
  }
};

const onLinkAnalysisReady = (ready: boolean) => {
  const next = !!ready;
  const unlocked = next && !linkAnalysisReady.value;
  linkAnalysisReady.value = next;
  if (unlocked && !railFull.value) {
    ElMessage.info("链路计算完成");
  }
};

const onRailFull = (full: boolean) => {
  railFull.value = !!full;
};

const onProfileLoading = (loading: boolean) => {
  profileLoading.value = !!loading;
};

const onWorkflowActive = (name: "slp" | "profile" | "linkage" | "coverage" | "prediction" | "cluster" | "") => {
  activeWorkflow.value = name || "";
};

const onProjectId = (id: string | number) => {
  currentProjectId.value = id ? String(id) : "";
};

const onDocKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape" && projectListOpen.value) {
    closeProjectList();
  }
};

const resetToolbarSession = () => {
  pickLocked.value = false;
  projectOpen.value = false;
  stationReady.value = false;
  linkReady.value = false;
  profileReady.value = false;
  linkAnalysisReady.value = false;
  railFull.value = false;
  activeWorkflow.value = "";
  profileLoading.value = false;
  layerPanelOpen.value = false;
  closeProjectList();
  currentProjectId.value = "";
  if (measureMode.value && measureTool) {
    stopMeasure();
  } else {
    measureTool?.clear();
  }
};

const onLogout = () => {
  resetToolbarSession();
  wsConnected.value = false;
};

onMounted(async () => {
  await nextTick();
  $bus?.on("mapPickMode", onMapPickMode);
  $bus?.on("workflowProjectOpen", onProjectOpen);
  $bus?.on("workflowProjectId", onProjectId);
  $bus?.on("workflowStationReady", onStationReady);
  $bus?.on("workflowLinkReady", onLinkReady);
  $bus?.on("workflowProfileReady", onProfileReady);
  $bus?.on("workflowLinkAnalysisReady", onLinkAnalysisReady);
  $bus?.on("workflowRailFull", onRailFull);
  $bus?.on("workflowProfileLoading", onProfileLoading);
  $bus?.on("workflowActive", onWorkflowActive);
  $bus?.on("wsConnectionStatus", onWsConnectionStatus);
  $bus?.on("Logout", onLogout);
  $bus?.on("resetMapView", resetToolbarSession);
  document.addEventListener("keydown", onDocKeydown);
  $bus?.emit("wsConnectionStatusRequest");
  $bus?.emit("workflowRailStateRequest");
  restoreToolbarPos();
  const map = await waitForMap();
  $bus?.emit("wsConnectionStatusRequest");
  $bus?.emit("workflowRailStateRequest");
  if (!map) return;
  operatingButton = new UseoperatingButton(map);
  measureTool = new Tool(map);

  const current = (map3dConfig.basemaps || []).find((item: any) => item.show && item.name);
  if (current?.name) activeBasemap.value = current.name;
});

onUnmounted(() => {
  burstGen += 1;
  activeColAnim?.cancel();
  window.removeEventListener("pointermove", onHubPointerMove);
  window.removeEventListener("pointerup", onHubPointerUp);
  $bus?.off("mapPickMode", onMapPickMode);
  $bus?.off("workflowProjectOpen", onProjectOpen);
  $bus?.off("workflowProjectId", onProjectId);
  $bus?.off("workflowStationReady", onStationReady);
  $bus?.off("workflowLinkReady", onLinkReady);
  $bus?.off("workflowProfileReady", onProfileReady);
  $bus?.off("workflowLinkAnalysisReady", onLinkAnalysisReady);
  $bus?.off("workflowRailFull", onRailFull);
  $bus?.off("workflowProfileLoading", onProfileLoading);
  $bus?.off("workflowActive", onWorkflowActive);
  $bus?.off("wsConnectionStatus", onWsConnectionStatus);
  $bus?.off("Logout", onLogout);
  $bus?.off("resetMapView", resetToolbarSession);
  document.removeEventListener("keydown", onDocKeydown);
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
  background: rgba(24, 26, 24, 0.82);
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
    left: 24px;
    top: 96px;
    bottom: auto;
    height: auto;
    max-width: none;
    width: auto;
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
  &__btn,
  &__tab,
  &__open,
  &__projects {
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
    background: rgba(24, 26, 24, 0.82);
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
  }

  &.has-workflow &__row {
    width: auto;
    margin-left: 92px;
    justify-content: flex-start;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 12px;
    overflow: visible;
    position: relative;
    z-index: 3;
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
      max-width: 420px;
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
    gap: 0;
    width: 80px;
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
    position: relative;
    left: auto;
    top: auto;
    bottom: auto;
    z-index: 40;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 80px;
    height: auto;
    padding: 16px 0 12px;
    border-radius: 0.75rem;
    animation: none;
    background: rgba(12, 21, 16, 0.75);
    border: 1px solid rgba(64, 73, 69, 0.2);
    box-shadow:
      0 10px 15px -3px rgb(0 0 0 / 0.1),
      0 4px 6px -4px rgb(0 0 0 / 0.1);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    overflow: visible;
    transform-origin: top center;
    transition:
      width 0.55s 0.15s var(--toolbar-ease),
      padding 0.55s 0.15s var(--toolbar-ease),
      background 0.5s 0.22s ease,
      border-color 0.5s 0.22s ease,
      box-shadow 0.5s 0.22s ease,
      border-radius 0.5s 0.15s ease;

    &.is-charging,
    &.is-bursting {
      overflow: hidden;
      will-change: height;
    }

    &.is-charging {
      box-shadow:
        0 6px 12px -6px rgb(0 0 0 / 0.4),
        inset 0 -12px 20px rgba(0, 0, 0, 0.2);
      border-color: rgba(157, 223, 46, 0.16);
      transition: box-shadow 0.5s ease, border-color 0.5s ease;
    }

    &.is-bursting {
      box-shadow:
        0 18px 32px -8px rgb(0 0 0 / 0.38),
        0 0 0 1px rgba(157, 223, 46, 0.14);
      border-color: rgba(157, 223, 46, 0.28);
      transition: box-shadow 0.18s ease, border-color 0.18s ease;
    }
  }

  &__hub-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-bottom: 8px;
    padding: 0 8px;
    box-sizing: border-box;
  }

  &.is-dragging {
    user-select: none;
  }

  &__hub {
    width: 40px;
    height: 40px;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.5rem;
    background: #222c26;
    cursor: grab;
    touch-action: none;
    user-select: none;
    border: 1px solid rgba(64, 73, 69, 0.3);
    color: #a1d1bf;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);

    .material-symbols-outlined {
      font-size: 20px;
    }
  }

  &.is-dragging &__hub {
    cursor: grabbing;
  }

  &__project-nav {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 2px;
    flex: 0 0 auto;
    min-height: 0;
    overflow: visible;
  }

  &__analysis {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 2px;
    width: 100%;
  }

  .rail-unlock-enter-active {
    overflow: hidden;
    transition:
      opacity 0.18s ease,
      transform 0.2s cubic-bezier(0.2, 0.85, 0.25, 1),
      max-height 0.2s cubic-bezier(0.2, 0.85, 0.25, 1),
      margin 0.2s cubic-bezier(0.2, 0.85, 0.25, 1),
      padding 0.2s cubic-bezier(0.2, 0.85, 0.25, 1);
  }

  .rail-unlock-leave-active {
    overflow: hidden;
    transition:
      opacity 0.22s ease,
      transform 0.28s ease,
      max-height 0.28s ease,
      margin 0.28s ease,
      padding 0.28s ease,
      filter 0.22s ease;
  }

  .rail-unlock-enter-active:nth-child(1) { transition-delay: 0.52s; }
  .rail-unlock-enter-active:nth-child(2) { transition-delay: 0.56s; }
  .rail-unlock-enter-active:nth-child(3) { transition-delay: 0.6s; }
  .rail-unlock-enter-active:nth-child(4) { transition-delay: 0.64s; }
  .rail-unlock-enter-active:nth-child(5) { transition-delay: 0.68s; }
  .rail-unlock-enter-active:nth-child(6) { transition-delay: 0.72s; }
  .rail-unlock-enter-active:nth-child(7) { transition-delay: 0.76s; }

  .rail-unlock-leave-active:nth-child(1) { transition-delay: 0.15s; }
  .rail-unlock-leave-active:nth-child(2) { transition-delay: 0.1s; }
  .rail-unlock-leave-active:nth-child(3) { transition-delay: 0.05s; }
  .rail-unlock-leave-active:nth-child(4),
  .rail-unlock-leave-active:nth-child(5),
  .rail-unlock-leave-active:nth-child(6) { transition-delay: 0s; }

  .rail-unlock-enter-from {
    opacity: 0;
    transform: translateY(-12px) scale(0.92);
    max-height: 0;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  .rail-unlock-leave-to {
    opacity: 0;
    transform: translateY(-8px) scale(0.96);
    max-height: 0;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  .rail-unlock-enter-to,
  .rail-unlock-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
    max-height: 58px;
  }

  &__rail-divider {
    width: calc(100% - 24px);
    height: 1px;
    margin: 8px 12px;
    flex-shrink: 0;
    background: rgba(64, 73, 69, 0.4);
  }

  &__nav {
    flex: 0 0 auto;
    width: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    overflow: visible;
  }

  &__tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: auto;
    margin: 0 8px;
    padding: 8px 0;
    border: none;
    border-radius: 0.5rem;
    background: transparent;
    color: #c0c8c3;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;

    .material-symbols-outlined {
      margin-bottom: 2px;
      font-size: 22px;
      transition: transform 0.2s ease, color 0.2s ease;
    }

    &:hover:not(:disabled):not(.is-active) {
      background: rgba(49, 60, 53, 0.3);
      color: #dae5dc;

      .material-symbols-outlined {
        color: #dae5dc;
      }
    }

    &:hover:not(:disabled) .icon-fill {
      transform: scale(1.1);
    }

    &:disabled {
      opacity: 0.45;
      cursor: default;
    }

    &.is-active {
      background: #83c300;
      color: #304b00;
    }

    &--icon {
      padding: 8px 0;

      .material-symbols-outlined {
        margin-bottom: 0;
        font-size: 20px;
      }

      &:hover:not(:disabled) .material-symbols-outlined {
        transform: none;
        color: #dae5dc;
      }
    }

    &--status:hover:not(:disabled):not(.is-ws-live) .map-toolbar__ws-icon {
      .map-toolbar__ws-dot {
        fill: #9ddf2e;
      }

      .map-toolbar__ws-arc {
        stroke: #9ddf2e;
      }
    }

    &--status.is-ws-live:hover:not(:disabled) {
      color: #9ddf2e;
    }
  }

  &__ws-icon {
    width: 22px;
    height: 22px;
    display: block;
    overflow: visible;

    .map-toolbar__ws-dot {
      fill: #7a857e;
      stroke: none;
    }

    .map-toolbar__ws-arc {
      fill: none;
      stroke: #7a857e;
      stroke-width: 1.9;
      stroke-linecap: round;
    }

    &.is-live {
      .map-toolbar__ws-dot {
        animation: map-toolbar-ws-dot 0.9s linear infinite;
      }

      .map-toolbar__ws-arc--inner {
        animation: map-toolbar-ws-inner 0.9s linear infinite;
      }

      .map-toolbar__ws-arc--outer {
        animation: map-toolbar-ws-outer 0.9s linear infinite;
      }
    }
  }

  @keyframes map-toolbar-ws-dot {
    0%,
    8% {
      fill: #7a857e;
    }
    12%,
    72% {
      fill: #b8f03a;
    }
    80%,
    100% {
      fill: #7a857e;
    }
  }

  @keyframes map-toolbar-ws-inner {
    0%,
    18% {
      stroke: #7a857e;
      stroke-width: 1.9;
    }
    22%,
    72% {
      stroke: #b8f03a;
      stroke-width: 2.3;
    }
    80%,
    100% {
      stroke: #7a857e;
      stroke-width: 1.9;
    }
  }

  @keyframes map-toolbar-ws-outer {
    0%,
    38% {
      stroke: #7a857e;
      stroke-width: 1.9;
    }
    42%,
    78% {
      stroke: #b8f03a;
      stroke-width: 2.3;
    }
    88%,
    100% {
      stroke: #7a857e;
      stroke-width: 1.9;
    }
  }

  &__project-nav &__tab,
  &__analysis &__tab {
    padding: 7px 0;

    &.is-loading {
      opacity: 0.7;
    }
  }

  &__tab-label {
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 11px;
    font-weight: 500;
    line-height: 14px;
    letter-spacing: normal;
    white-space: nowrap;
    word-break: normal;
    opacity: 0.9;
  }

  &__footer {
    width: 100%;
    margin-top: 108px;
    padding-top: 16px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    border-top: 1px solid rgba(64, 73, 69, 0.2);
    flex-shrink: 0;
  }

  &__open {
    position: relative;
    z-index: 8;
    flex-shrink: 0;

    &--rail {
      width: 100%;
    }

    &--rail .map-toolbar__tab {
      width: calc(100% - 16px);
    }
  }

  &__projects {
    position: absolute;
    left: 0;
    top: calc(100% + 10px);
    z-index: 240;
    width: 460px;
    box-sizing: border-box;
    padding: 12px;
    border-radius: 12px;
    background: rgba(18, 20, 18, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.42);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    color: #fff;

    &--rail {
      left: calc(100% + 14px);
      top: 0;
      transform: none;
    }
  }

  &__projects-head {
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 2px 4px 10px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;

    em {
      font-style: normal;
      font-size: 11px;
      font-weight: 500;
      color: rgba(190, 200, 212, 0.7);
    }
  }

  &__projects-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 360px;
    overflow: auto;
    box-sizing: border-box;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 999px;
      background: rgba(157, 223, 46, 0.55);
    }
  }

  &__projects-empty {
    padding: 18px 8px;
    text-align: center;
    font-size: 12px;
    color: rgba(190, 200, 212, 0.72);
  }

  &__project {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-sizing: border-box;
    width: 100%;
    min-width: 0;
    padding: 8px 12px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #fff;
    cursor: pointer;
    text-align: left;

    &:hover,
    &.is-current {
      background: rgba(255, 255, 255, 0.08);
    }

    &.is-current {
      box-shadow: inset 0 0 0 1px rgba(163, 230, 53, 0.35);
    }
  }

  &__project-main {
    min-width: 0;
    flex: 1;
  }

  &__project-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.3;
    color: #f2f6fa;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__project-tag {
    flex-shrink: 0;
    padding: 1px 6px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 500;
    color: #d9f99d;
    background: rgba(163, 230, 53, 0.18);
  }

  &__project-meta {
    margin-top: 4px;
    font-size: 11px;
    line-height: 1.3;
    color: rgba(190, 200, 212, 0.72);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__project-side {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
    gap: 6px;
    flex: 0 0 auto;
    min-width: 124px;
  }

  &__project-time {
    font-size: 11px;
    line-height: 1.3;
    color: rgba(190, 200, 212, 0.62);
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }

  &__project-delete {
    border: none;
    background: transparent;
    padding: 0;
    font-size: 12px;
    line-height: 1.3;
    white-space: nowrap;
    color: rgba(255, 138, 128, 0.92);
    cursor: pointer;

    &:hover {
      color: #ff9d96;
    }
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
      background: #a3e635;
      color: #121412;
    }

    &--file {
      width: auto;
      min-width: 64px;
      height: 32px;
      padding: 0 10px;
      gap: 6px;
      border-radius: 8px;
      font-family: Inter, "Noto Sans SC", sans-serif;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.01em;

      svg {
        width: 16px;
        height: 16px;
        flex-shrink: 0;
      }

      span {
        white-space: nowrap;
      }

      &.is-loading {
        opacity: 0.7;
      }
    }
  }

  &__panel {
    position: absolute;
    left: calc(100% + 12px);
    top: 46%;
    z-index: 50;
    width: 200px;
    padding: 10px;
    border-radius: 12px;
    background: rgba(18, 20, 18, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.42);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
  }

  &__panel-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin: 0;
    padding: 8px 10px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #dae5dc;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 13px;
    text-align: left;
    cursor: pointer;

    &:hover {
      background: rgba(255, 255, 255, 0.08);
    }

    &.is-active {
      background: rgba(157, 223, 46, 0.16);
      color: #9ddf2e;
    }

    &--toggle {
      margin-top: 2px;
    }
  }

  &__panel-divider {
    height: 1px;
    margin: 8px 4px;
    background: rgba(255, 255, 255, 0.1);
  }

  &__toggle-state {
    font-size: 11px;
    color: rgba(190, 200, 212, 0.72);
  }

  &.has-workflow > .map-toolbar__col {
    overflow: visible;
  }
}
</style>

<style lang="scss">
/* Teleport 到 body：打开工程对话框 */
.open-project-dialog {
  position: fixed;
  inset: 0;
  z-index: 1300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(6, 12, 10, 0.55);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  box-sizing: border-box;

  &__panel {
    position: relative;
    width: min(560px, 100%);
    max-height: min(640px, calc(100vh - 48px));
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-radius: 0.75rem;
    background: rgba(12, 21, 16, 0.92);
    border: 1px solid rgba(64, 73, 69, 0.35);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
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
    flex-shrink: 0;
  }

  &__heading {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
  }

  &__badge {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba(157, 223, 46, 0.12);
    color: #9ddf2e;
    flex-shrink: 0;

    .material-symbols-outlined {
      font-size: 22px;
    }
  }

  &__title {
    margin: 0;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 20px;
    font-weight: 600;
    line-height: 28px;
    color: #ffffff;
  }

  &__subtitle {
    margin: 2px 0 0;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 13px;
    color: rgba(192, 200, 195, 0.75);
  }

  &__icon-btn {
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 0.5rem;
    background: transparent;
    color: #c0c8c3;
    cursor: pointer;

    &:hover {
      background: rgba(45, 55, 49, 0.6);
      color: #ffffff;
    }

    .material-symbols-outlined {
      font-size: 20px;
    }
  }

  &__body {
    flex: 1;
    min-height: 0;
    padding: 16px 20px 8px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  &__section-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    color: #ffffff;
    flex-shrink: 0;

    .material-symbols-outlined {
      font-size: 18px;
      color: #9ddf2e;
    }

    h3 {
      margin: 0;
      font-family: Inter, "Noto Sans SC", sans-serif;
      font-size: 13px;
      font-weight: 600;
    }

    em {
      margin-left: auto;
      font-style: normal;
      font-size: 12px;
      color: rgba(192, 200, 195, 0.7);
    }
  }

  &__list {
    flex: 1;
    min-height: 0;
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 999px;
      background: rgba(157, 223, 46, 0.55);
    }
  }

  &__empty {
    padding: 48px 12px;
    text-align: center;
    font-size: 13px;
    color: rgba(192, 200, 195, 0.7);
  }

  &__item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 12px 14px;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.15s ease;

    &:hover,
    &.is-current {
      background: rgba(255, 255, 255, 0.06);
    }

    &.is-current {
      box-shadow: inset 0 0 0 1px rgba(157, 223, 46, 0.2);
    }

    &.is-selected {
      background: rgba(157, 223, 46, 0.1);
      box-shadow: inset 0 0 0 1px rgba(157, 223, 46, 0.45);
    }
  }

  &__main {
    min-width: 0;
    flex: 1;
  }

  &__name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #f2f6fa;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__tag {
    flex-shrink: 0;
    padding: 1px 6px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 500;
    color: #d9f99d;
    background: rgba(157, 223, 46, 0.18);
  }

  &__meta {
    margin-top: 4px;
    font-size: 12px;
    color: rgba(192, 200, 195, 0.72);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__side {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
    flex-shrink: 0;
  }

  &__time {
    font-size: 12px;
    color: rgba(192, 200, 195, 0.62);
    font-variant-numeric: tabular-nums;
  }

  &__delete {
    border: none;
    background: transparent;
    padding: 0;
    font-size: 12px;
    color: rgba(255, 138, 128, 0.92);
    cursor: pointer;

    &:hover {
      color: #ff9d96;
    }
  }

  &__footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    padding: 16px 24px;
    border-top: 1px solid rgba(64, 73, 69, 0.2);
    background: rgba(45, 55, 49, 0.3);
    flex-shrink: 0;
  }

  &__btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-width: 88px;
    height: 40px;
    padding: 0 18px;
    border-radius: 0.5rem;
    font-family: Inter, "Noto Sans SC", sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;

    .material-symbols-outlined {
      font-size: 18px;
    }

    &--ghost {
      border: 1px solid rgba(64, 73, 69, 0.6);
      background: transparent;
      color: #dae5dc;

      &:hover {
        border-color: #8a938e;
        color: #ffffff;
      }
    }

    &--primary {
      border: none;
      background: #9ddf2e;
      color: #213600;

      &:hover {
        background: #b2f746;
      }
    }
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
