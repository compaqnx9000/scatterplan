<template>
    <transition name="station-fade">
        <div
            v-if="showCommunicationAreaDialog"
            ref="panelRef"
            class="station-config"
            :style="panelStyle"
        >
            <div class="station-config__panel">
                <div class="station-config__header" @mousedown="startDrag">
                    <div class="station-config__title">区域覆盖计算适配</div>
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

                <div class="station-config__tabs">
                    <button
                        class="station-config__tab"
                        :class="{ 'is-active': CommunicationArea.activeName === 'Rectangle' }"
                        type="button"
                        @click="CommunicationArea.activeName = 'Rectangle'"
                    >
                        矩形区域选择
                    </button>
                    <button
                        class="station-config__tab"
                        :class="{ 'is-active': CommunicationArea.activeName === 'Round' }"
                        type="button"
                        @click="CommunicationArea.activeName = 'Round'"
                    >
                        圆形区域选择
                    </button>
                </div>

                <div v-show="CommunicationArea.activeName === 'Rectangle'">
                    <el-form
                        ref="RectangleFormRef"
                        :rules="rules.Rectangle"
                        :model="CommunicationArea"
                        label-position="top"
                        class="station-config__form"
                        :show-message="false"
                    >
                        <section class="station-config__card">
                            <h3 class="station-config__card-title">矩形区域</h3>
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="rectangleCoordDisplay" placeholder="起点, 终点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawGraph('Rectangle')">
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
                                <el-form-item label="起点经度（°）" prop="initialPointLng">
                                    <el-input v-model="CommunicationArea.initialPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="起点纬度（°）" prop="initialPointLat">
                                    <el-input v-model="CommunicationArea.initialPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="终点经度（°）" prop="destinationPointLng">
                                    <el-input v-model="CommunicationArea.destinationPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="终点纬度（°）" prop="destinationPointLat">
                                    <el-input v-model="CommunicationArea.destinationPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                        </section>
                    </el-form>
                </div>

                <div v-show="CommunicationArea.activeName === 'Round'">
                    <el-form
                        ref="roundFormRef"
                        :rules="rules.round"
                        :model="CommunicationArea"
                        label-position="top"
                        class="station-config__form"
                        :show-message="false"
                    >
                        <section class="station-config__card">
                            <h3 class="station-config__card-title">圆形区域</h3>
                            <el-form-item label="坐标">
                                <div class="station-config__coord-row">
                                    <el-input :model-value="roundCoordDisplay" placeholder="中心点" readonly />
                                    <button class="station-config__map-btn" type="button" title="地图绘制" @click="drawGraph('round')">
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
                                <el-form-item label="中心点经度（°）" prop="centerPointLng">
                                    <el-input v-model="CommunicationArea.centerPointLng" placeholder="请输入" clearable />
                                </el-form-item>
                                <el-form-item label="中心点纬度（°）" prop="centerPointLat">
                                    <el-input v-model="CommunicationArea.centerPointLat" placeholder="请输入" clearable />
                                </el-form-item>
                            </div>
                            <el-form-item label="目标区域半径（km）" prop="radius">
                                <el-input v-model="CommunicationArea.radius" placeholder="请输入" clearable />
                            </el-form-item>
                        </section>
                    </el-form>
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
                        @click="handleConfirmCommunicationArea"
                    >
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
//@ts-nocheck

import { computed, getCurrentInstance, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { validateLongitude, validateLatitude } from "@/view/home/service/rules";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const RectangleRules = {
    initialPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
    initialPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
    destinationPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
    destinationPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
};
const RoundRules = {
    centerPointLng: [{ required: true, validator: validateLongitude, trigger: "change" }],
    centerPointLat: [{ required: true, validator: validateLatitude, trigger: "change" }],
    radius: [{ required: true, message: "请输入半径", trigger: "change" }],
};
const rules = {
    Rectangle: RectangleRules,
    round: RoundRules,
};

const props = defineProps({
    showCommunicationAreaDialog: {
        type: Boolean,
        default: false,
    },
    CommunicationArea: {
        type: Object,
        default: () => ({
            activeName: "Rectangle",
            initialPointLng: "",
            initialPointLat: "",
            destinationPointLng: "",
            destinationPointLat: "",
            centerPointLng: "",
            centerPointLat: "",
            radius: "",
        }),
    },
    CommunicationAreaProhibited: {
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
    launchSite: {
        type: Object,
        default: () => ({
            lng: "",
            lat: "",
        }),
    },
});

const emit = defineEmits(["update:visible", "update:drawLaunchSiteForm"]);

const RectangleFormRef = ref<any>(null);
const roundFormRef = ref<any>(null);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 0, y: 0 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 520;

const panelStyle = computed(() => ({
    left: `${panelPos.value.x}px`,
    top: `${panelPos.value.y}px`,
    width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const rectangleCoordDisplay = computed(() => {
    const { initialPointLng, initialPointLat, destinationPointLng, destinationPointLat } = props.CommunicationArea;
    if (!initialPointLng || !initialPointLat || !destinationPointLng || !destinationPointLat) return "";
    return `${initialPointLng}, ${initialPointLat}  →  ${destinationPointLng}, ${destinationPointLat}`;
});

const roundCoordDisplay = computed(() => {
    const { centerPointLng, centerPointLat } = props.CommunicationArea;
    if (!centerPointLng || !centerPointLat) return "";
    return `${centerPointLng}, ${centerPointLat}`;
});

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
    const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
    const height = size?.height ?? 420;
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
    () => props.showCommunicationAreaDialog,
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

const onDrawAreaEnd = (payload: { type?: string }) => {
    if (payload?.type && payload.type !== "Rectangle" && payload.type !== "round") return;
    finishPickMode();
};

const handleConfirmCommunicationArea = async () => {
    if (props.CommunicationArea.activeName === "Rectangle") {
        await RectangleFormRef.value?.validate((valid) => {
            if (valid) {
                $bus.emit("setCommunicationArea", props.CommunicationArea);
                setVisible(false);
            } else {
                shakeInvalidFormFields(RectangleFormRef.value);
            }
        });
    } else if (props.CommunicationArea.activeName === "Round") {
        await roundFormRef.value?.validate((valid) => {
            if (valid) {
                $bus.emit("setCommunicationArea", props.CommunicationArea);
                setVisible(false);
            } else {
                shakeInvalidFormFields(roundFormRef.value);
            }
        });
    }
};

const drawGraph = (type: string) => {
    pendingPickRestore.value = true;
    setVisible(false);

    const onEsc = (e: KeyboardEvent) => {
        if (e.key !== "Escape") return;
        $bus.emit("cancelDrawPoint");
        finishPickMode();
    };
    pickEscHandler = onEsc;
    window.addEventListener("keydown", onEsc);

    $bus.emit("drawCommunicationArea", type);
};

const getDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
};

const readLngLat = (point: any): [number, number] | null => {
    if (!point) return null;
    if (Array.isArray(point) && Number.isFinite(Number(point[0])) && Number.isFinite(Number(point[1]))) {
        return [Number(point[0]), Number(point[1])];
    }
    const lng = point.lng ?? point.lon ?? point.x;
    const lat = point.lat ?? point.y;
    if (Number.isFinite(Number(lng)) && Number.isFinite(Number(lat))) {
        return [Number(lng), Number(lat)];
    }
    return null;
};

const updateCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
    if (!graphic) return;
    const json = graphic.toJSON?.() || {};
    const name = json.name || graphic.name;
    if (name === "Rectangle") {
        const start = readLngLat(json.positions?.[0]);
        const end = readLngLat(json.positions?.[1]);
        if (!start || !end) return;
        props.CommunicationArea.initialPointLng = start[0];
        props.CommunicationArea.initialPointLat = start[1];
        props.CommunicationArea.destinationPointLng = end[0];
        props.CommunicationArea.destinationPointLat = end[1];
        const launchLng = parseFloat(props.launchSite.lng);
        const launchLat = parseFloat(props.launchSite.lat);
        if (launchLng && launchLat) {
            const minLng = Math.min(start[0], end[0]);
            const maxLng = Math.max(start[0], end[0]);
            const minLat = Math.min(start[1], end[1]);
            const maxLat = Math.max(start[1], end[1]);
            if (launchLng < minLng || launchLng > maxLng || launchLat < minLat || launchLat > maxLat) {
                ElMessage.error({
                    message: "发射站点不在绘制区域内，请重新绘制",
                    duration: 0,
                    offset: 200,
                    showClose: true,
                });
                graphic.remove();
                return;
            }
        }
    } else if (name === "round" || name === "Round") {
        const center = readLngLat(json.position || json.center);
        const radiusM = json.style?.radius;
        if (!center || !radiusM) return;
        props.CommunicationArea.centerPointLng = center[0];
        props.CommunicationArea.centerPointLat = center[1];
        props.CommunicationArea.radius = radiusM / 1000;
        const launchLng = parseFloat(props.launchSite.lng);
        const launchLat = parseFloat(props.launchSite.lat);
        if (launchLng && launchLat) {
            const radius = radiusM / 1000;
            const distance = getDistance(launchLat, launchLng, center[1], center[0]);
            if (distance > radius) {
                ElMessage.error({
                    message: "发射站点不在绘制区域内，请重新绘制",
                    duration: 0,
                    offset: 200,
                    showClose: true,
                });
                graphic.remove();
                return;
            }
        }
    }
};

$bus.on("drawCommunicationAreaMsg", updateCommunicationAreaData);
$bus.on("drawCommunicationAreaEnd", onDrawAreaEnd);

const updateProhibitedCommunicationAreaData = (graphic: mars3d.graphic.BaseGraphic) => {
    if (graphic && graphic.toJSON().name === "prohibitedRectangle") {
        props.CommunicationAreaProhibited.initialPointLng = graphic.toJSON().positions[0][0];
        props.CommunicationAreaProhibited.initialPointLat = graphic.toJSON().positions[0][1];
        props.CommunicationAreaProhibited.destinationPointLng = graphic.toJSON().positions[1][0];
        props.CommunicationAreaProhibited.destinationPointLat = graphic.toJSON().positions[1][1];
    } else if (graphic && graphic.toJSON().name === "prohibitedround") {
        props.CommunicationAreaProhibited.centerPointLng = graphic.toJSON().position[0];
        props.CommunicationAreaProhibited.centerPointLat = graphic.toJSON().position[1];
        props.CommunicationAreaProhibited.radius = graphic.toJSON().style.radius / 1000;
    }
};

$bus.on("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);

watch(
    () => props.CommunicationArea.activeName,
    (newVal) => {
        $bus.emit("showCommunicationArea", newVal);
    }
);
watch(
    () => props.CommunicationAreaProhibited.activeProhibitedName,
    (newVal) => {
        $bus.emit("showProhibitedCommunicationArea", newVal);
    }
);

onBeforeUnmount(() => {
    stopDrag();
    cleanupPickMode();
    $bus.off("drawCommunicationAreaMsg", updateCommunicationAreaData);
    $bus.off("drawCommunicationAreaEnd", onDrawAreaEnd);
    $bus.off("drawProhibitedCommunicationAreaMsg", updateProhibitedCommunicationAreaData);
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
        overflow: hidden;
    }

    &__header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
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

    &__tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 16px;
    }

    &__tab {
        height: 34px;
        padding: 0 16px;
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

    &__card {
        width: 100%;
        min-width: 0;
        padding: 16px 14px 8px;
        border-radius: 10px;
        background: rgba(18, 24, 31, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    &__card-title {
        margin: 0 0 14px;
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
        margin-top: 18px;
        gap: 12px;
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

        svg {
            width: 14px;
            height: 14px;
        }
    }

    :deep(.el-form-item) {
        margin-bottom: 14px;
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

    :deep(.station-config__form .el-form-item.is-error .el-input__wrapper),
    :deep(.station-config__form .el-form-item.is-error .el-select__wrapper) {
        border-color: rgba(248, 113, 113, 0.7) !important;
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
