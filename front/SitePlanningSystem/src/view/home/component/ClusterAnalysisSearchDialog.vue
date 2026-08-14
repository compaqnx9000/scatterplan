<template>
    <transition name="station-fade">
        <div
            v-if="showClusterAnalysisSearchDialog"
            ref="panelRef"
            class="station-config"
            :style="panelStyle"
        >
            <div class="station-config__panel">
                <div class="station-config__header" @mousedown="startDrag">
                    <div class="station-config__title">聚类分析及站点推荐列表查询</div>
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

                <div class="station-config__scroll">
                    <el-form
                        ref="clusterAnalysisFormRef"
                        :rules="clusterAnalysisFormRules"
                        :model="clusterAnalysisForm"
                        label-position="top"
                        class="station-config__form"
                    >
                        <section class="station-config__card">
                            <h3 class="station-config__card-title">参数配置</h3>
                            <div class="station-config__row-2">
                                <el-form-item label="邻域距离阈值（m）" prop="eps_cells">
                                    <el-input v-model="clusterAnalysisForm.eps_cells" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="邻域样本个体阈值（个）" prop="min_samples">
                                    <el-input v-model="clusterAnalysisForm.min_samples" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="传输损耗值的约束条件（dB）" prop="loss_threshold">
                                    <el-input v-model="clusterAnalysisForm.loss_threshold" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="道路距离限制（m）" prop="limit_road_distance">
                                    <el-input v-model="clusterAnalysisForm.limit_road_distance" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                        </section>
                    </el-form>

                    <!-- 目标区域 -->
                    <section class="station-config__card">
                        <div class="station-config__section-head">
                            <h3 class="station-config__card-title">目标区域选择</h3>
                            <div class="station-config__tabs">
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': clusterAnalysisForm.area_type === 'smallRectangle' }"
                                    type="button"
                                    @click="setTargetAreaType('smallRectangle')"
                                >
                                    矩形区域选择
                                </button>
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': clusterAnalysisForm.area_type === 'smallRound' }"
                                    type="button"
                                    @click="setTargetAreaType('smallRound')"
                                >
                                    圆形区域选择
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
                        >
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="targetRectCoordDisplay" placeholder="初始点, 目标点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawSmallGraph('smallRectangle')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="初始点经度（°）" prop="initialPointLng">
                                    <el-input v-model="clusterAnalysisForm.initialPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="初始点纬度（°）" prop="initialPointLat">
                                    <el-input v-model="clusterAnalysisForm.initialPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="目标点经度（°）" prop="destinationPointLng">
                                    <el-input v-model="clusterAnalysisForm.destinationPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="目标点纬度（°）" prop="destinationPointLat">
                                    <el-input v-model="clusterAnalysisForm.destinationPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                        </el-form>

                        <el-form
                            v-show="clusterAnalysisForm.area_type === 'smallRound'"
                            ref="roundFormRef"
                            :rules="roundRules"
                            :model="clusterAnalysisForm"
                            label-position="top"
                            class="station-config__form"
                        >
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="targetRoundCoordDisplay" placeholder="中心点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawSmallGraph('smallRound')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="中心经度（°）" prop="centerPointLng">
                                    <el-input v-model="clusterAnalysisForm.centerPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="中心纬度（°）" prop="centerPointLat">
                                    <el-input v-model="clusterAnalysisForm.centerPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                            <el-form-item label="半径（km）" prop="radius">
                                <el-input v-model="clusterAnalysisForm.radius" placeholder="请输入" clearable />
                            </el-form-item>
                        </el-form>
                    </section>

                    <!-- 中继区域 -->
                    <section class="station-config__card">
                        <div class="station-config__section-head">
                            <h3 class="station-config__card-title">中继区域选择</h3>
                            <div class="station-config__tabs">
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': clusterAnalysisFormRelay.area_type === 'relayRectangle' }"
                                    type="button"
                                    @click="setRelayAreaType('relayRectangle')"
                                >
                                    矩形区域选择
                                </button>
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': clusterAnalysisFormRelay.area_type === 'relayRound' }"
                                    type="button"
                                    @click="setRelayAreaType('relayRound')"
                                >
                                    圆形区域选择
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
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="relayRectCoordDisplay" placeholder="初始点, 目标点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawRelayGraph('relayRectangle')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="初始点经度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.initialPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="初始点纬度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.initialPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="目标点经度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.destinationPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="目标点纬度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.destinationPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                        </el-form>

                        <el-form
                            v-show="clusterAnalysisFormRelay.area_type === 'relayRound'"
                            :model="clusterAnalysisFormRelay"
                            label-position="top"
                            class="station-config__form"
                        >
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="relayRoundCoordDisplay" placeholder="中心点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawRelayGraph('relayRound')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="中心经度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.centerPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="中心纬度（°）">
                                    <el-input v-model="clusterAnalysisFormRelay.centerPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                            <el-form-item label="半径（km）">
                                <el-input v-model="clusterAnalysisFormRelay.radius" placeholder="请输入" clearable />
                            </el-form-item>
                        </el-form>
                    </section>

                    <!-- 限制区域 -->
                    <section class="station-config__card">
                        <div class="station-config__section-head">
                            <h3 class="station-config__card-title">限制区域选择</h3>
                            <div class="station-config__tabs">
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': communicationAreaProhibitedForm.activeProhibitedName === 'Rectangle' }"
                                    type="button"
                                    @click="communicationAreaProhibitedForm.activeProhibitedName = 'Rectangle'"
                                >
                                    矩形区域选择
                                </button>
                                <button
                                    class="station-config__tab"
                                    :class="{ 'is-active': communicationAreaProhibitedForm.activeProhibitedName === 'Round' }"
                                    type="button"
                                    @click="communicationAreaProhibitedForm.activeProhibitedName = 'Round'"
                                >
                                    圆形区域选择
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
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="prohibitedRectCoordDisplay" placeholder="起点, 终点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawGraph('prohibitedRectangle')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="起点经度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.initialPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="起点纬度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.initialPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="终点经度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.destinationPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="终点纬度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.destinationPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                        </el-form>

                        <el-form
                            v-show="communicationAreaProhibitedForm.activeProhibitedName === 'Round'"
                            :model="communicationAreaProhibitedForm"
                            label-position="top"
                            class="station-config__form"
                        >
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="prohibitedRoundCoordDisplay" placeholder="中心点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawGraph('prohibitedRound')">
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path
                                                d="M12 3.2c-3.4 0-6.2 2.7-6.2 6.1 0 4.5 5.4 10.4 5.7 10.7l.5.5.5-.5c.3-.3 5.7-6.2 5.7-10.7 0-3.4-2.8-6.1-6.2-6.1Zm0 8.4a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6Z"
                                                fill="currentColor"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </el-form-item>
                            <div class="station-config__row-2">
                                <el-form-item label="中心点经度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.centerPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="中心点纬度（°）">
                                    <el-input v-model="communicationAreaProhibitedForm.centerPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                            <el-form-item label="目标区域半径（km）">
                                <el-input v-model="communicationAreaProhibitedForm.radius" placeholder="请输入" clearable />
                            </el-form-item>
                        </el-form>
                    </section>
                </div>

                <div class="station-config__footer">
                    <div class="station-config__footer-left">
                        <button class="station-config__btn station-config__btn--ghost" type="button" @click="setVisible(false)">
                            取消
                        </button>
                    </div>
                    <button
                        class="station-config__btn station-config__btn--primary"
                        type="button"
                        :disabled="btnloading"
                        @click="handleConfirmClusterAnalysis"
                    >
                        <span>{{ btnloading ? '计算中...' : '确认' }}</span>
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
//@ts-nocheck
import { computed, getCurrentInstance, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { validateLongitude, validateLatitude } from "@/view/home/service/rules";

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
const PANEL_WIDTH = 760;

const panelStyle = computed(() => ({
    left: `${panelPos.value.x}px`,
    top: `${panelPos.value.y}px`,
    width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const targetRectCoordDisplay = computed(() => {
    const f = props.clusterAnalysisForm;
    if (!f.initialPointLng || !f.initialPointLat || !f.destinationPointLng || !f.destinationPointLat) return "";
    return `${f.initialPointLng}, ${f.initialPointLat}  →  ${f.destinationPointLng}, ${f.destinationPointLat}`;
});

const targetRoundCoordDisplay = computed(() => {
    const f = props.clusterAnalysisForm;
    if (!f.centerPointLng || !f.centerPointLat) return "";
    return `${f.centerPointLng}, ${f.centerPointLat}`;
});

const relayRectCoordDisplay = computed(() => {
    const f = props.clusterAnalysisFormRelay;
    if (!f.initialPointLng || !f.initialPointLat || !f.destinationPointLng || !f.destinationPointLat) return "";
    return `${f.initialPointLng}, ${f.initialPointLat}  →  ${f.destinationPointLng}, ${f.destinationPointLat}`;
});

const relayRoundCoordDisplay = computed(() => {
    const f = props.clusterAnalysisFormRelay;
    if (!f.centerPointLng || !f.centerPointLat) return "";
    return `${f.centerPointLng}, ${f.centerPointLat}`;
});

const prohibitedRectCoordDisplay = computed(() => {
    const f = props.communicationAreaProhibitedForm;
    if (!f.initialPointLng || !f.initialPointLat || !f.destinationPointLng || !f.destinationPointLat) return "";
    return `${f.initialPointLng}, ${f.initialPointLat}  →  ${f.destinationPointLng}, ${f.destinationPointLat}`;
});

const prohibitedRoundCoordDisplay = computed(() => {
    const f = props.communicationAreaProhibitedForm;
    if (!f.centerPointLng || !f.centerPointLat) return "";
    return `${f.centerPointLng}, ${f.centerPointLat}`;
});

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
        props.clusterAnalysisForm.centerPointLng = graphic.toJSON().position[0];
        props.clusterAnalysisForm.centerPointLat = graphic.toJSON().position[1];
        props.clusterAnalysisForm.radius = graphic.toJSON().style.radius / 1000;
    } else if (graphic && graphic.toJSON().name === "smallRectangle") {
        props.clusterAnalysisForm.initialPointLng = graphic.toJSON().positions[0][0];
        props.clusterAnalysisForm.initialPointLat = graphic.toJSON().positions[0][1];
        props.clusterAnalysisForm.destinationPointLng = graphic.toJSON().positions[1][0];
        props.clusterAnalysisForm.destinationPointLat = graphic.toJSON().positions[1][1];
    }
};

$bus.on("drawSmallCommunicationAreaMsg", updateSmallAreaData);

const drawRelayGraph = (type: string) => {
    beginMapDraw(() => $bus.emit("drawRelayCommunicationArea", type));
};

const updateRelayAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
    if (graphic && graphic.toJSON().name === "relayRound") {
        props.clusterAnalysisFormRelay.centerPointLng = graphic.toJSON().position[0];
        props.clusterAnalysisFormRelay.centerPointLat = graphic.toJSON().position[1];
        props.clusterAnalysisFormRelay.radius = graphic.toJSON().style.radius / 1000;
    } else if (graphic && graphic.toJSON().name === "relayRectangle") {
        props.clusterAnalysisFormRelay.initialPointLng = graphic.toJSON().positions[0][0];
        props.clusterAnalysisFormRelay.initialPointLat = graphic.toJSON().positions[0][1];
        props.clusterAnalysisFormRelay.destinationPointLng = graphic.toJSON().positions[1][0];
        props.clusterAnalysisFormRelay.destinationPointLat = graphic.toJSON().positions[1][1];
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
    initialPointLng: [{ required: true, validator: validateLongitude, trigger: ["focus", "change"] }],
    initialPointLat: [{ required: true, validator: validateLatitude, trigger: ["focus", "change"] }],
    destinationPointLng: [{ required: true, validator: validateLongitude, trigger: ["focus", "change"] }],
    destinationPointLat: [{ required: true, validator: validateLatitude, trigger: ["focus", "change"] }],
};

const roundRules = {
    centerPointLng: [{ required: true, validator: validateLongitude, trigger: ["focus", "change"] }],
    centerPointLat: [{ required: true, validator: validateLatitude, trigger: ["focus", "change"] }],
    radius: [{ required: true, message: "请输入半径", trigger: "blur" }],
};

const clusterAnalysisFormRef = ref(null);
const rectangleFormRef = ref(null);
const roundFormRef = ref(null);

$bus.on("clusterAnalysisFailure", closeLoading);

const handleConfirmClusterAnalysis = async () => {
    await clusterAnalysisFormRef.value?.validate((valid) => {
        if (!valid) {
            ElMessage.error("请填写完整信息");
            return;
        }
    });

    if (props.clusterAnalysisForm.area_type === "smallRectangle") {
        await rectangleFormRef.value?.validate((valid) => {
            if (valid) {
                btnloading.value = true;
                $bus.emit("setCommunicationArea", props.clusterAnalysisForm);
                if (props.clusterAnalysisFormRelay.initialPointLng || props.clusterAnalysisFormRelay.centerPointLng) {
                    $bus.emit("setCommunicationArea", props.clusterAnalysisFormRelay);
                }
                let data = {
                    type: "rectangle area clustering",
                    id: props.id,
                    tif_path: props.tif_path,
                    loss_threshold: props.clusterAnalysisForm.loss_threshold,
                    limit_road_distance: props.clusterAnalysisForm.limit_road_distance,
                    eps_cells: props.clusterAnalysisForm.eps_cells,
                    min_samples: props.clusterAnalysisForm.min_samples,
                    p: props.clusterAnalysisForm.p,
                    min_lon: props.clusterAnalysisForm.initialPointLng,
                    min_lat: props.clusterAnalysisForm.initialPointLat,
                    max_lon: props.clusterAnalysisForm.destinationPointLng,
                    max_lat: props.clusterAnalysisForm.destinationPointLat,
                };
                if (props.clusterAnalysisFormRelay.area_type === "relayRectangle" && props.clusterAnalysisFormRelay.initialPointLng) {
                    delete data.id;
                    data.type = "rectangle area clustering";
                    data.min_lon = props.clusterAnalysisFormRelay.initialPointLng;
                    data.min_lat = props.clusterAnalysisFormRelay.initialPointLat;
                    data.max_lon = props.clusterAnalysisFormRelay.destinationPointLng;
                    data.max_lat = props.clusterAnalysisFormRelay.destinationPointLat;
                } else if (props.clusterAnalysisFormRelay.area_type === "relayRound" && props.clusterAnalysisFormRelay.centerPointLng) {
                    delete data.id;
                    data.type = "circle area clustering";
                    data.center_lon = props.clusterAnalysisFormRelay.centerPointLng;
                    data.center_lat = props.clusterAnalysisFormRelay.centerPointLat;
                    data.radius_m = props.clusterAnalysisFormRelay.radius * 1000;
                }
                if (
                    props.communicationAreaProhibitedForm.activeProhibitedName == "Rectangle" &&
                    props.communicationAreaProhibitedForm.initialPointLng
                ) {
                    data = {
                        ...data,
                        prohibited_area_type: "rectangle",
                        prohibited_min_lon: props.communicationAreaProhibitedForm.initialPointLng,
                        prohibited_min_lat: props.communicationAreaProhibitedForm.initialPointLat,
                        prohibited_max_lon: props.communicationAreaProhibitedForm.destinationPointLng,
                        prohibited_max_lat: props.communicationAreaProhibitedForm.destinationPointLat,
                    };
                } else if (
                    props.communicationAreaProhibitedForm.activeProhibitedName == "Round" &&
                    props.communicationAreaProhibitedForm.centerPointLng
                ) {
                    data = {
                        ...data,
                        prohibited_area_type: "circle",
                        prohibited_center_lon: props.communicationAreaProhibitedForm.centerPointLng,
                        prohibited_center_lat: props.communicationAreaProhibitedForm.centerPointLat,
                        prohibited_radius_m: props.communicationAreaProhibitedForm.radius * 1000,
                    };
                }
                $bus.emit("sendMessage", data);
            } else {
                ElMessage.error("请填写完整信息");
            }
        });
    } else if (props.clusterAnalysisForm.area_type === "smallRound") {
        await roundFormRef.value?.validate((valid) => {
            if (valid) {
                btnloading.value = true;
                $bus.emit("setCommunicationArea", props.clusterAnalysisForm);
                if (props.clusterAnalysisFormRelay.initialPointLng || props.clusterAnalysisFormRelay.centerPointLng) {
                    $bus.emit("setCommunicationArea", props.clusterAnalysisFormRelay);
                }
                if (
                    props.communicationAreaProhibitedForm.initialPointLng ||
                    props.communicationAreaProhibitedForm.centerPointLng
                ) {
                    $bus.emit("setCommunicationArea", props.communicationAreaProhibitedForm);
                }
                let data = {
                    type: "circle area clustering",
                    id: props.id,
                    tif_path: props.tif_path,
                    loss_threshold: props.clusterAnalysisForm.loss_threshold,
                    limit_road_distance: props.clusterAnalysisForm.limit_road_distance,
                    eps_cells: props.clusterAnalysisForm.eps_cells,
                    min_samples: props.clusterAnalysisForm.min_samples,
                    p: props.clusterAnalysisForm.p,
                    center_lon: props.clusterAnalysisForm.centerPointLng,
                    center_lat: props.clusterAnalysisForm.centerPointLat,
                    radius_m: props.clusterAnalysisForm.radius * 1000,
                };

                if (props.clusterAnalysisFormRelay.area_type === "relayRectangle" && props.clusterAnalysisFormRelay.initialPointLng) {
                    delete data.id;
                    data.type = "rectangle area clustering";
                    data.min_lon = props.clusterAnalysisFormRelay.initialPointLng;
                    data.min_lat = props.clusterAnalysisFormRelay.initialPointLat;
                    data.max_lon = props.clusterAnalysisFormRelay.destinationPointLng;
                    data.max_lat = props.clusterAnalysisFormRelay.destinationPointLat;
                } else if (props.clusterAnalysisFormRelay.area_type === "relayRound" && props.clusterAnalysisFormRelay.centerPointLng) {
                    delete data.id;
                    data.type = "circle area clustering";
                    data.center_lon = props.clusterAnalysisFormRelay.centerPointLng;
                    data.center_lat = props.clusterAnalysisFormRelay.centerPointLat;
                    data.radius_m = props.clusterAnalysisFormRelay.radius * 1000;
                }

                if (
                    props.communicationAreaProhibitedForm.activeProhibitedName == "Rectangle" &&
                    props.communicationAreaProhibitedForm.initialPointLng
                ) {
                    data = {
                        ...data,
                        prohibited_area_type: "rectangle",
                        prohibited_min_lon: props.communicationAreaProhibitedForm.initialPointLng,
                        prohibited_min_lat: props.communicationAreaProhibitedForm.initialPointLat,
                        prohibited_max_lon: props.communicationAreaProhibitedForm.destinationPointLng,
                        prohibited_max_lat: props.communicationAreaProhibitedForm.destinationPointLat,
                    };
                } else if (
                    props.communicationAreaProhibitedForm.activeProhibitedName == "Round" &&
                    props.communicationAreaProhibitedForm.centerPointLng
                ) {
                    data = {
                        ...data,
                        prohibited_area_type: "circle",
                        prohibited_center_lon: props.communicationAreaProhibitedForm.centerPointLng,
                        prohibited_center_lat: props.communicationAreaProhibitedForm.centerPointLat,
                        prohibited_radius_m: props.communicationAreaProhibitedForm.radius * 1000,
                    };
                }
                $bus.emit("sendMessage", data);
            } else {
                ElMessage.error("请填写完整信息");
            }
        });
    }
};

const drawGraph = (type: string) => {
    beginMapDraw(() => $bus.emit("drawCommunicationArea", type));
};

const updateProhibitedCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
    if (graphic && graphic.toJSON().name === "prohibitedRectangle") {
        props.communicationAreaProhibitedForm.initialPointLng = graphic.toJSON().positions[0][0];
        props.communicationAreaProhibitedForm.initialPointLat = graphic.toJSON().positions[0][1];
        props.communicationAreaProhibitedForm.destinationPointLng = graphic.toJSON().positions[1][0];
        props.communicationAreaProhibitedForm.destinationPointLat = graphic.toJSON().positions[1][1];
    } else if (graphic && graphic.toJSON().name === "prohibitedRound") {
        props.communicationAreaProhibitedForm.centerPointLng = graphic.toJSON().position[0];
        props.communicationAreaProhibitedForm.centerPointLat = graphic.toJSON().position[1];
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
    pointer-events: all;
    box-sizing: border-box;

    *,
    *::before,
    *::after {
        box-sizing: border-box;
    }

    &__panel {
        width: 100%;
        max-height: calc(100vh - 72px);
        display: flex;
        flex-direction: column;
        padding: 18px 20px 16px;
        border-radius: 14px;
        background: rgba(26, 34, 44, 0.72);
        border: 1px solid rgba(180, 200, 220, 0.18);
        box-shadow:
            0 18px 48px rgba(0, 0, 0, 0.38),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(22px) saturate(1.15);
        -webkit-backdrop-filter: blur(22px) saturate(1.15);
        color: #ffffff;
        overflow: hidden;
    }

    &__scroll {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        padding-right: 4px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    &__header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
        cursor: move;
        user-select: none;
        flex-shrink: 0;
    }

    &__title {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
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

        svg {
            width: 18px;
            height: 18px;
        }

        &:hover {
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
        }
    }

    &__section-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }

    &__tabs {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }

    &__tab {
        height: 30px;
        padding: 0 12px;
        border-radius: 8px;
        border: 1px solid rgba(180, 200, 220, 0.16);
        background: rgba(18, 24, 31, 0.55);
        color: rgba(220, 228, 236, 0.8);
        font-size: 12px;
        cursor: pointer;

        &:hover {
            color: #fff;
        }

        &.is-active {
            background: rgba(0, 162, 255, 0.18);
            border-color: rgba(0, 162, 255, 0.45);
            color: #ffffff;
        }
    }

    &__clear {
        height: 30px;
        padding: 0 12px;
        border-radius: 8px;
        border: 1px solid rgba(0, 162, 255, 0.35);
        background: rgba(0, 162, 255, 0.16);
        color: #ffffff;
        font-size: 12px;
        cursor: pointer;

        &:hover {
            background: rgba(0, 162, 255, 0.28);
        }
    }

    &__card {
        width: 100%;
        min-width: 0;
        padding: 14px 12px 6px;
        border-radius: 10px;
        background: rgba(18, 24, 31, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    &__card-title {
        margin: 0;
        font-size: 12px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.95);
    }

    &__row-2 {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 0 12px;
    }

    &__coord-row {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        min-width: 0;

        :deep(.el-input) {
            flex: 1;
            min-width: 0;
            width: auto !important;
        }
    }

    &__map-btn {
        width: 36px;
        height: 36px;
        flex-shrink: 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        background: rgba(26, 34, 44, 0.72);
        color: #8ec8ff;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;

        svg {
            width: 18px;
            height: 18px;
        }

        &:hover {
            background: #303841;
            color: #b7dcff;
        }
    }

    &__footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 14px;
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

        &:disabled {
            opacity: 0.65;
            cursor: not-allowed;
        }

        &--ghost {
            min-width: 72px;
            height: 40px;
            padding: 0 16px;
            border-radius: 8px;
            background: rgba(38, 44, 53, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(235, 240, 245, 0.92);

            &:hover {
                background: rgba(48, 56, 66, 0.95);
            }
        }

        &--primary {
            min-width: 120px;
            height: 44px;
            padding: 0 16px 0 20px;
            border-radius: 999px;
            background: linear-gradient(90deg, #00a2ff 0%, #3b82f6 100%);
            box-shadow: 0 8px 24px rgba(0, 162, 255, 0.38);
            font-weight: 600;

            &:hover:not(:disabled) {
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

        svg {
            width: 14px;
            height: 14px;
        }
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

    :deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-right > .el-form-item__label:after),
    :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label:before) {
        color: #ff6b6b;
    }

    :deep(.station-config__form .el-input),
    :deep(.station-config__form .el-input__wrapper),
    :deep(.station-config__form .el-input .el-input__wrapper) {
        width: 100% !important;
        max-width: 100% !important;
    }

    :deep(.station-config__form .el-input__wrapper),
    :deep(.station-config__form .el-input .el-input__wrapper) {
        background: rgba(26, 34, 44, 0.72) !important;
        background-color: rgba(26, 34, 44, 0.72) !important;
        background-image: none !important;
        border: 1px solid rgba(180, 200, 220, 0.18) !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        min-height: 36px;
    }

    :deep(.station-config__form .el-input__wrapper:hover),
    :deep(.station-config__form .el-input__wrapper.is-focus) {
        border-color: rgba(0, 162, 255, 0.45) !important;
        box-shadow: none !important;
        background: rgba(26, 34, 44, 0.72) !important;
        background-color: rgba(26, 34, 44, 0.72) !important;
        background-image: none !important;
    }

    :deep(.station-config__form .el-input__inner) {
        color: #ffffff !important;
        font-size: 12px !important;
    }

    :deep(.station-config__form .el-input__inner::placeholder) {
        color: #6b7280 !important;
    }

    :deep(.station-config__form .el-form-item__error) {
        color: #ff7b7b;
        font-size: 11px;
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
