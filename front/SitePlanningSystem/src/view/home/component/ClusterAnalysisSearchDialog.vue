<template>
  <transition name="station-fade">
    <div
      v-if="showClusterAnalysisSearchDialog"
      ref="panelRef"
      class="station-config"
      :style="panelStyle"
    >
      <div class="station-config__panel">
        <div class="station-config__edge"></div>
        <div class="station-config__header" @mousedown="startDrag">
          <div class="station-config__heading">
            <div class="station-config__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M5 7h4v4H5zm5 0h4v4h-4zm5 0h4v4h-4zM7.5 14.5 5 19h14l-3.5-4.5-2.5 3z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="station-config__title">聚类分析及站点推荐列表查询</h2>
              <p class="station-config__subtitle">Cluster analysis and station recommendation.</p>
            </div>
          </div>
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

        <div class="station-config__body">
          <el-form
            ref="clusterAnalysisFormRef"
            :rules="clusterAnalysisFormRules"
            :model="clusterAnalysisForm"
            label-position="top"
            class="station-config__form"
            require-asterisk-position="right"
            :show-message="false"
          >
            <section class="station-config__card">
              <div class="station-config__section-head">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M5 7h14M5 12h14M5 17h10"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <h3>参数配置</h3>
              </div>
              <div class="station-config__row-2">
                <el-form-item label="邻域距离阈值" prop="eps_cells">
                  <el-input v-model="clusterAnalysisForm.eps_cells" placeholder="请输入">
                    <template #suffix>
                      <span class="station-config__unit">m</span>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="邻域样本个体阈值" prop="min_samples">
                  <el-input v-model="clusterAnalysisForm.min_samples" placeholder="请输入">
                    <template #suffix>
                      <span class="station-config__unit">个</span>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="传输损耗值的约束条件" prop="loss_threshold">
                  <el-input v-model="clusterAnalysisForm.loss_threshold" placeholder="请输入">
                    <template #suffix>
                      <span class="station-config__unit">dB</span>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="道路距离限制" prop="limit_road_distance">
                  <el-input v-model="clusterAnalysisForm.limit_road_distance" placeholder="请输入">
                    <template #suffix>
                      <span class="station-config__unit">m</span>
                    </template>
                  </el-input>
                </el-form-item>
              </div>
            </section>
          </el-form>

          <!-- 目标区域 -->
          <section class="station-config__card">
            <div class="station-config__section-head">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 5h14v14H5z" fill="none" stroke="currentColor" stroke-width="1.6" />
              </svg>
              <h3>目标区域选择</h3>
              <div class="station-config__tabs">
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': clusterAnalysisForm.area_type === 'smallRectangle' }"
                  type="button"
                  @click="setTargetAreaType('smallRectangle')"
                >
                  矩形区域
                </button>
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': clusterAnalysisForm.area_type === 'smallRound' }"
                  type="button"
                  @click="setTargetAreaType('smallRound')"
                >
                  圆形区域
                </button>
              </div>
            </div>

            <el-form
              v-show="clusterAnalysisForm.area_type === 'smallRectangle'"
              ref="rectangleFormRef"
              :rules="rectangleRules"
              :model="clusterAnalysisForm"
              label-position="top"
              class="station-config__form"
              require-asterisk-position="right"
              :show-message="false"
            >
              <div class="station-config__coord-row">
                <el-form-item label="初始点经度" prop="initialPointLng">
                  <el-input v-model="clusterAnalysisForm.initialPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="初始点纬度" prop="initialPointLat">
                  <el-input v-model="clusterAnalysisForm.initialPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <div class="station-config__coord-row">
                <el-form-item label="目标点经度" prop="destinationPointLng">
                  <el-input v-model="clusterAnalysisForm.destinationPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="目标点纬度" prop="destinationPointLat">
                  <el-input v-model="clusterAnalysisForm.destinationPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <button class="station-config__map-pick" type="button" @click="drawSmallGraph('smallRectangle')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>

            <el-form
              v-show="clusterAnalysisForm.area_type === 'smallRound'"
              ref="roundFormRef"
              :rules="roundRules"
              :model="clusterAnalysisForm"
              label-position="top"
              class="station-config__form"
              require-asterisk-position="right"
              :show-message="false"
            >
              <div class="station-config__coord-row">
                <el-form-item label="中心经度" prop="centerPointLng">
                  <el-input v-model="clusterAnalysisForm.centerPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="中心纬度" prop="centerPointLat">
                  <el-input v-model="clusterAnalysisForm.centerPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <el-form-item label="半径" prop="radius">
                <el-input v-model="clusterAnalysisForm.radius" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">km</span>
                  </template>
                </el-input>
              </el-form-item>
              <button class="station-config__map-pick" type="button" @click="drawSmallGraph('smallRound')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>
          </section>

          <!-- 中继区域 -->
          <section class="station-config__card">
            <div class="station-config__section-head">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.6" />
                <path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="1.4" />
              </svg>
              <h3>中继区域选择</h3>
              <div class="station-config__tabs">
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': clusterAnalysisFormRelay.area_type === 'relayRectangle' }"
                  type="button"
                  @click="setRelayAreaType('relayRectangle')"
                >
                  矩形区域
                </button>
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': clusterAnalysisFormRelay.area_type === 'relayRound' }"
                  type="button"
                  @click="setRelayAreaType('relayRound')"
                >
                  圆形区域
                </button>
                <button class="station-config__clear" type="button" @click="clearRelayArea">清除</button>
              </div>
            </div>

            <el-form
              v-show="clusterAnalysisFormRelay.area_type === 'relayRectangle'"
              :model="clusterAnalysisFormRelay"
              label-position="top"
              class="station-config__form"
            >
              <div class="station-config__coord-row">
                <el-form-item label="初始点经度">
                  <el-input v-model="clusterAnalysisFormRelay.initialPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="初始点纬度">
                  <el-input v-model="clusterAnalysisFormRelay.initialPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <div class="station-config__coord-row">
                <el-form-item label="目标点经度">
                  <el-input v-model="clusterAnalysisFormRelay.destinationPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="目标点纬度">
                  <el-input v-model="clusterAnalysisFormRelay.destinationPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <button class="station-config__map-pick" type="button" @click="drawRelayGraph('relayRectangle')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>

            <el-form
              v-show="clusterAnalysisFormRelay.area_type === 'relayRound'"
              :model="clusterAnalysisFormRelay"
              label-position="top"
              class="station-config__form"
            >
              <div class="station-config__coord-row">
                <el-form-item label="中心经度">
                  <el-input v-model="clusterAnalysisFormRelay.centerPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="中心纬度">
                  <el-input v-model="clusterAnalysisFormRelay.centerPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <el-form-item label="半径">
                <el-input v-model="clusterAnalysisFormRelay.radius" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">km</span>
                  </template>
                </el-input>
              </el-form-item>
              <button class="station-config__map-pick" type="button" @click="drawRelayGraph('relayRound')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>
          </section>

          <!-- 限制区域 -->
          <section class="station-config__card">
            <div class="station-config__section-head">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 4.5 19 8v8l-7 3.5L5 16V8z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linejoin="round"
                />
              </svg>
              <h3>限制区域选择</h3>
              <div class="station-config__tabs">
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': communicationAreaProhibitedForm.activeProhibitedName === 'Rectangle' }"
                  type="button"
                  @click="communicationAreaProhibitedForm.activeProhibitedName = 'Rectangle'"
                >
                  矩形区域
                </button>
                <button
                  class="station-config__tab"
                  :class="{ 'is-active': communicationAreaProhibitedForm.activeProhibitedName === 'Round' }"
                  type="button"
                  @click="communicationAreaProhibitedForm.activeProhibitedName = 'Round'"
                >
                  圆形区域
                </button>
                <button class="station-config__clear" type="button" @click="clearProhibitedArea">清除</button>
              </div>
            </div>

            <el-form
              v-show="communicationAreaProhibitedForm.activeProhibitedName === 'Rectangle'"
              :model="communicationAreaProhibitedForm"
              label-position="top"
              class="station-config__form"
            >
              <div class="station-config__coord-row">
                <el-form-item label="起点经度">
                  <el-input v-model="communicationAreaProhibitedForm.initialPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="起点纬度">
                  <el-input v-model="communicationAreaProhibitedForm.initialPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <div class="station-config__coord-row">
                <el-form-item label="终点经度">
                  <el-input v-model="communicationAreaProhibitedForm.destinationPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="终点纬度">
                  <el-input v-model="communicationAreaProhibitedForm.destinationPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <button class="station-config__map-pick" type="button" @click="drawGraph('prohibitedRectangle')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>

            <el-form
              v-show="communicationAreaProhibitedForm.activeProhibitedName === 'Round'"
              :model="communicationAreaProhibitedForm"
              label-position="top"
              class="station-config__form"
            >
              <div class="station-config__coord-row">
                <el-form-item label="中心点经度">
                  <el-input v-model="communicationAreaProhibitedForm.centerPointLng" placeholder="请输入" />
                </el-form-item>
                <el-form-item label="中心点纬度">
                  <el-input v-model="communicationAreaProhibitedForm.centerPointLat" placeholder="请输入" />
                </el-form-item>
              </div>
              <el-form-item label="目标区域半径">
                <el-input v-model="communicationAreaProhibitedForm.radius" placeholder="请输入">
                  <template #suffix>
                    <span class="station-config__unit">km</span>
                  </template>
                </el-input>
              </el-form-item>
              <button class="station-config__map-pick" type="button" @click="drawGraph('prohibitedRound')">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                    fill="currentColor"
                  />
                </svg>
                <span>地图绘制</span>
              </button>
            </el-form>
          </section>
        </div>

        <div class="station-config__footer">
          <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
            取消
          </button>
          <button
            class="station-config__btn station-config__btn--primary"
            type="button"
            :disabled="btnloading"
            @click="handleConfirmClusterAnalysis"
          >
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
            {{ btnloading ? "计算中..." : "确认" }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck
import { computed, getCurrentInstance, nextTick, onBeforeUnmount, ref, watch } from "vue";
import {
  validateLongitude,
  validateLatitude,
  formatLongitude,
  formatLatitude,
  parseLongitude,
  parseLatitude,
} from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const props = defineProps({
  id: {
    type: String,
    default: "",
  },
  tif_path: {
    type: String,
    default: "",
  },
  showClusterAnalysisSearchDialog: {
    type: Boolean,
    default: false,
  },
  clusterAnalysisForm: {
    type: Object,
    default: () => ({
      loss_threshold: "",
      limit_road_distance: "",
      eps_cells: "",
      min_samples: "",
      p: "",
      area_type: "smallRectangle",
      initialPointLng: "",
      initialPointLat: "",
      destinationPointLng: "",
      destinationPointLat: "",
      centerPointLng: "",
      centerPointLat: "",
      radius: "",
    }),
  },
  clusterAnalysisFormRelay: {
    type: Object,
    default: () => ({
      loss_threshold: "",
      limit_road_distance: "",
      eps_cells: "",
      min_samples: "",
      p: "",
      area_type: "relayRectangle",
      initialPointLng: "",
      initialPointLat: "",
      destinationPointLng: "",
      destinationPointLat: "",
      centerPointLng: "",
      centerPointLat: "",
      radius: "",
    }),
  },
  communicationAreaProhibitedForm: {
    type: Object,
    default: () => ({
      activeProhibitedName: "Rectangle",
      initialPointLng: "",
      initialPointLat: "",
      destinationPointLng: "",
      destinationPointLat: "",
      centerPointLng: "",
      centerPointLat: "",
      radius: "",
    }),
  },
});

const emit = defineEmits(["update:visible"]);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 720;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 520;
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
  () => props.showClusterAnalysisSearchDialog,
  (val) => {
    if (val) centerPanel();
  }
);

const setVisible = (val: boolean) => {
  emit("update:visible", val);
};

const pendingPickRestore = ref(false);
let pickEscHandler: ((e: KeyboardEvent) => void) | null = null;

const cleanupPickMode = () => {
  if (pickEscHandler) {
    window.removeEventListener("keydown", pickEscHandler);
    pickEscHandler = null;
  }
};

const finishPickMode = () => {
  if (!pendingPickRestore.value) return;
  pendingPickRestore.value = false;
  cleanupPickMode();
  setVisible(true);
};

const onDrawAreaEnd = () => {
  finishPickMode();
};

const beginMapDraw = (start: () => void) => {
  pendingPickRestore.value = true;
  setVisible(false);

  const onEsc = (e: KeyboardEvent) => {
    if (e.key !== "Escape") return;
    $bus.emit("cancelDrawPoint");
    finishPickMode();
  };
  pickEscHandler = onEsc;
  window.addEventListener("keydown", onEsc);

  start();
};

const setTargetAreaType = (val: string) => {
  props.clusterAnalysisForm.area_type = val;
  handleChangeAreaType(val);
};

const setRelayAreaType = (val: string) => {
  props.clusterAnalysisFormRelay.area_type = val;
  handleChangeRealyAreaType(val);
};

const handleChangeAreaType = (val: string) => {
  $bus.emit("changeCommunicationAreaType", val);
};

const handleChangeRealyAreaType = (val: string) => {
  $bus.emit("changeRelayCommunicationAreaType", val);
};

const drawSmallGraph = (type: string) => {
  beginMapDraw(() => $bus.emit("drawSmallCommunicationArea", type));
};

const updateSmallAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.toJSON().name === "smallRound") {
    props.clusterAnalysisForm.centerPointLng = formatLongitude(graphic.toJSON().position[0]);
    props.clusterAnalysisForm.centerPointLat = formatLatitude(graphic.toJSON().position[1]);
    props.clusterAnalysisForm.radius = graphic.toJSON().style.radius / 1000;
  } else if (graphic && graphic.toJSON().name === "smallRectangle") {
    props.clusterAnalysisForm.initialPointLng = formatLongitude(graphic.toJSON().positions[0][0]);
    props.clusterAnalysisForm.initialPointLat = formatLatitude(graphic.toJSON().positions[0][1]);
    props.clusterAnalysisForm.destinationPointLng = formatLongitude(graphic.toJSON().positions[1][0]);
    props.clusterAnalysisForm.destinationPointLat = formatLatitude(graphic.toJSON().positions[1][1]);
  }
};

$bus.on("drawSmallCommunicationAreaMsg", updateSmallAreaData);

const drawRelayGraph = (type: string) => {
  beginMapDraw(() => $bus.emit("drawRelayCommunicationArea", type));
};

const updateRelayAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.toJSON().name === "relayRound") {
    props.clusterAnalysisFormRelay.centerPointLng = formatLongitude(graphic.toJSON().position[0]);
    props.clusterAnalysisFormRelay.centerPointLat = formatLatitude(graphic.toJSON().position[1]);
    props.clusterAnalysisFormRelay.radius = graphic.toJSON().style.radius / 1000;
  } else if (graphic && graphic.toJSON().name === "relayRectangle") {
    props.clusterAnalysisFormRelay.initialPointLng = formatLongitude(graphic.toJSON().positions[0][0]);
    props.clusterAnalysisFormRelay.initialPointLat = formatLatitude(graphic.toJSON().positions[0][1]);
    props.clusterAnalysisFormRelay.destinationPointLng = formatLongitude(graphic.toJSON().positions[1][0]);
    props.clusterAnalysisFormRelay.destinationPointLat = formatLatitude(graphic.toJSON().positions[1][1]);
  }
};
$bus.on("drawRelayCommunicationAreaMsg", updateRelayAreaData);

const btnloading = ref(false);

const closeLoading = () => {
  btnloading.value = false;
};
$bus.on("closeLoading", closeLoading);

const clusterAnalysisFormRules = {
  loss_threshold: [{ required: true, message: "请输入损失阈值", trigger: "blur" }],
  eps_cells: [{ required: true, message: "请输入半径", trigger: "blur" }],
  min_samples: [{ required: true, message: "请输入最小样本数", trigger: "blur" }],
  limit_road_distance: [{ required: false, message: "请输入道路距离限制", trigger: "blur" }],
};
const rectangleRules = {
  initialPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  initialPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
  destinationPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  destinationPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
};

const roundRules = {
  centerPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
  centerPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
  radius: [{ required: true, message: "请输入半径", trigger: "change" }],
};

const clusterAnalysisFormRef = ref(null);
const rectangleFormRef = ref(null);
const roundFormRef = ref(null);

$bus.on("clusterAnalysisFailure", closeLoading);

const validateFormOrShake = async (formRef) => {
  const formEl = formRef?.value;
  if (!formEl) return false;
  try {
    await formEl.validate();
    return true;
  } catch {
    shakeInvalidFormFields(formEl);
    return false;
  }
};

const toNum = (v: any) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const appendRelayAndProhibitedToData = (data) => {
  let next = { ...data };
  if (props.clusterAnalysisFormRelay.area_type === "relayRectangle" && props.clusterAnalysisFormRelay.initialPointLng) {
    delete next.id;
    next.type = "rectangle area clustering";
    next.min_lon = parseLongitude(props.clusterAnalysisFormRelay.initialPointLng);
    next.min_lat = parseLatitude(props.clusterAnalysisFormRelay.initialPointLat);
    next.max_lon = parseLongitude(props.clusterAnalysisFormRelay.destinationPointLng);
    next.max_lat = parseLatitude(props.clusterAnalysisFormRelay.destinationPointLat);
  } else if (props.clusterAnalysisFormRelay.area_type === "relayRound" && props.clusterAnalysisFormRelay.centerPointLng) {
    delete next.id;
    next.type = "circle area clustering";
    next.center_lon = parseLongitude(props.clusterAnalysisFormRelay.centerPointLng);
    next.center_lat = parseLatitude(props.clusterAnalysisFormRelay.centerPointLat);
    next.radius_m = toNum(props.clusterAnalysisFormRelay.radius) * 1000;
  }

  if (
    props.communicationAreaProhibitedForm.activeProhibitedName == "Rectangle" &&
    props.communicationAreaProhibitedForm.initialPointLng
  ) {
    next = {
      ...next,
      prohibited_area_type: "rectangle",
      prohibited_min_lon: parseLongitude(props.communicationAreaProhibitedForm.initialPointLng),
      prohibited_min_lat: parseLatitude(props.communicationAreaProhibitedForm.initialPointLat),
      prohibited_max_lon: parseLongitude(props.communicationAreaProhibitedForm.destinationPointLng),
      prohibited_max_lat: parseLatitude(props.communicationAreaProhibitedForm.destinationPointLat),
    };
  } else if (
    props.communicationAreaProhibitedForm.activeProhibitedName == "Round" &&
    props.communicationAreaProhibitedForm.centerPointLng
  ) {
    next = {
      ...next,
      prohibited_area_type: "circle",
      prohibited_center_lon: parseLongitude(props.communicationAreaProhibitedForm.centerPointLng),
      prohibited_center_lat: parseLatitude(props.communicationAreaProhibitedForm.centerPointLat),
      prohibited_radius_m: toNum(props.communicationAreaProhibitedForm.radius) * 1000,
    };
  }
  return next;
};

const emitClusterAreas = () => {
  $bus.emit("setCommunicationArea", props.clusterAnalysisForm);
  if (props.clusterAnalysisFormRelay.initialPointLng || props.clusterAnalysisFormRelay.centerPointLng) {
    $bus.emit("setCommunicationArea", props.clusterAnalysisFormRelay);
  }
  if (
    props.communicationAreaProhibitedForm.initialPointLng ||
    props.communicationAreaProhibitedForm.centerPointLng
  ) {
    const prohibited = props.communicationAreaProhibitedForm;
    $bus.emit("setProhibitedCommunicationArea", {
      ...prohibited,
      activeName:
        prohibited.activeProhibitedName === "Round" ? "prohibitedRound" : "prohibitedRectangle",
    });
  }
};

const handleConfirmClusterAnalysis = async () => {
  if (!(await validateFormOrShake(clusterAnalysisFormRef))) return;

  if (props.clusterAnalysisForm.area_type === "smallRectangle") {
    if (!(await validateFormOrShake(rectangleFormRef))) return;

    btnloading.value = true;
    emitClusterAreas();
    const data = appendRelayAndProhibitedToData({
      type: "rectangle area clustering",
      id: props.id,
      tif_path: props.tif_path,
      loss_threshold: props.clusterAnalysisForm.loss_threshold,
      limit_road_distance: props.clusterAnalysisForm.limit_road_distance,
      eps_cells: props.clusterAnalysisForm.eps_cells,
      min_samples: props.clusterAnalysisForm.min_samples,
      p: props.clusterAnalysisForm.p,
      min_lon: parseLongitude(props.clusterAnalysisForm.initialPointLng),
      min_lat: parseLatitude(props.clusterAnalysisForm.initialPointLat),
      max_lon: parseLongitude(props.clusterAnalysisForm.destinationPointLng),
      max_lat: parseLatitude(props.clusterAnalysisForm.destinationPointLat),
    });
    $bus.emit("sendMessage", data);
    return;
  }

  if (props.clusterAnalysisForm.area_type === "smallRound") {
    if (!(await validateFormOrShake(roundFormRef))) return;

    btnloading.value = true;
    emitClusterAreas();
    const data = appendRelayAndProhibitedToData({
      type: "circle area clustering",
      id: props.id,
      tif_path: props.tif_path,
      loss_threshold: props.clusterAnalysisForm.loss_threshold,
      limit_road_distance: props.clusterAnalysisForm.limit_road_distance,
      eps_cells: props.clusterAnalysisForm.eps_cells,
      min_samples: props.clusterAnalysisForm.min_samples,
      p: props.clusterAnalysisForm.p,
      center_lon: parseLongitude(props.clusterAnalysisForm.centerPointLng),
      center_lat: parseLatitude(props.clusterAnalysisForm.centerPointLat),
      radius_m: toNum(props.clusterAnalysisForm.radius) * 1000,
    });
    $bus.emit("sendMessage", data);
  }
};

const drawGraph = (type: string) => {
  beginMapDraw(() => $bus.emit("drawCommunicationArea", type));
};

const updateProhibitedCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
  if (graphic && graphic.toJSON().name === "prohibitedRectangle") {
    props.communicationAreaProhibitedForm.initialPointLng = formatLongitude(graphic.toJSON().positions[0][0]);
    props.communicationAreaProhibitedForm.initialPointLat = formatLatitude(graphic.toJSON().positions[0][1]);
    props.communicationAreaProhibitedForm.destinationPointLng = formatLongitude(graphic.toJSON().positions[1][0]);
    props.communicationAreaProhibitedForm.destinationPointLat = formatLatitude(graphic.toJSON().positions[1][1]);
  } else if (graphic && graphic.toJSON().name === "prohibitedRound") {
    props.communicationAreaProhibitedForm.centerPointLng = formatLongitude(graphic.toJSON().position[0]);
    props.communicationAreaProhibitedForm.centerPointLat = formatLatitude(graphic.toJSON().position[1]);
    props.communicationAreaProhibitedForm.radius = graphic.toJSON().style.radius / 1000;
  }
};

$bus.on("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);
$bus.on("drawCommunicationAreaEnd", onDrawAreaEnd);

watch(
  () => props.communicationAreaProhibitedForm.activeProhibitedName,
  (newVal) => {
    $bus.emit("showProhibitedCommunicationArea", newVal);
  }
);

const clearProhibitedArea = () => {
  props.communicationAreaProhibitedForm.area_type = "rectangle";
  props.communicationAreaProhibitedForm.initialPointLng = "";
  props.communicationAreaProhibitedForm.initialPointLat = "";
  props.communicationAreaProhibitedForm.destinationPointLng = "";
  props.communicationAreaProhibitedForm.destinationPointLat = "";
  props.communicationAreaProhibitedForm.centerPointLng = "";
  props.communicationAreaProhibitedForm.centerPointLat = "";
  props.communicationAreaProhibitedForm.radius = "";
  $bus.emit("clearProhibitedArea");
};

const clearRelayArea = () => {
  props.clusterAnalysisFormRelay.area_type = "relayRectangle";
  props.clusterAnalysisFormRelay.initialPointLng = "";
  props.clusterAnalysisFormRelay.initialPointLat = "";
  props.clusterAnalysisFormRelay.destinationPointLng = "";
  props.clusterAnalysisFormRelay.destinationPointLat = "";
  props.clusterAnalysisFormRelay.centerPointLng = "";
  props.clusterAnalysisFormRelay.centerPointLat = "";
  props.clusterAnalysisFormRelay.radius = "";
  $bus.emit("clearRelayArea");
};

onBeforeUnmount(() => {
  stopDrag();
  cleanupPickMode();
  $bus.off("closeLoading", closeLoading);
  $bus.off("clusterAnalysisFailure", closeLoading);
  $bus.off("drawSmallCommunicationAreaMsg", updateSmallAreaData);
  $bus.off("drawRelayCommunicationAreaMsg", updateRelayAreaData);
  $bus.off("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);
  $bus.off("drawCommunicationAreaEnd", onDrawAreaEnd);
});
</script>

<style lang="scss" scoped>
.station-config {
  position: fixed;
  z-index: 1200;
  width: min(720px, calc(100vw - 48px));
  pointer-events: all;
  box-sizing: border-box;

  &__panel {
    position: relative;
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 72px);
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
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 28px;
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
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  &__card {
    width: 100%;
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
    flex-wrap: wrap;

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
    }

    .station-config__tabs {
      margin-left: auto;
    }
  }

  &__tabs {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  &__tab {
    height: 32px;
    padding: 0 16px;
    border-radius: 9999px;
    border: 1px solid #404945;
    background: #18221c;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;
    transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;

    &:hover {
      border-color: #8a938e;
      color: #dae5dc;
    }

    &.is-active {
      border-color: rgba(157, 223, 46, 0.4);
      background: rgba(157, 223, 46, 0.1);
      color: #9ddf2e;
    }
  }

  &__clear {
    height: 32px;
    padding: 0 16px;
    border-radius: 9999px;
    border: 1px solid #404945;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;
    transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;

    &:hover {
      border-color: #8a938e;
      color: #dae5dc;
      background: rgba(45, 55, 49, 0.5);
    }
  }

  &__row-2 {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 0 12px;
    width: 100%;
  }

  &__coord-row {
    --coord-h: 42px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 12px;
    width: 100%;
    margin-bottom: 4px;

    :deep(.el-form-item) {
      margin-bottom: 14px !important;
      width: 100% !important;
    }

    :deep(.el-form-item__content),
    :deep(.el-input),
    :deep(.el-input__wrapper) {
      width: 100% !important;
    }

    :deep(.el-input__wrapper) {
      height: var(--coord-h) !important;
      min-height: var(--coord-h) !important;
      box-sizing: border-box !important;
      padding: 8px 12px !important;
      background: #07100b !important;
      border: 1px solid rgba(64, 73, 69, 0.5) !important;
      border-radius: 0.5rem !important;
      box-shadow: none !important;
      outline: none !important;
    }

    :deep(.el-input__wrapper.is-focus) {
      border-color: #9ddf2e !important;
      border-width: 2px !important;
      box-shadow: none !important;
    }

    :deep(.el-input__inner) {
      font-family: Inter, "Noto Sans SC", sans-serif !important;
      font-size: 16px !important;
      color: #ffffff !important;
      white-space: pre !important;
    }
  }

  &__map-pick {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 24px;
    margin: 4px 0 0;
    padding: 0 14px;
    border-radius: 9999px;
    border: 1px dashed #8a938e;
    background: transparent;
    color: #c0c8c3;
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    white-space: nowrap;
    cursor: pointer;

    svg {
      width: 14px;
      height: 14px;
      flex-shrink: 0;
    }

    span {
      transform: translateY(1px);
    }

    &:hover {
      border-color: #dae5dc;
      color: #dae5dc;
      background: rgba(45, 55, 49, 0.35);
    }
  }

  &__unit {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 14px !important;
    color: #a1d1bf !important;
    pointer-events: none;
  }

  &__footer {
    display: flex !important;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(64, 73, 69, 0.2) !important;
    background: rgba(45, 55, 49, 0.3) !important;
    flex-shrink: 0;
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
      opacity: 0.65;
      cursor: not-allowed;
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

  :deep(.el-form-item) {
    margin-bottom: 16px;
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

  :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
  :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
    color: #ffb4ab !important;
  }

  :deep(.station-config__form .el-input__wrapper) {
    background: #07100b !important;
    border: 1px solid rgba(180, 200, 220, 0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 40px;
  }

  :deep(.station-config__form .el-input__wrapper:hover) {
    border-color: rgba(180, 200, 220, 0.32) !important;
  }

  :deep(.station-config__form .el-input__wrapper.is-focus) {
    border-color: #9ddf2e !important;
    border-width: 2px !important;
    box-shadow: none !important;
  }

  :deep(.station-config__form .el-input__inner) {
    font-family: Inter, "Noto Sans SC", sans-serif !important;
    font-size: 16px !important;
    color: #dae5dc !important;
  }

  :deep(.station-config__form .el-input__inner::placeholder) {
    color: rgba(192, 200, 195, 0.7) !important;
  }

  :deep(.station-config__form .el-form-item.is-error .el-input__wrapper) {
    border-color: #ffb4ab !important;
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
