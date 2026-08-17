<template>
    <div id="mars3dContainer" class="mars3dContainer"></div>
    <div ref="hudRef" class="map-hud">
        <div id="map-toast-host" class="map-toast-host" aria-live="polite"></div>
        <div ref="statusRef" class="map-status" aria-hidden="true">
            <div class="map-status__scale">
                <span class="map-status__scale-label">{{ scaleLabel }}</span>
                <span class="map-status__scale-bar" :style="{ width: scaleBarWidth + 'px' }"></span>
            </div>
            <div class="map-status__divider"></div>
            <div class="map-status__coord">
                <span>经度 {{ lngText }}°</span>
                <span>纬度 {{ latText }}°</span>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { getCurrentInstance, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { map3dConfig } from "./config/config"
import * as mars3d from "mars3d"
import { main } from "./service/main"
import { setMapInstance } from "@/assets/util/index";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

import SingleLinkService from "../../../home/service/singlelink";
import SLPComputeService from "../../../home/service/SLPCompute";
import CommunicationAreaService from "../../../home/service/CommunicationArea";

const store = useStore();
const router = useRouter();
let mapMain: main | null = null;
const currentInstance = getCurrentInstance();
const $bus = currentInstance?.appContext.config.globalProperties.$bus;

const lngText = ref("--");
const latText = ref("--");
const scaleLabel = ref("--");
const scaleBarWidth = ref(72);
const hudRef = ref<HTMLElement | null>(null);
const statusRef = ref<HTMLElement | null>(null);
let statusObserver: ResizeObserver | null = null;

const syncHudSize = () => {
    const status = statusRef.value;
    const hud = hudRef.value;
    if (!status || !hud) return;
    const rect = status.getBoundingClientRect();
    if (rect.width < 8 || rect.height < 8) return;
    hud.style.setProperty("--map-status-width", `${Math.round(rect.width)}px`);
    hud.style.setProperty("--map-status-height", `${Math.round(rect.height)}px`);
};

watch(
    () => router.currentRoute.value.path,
    () => {
        if (mapMain) {
            mapMain.setPageRootRoute(router.currentRoute.value.matched[0].path);
        }
    },
    { immediate: true, deep: true }
);

let map: mars3d.Map;
let distanceLegend: any = null;

const formatScaleLabel = (meters: number) => {
    if (!Number.isFinite(meters) || meters <= 0) return "--";
    if (meters >= 1000) {
        const km = meters / 1000;
        const text = Number.isInteger(km) ? String(km) : String(Number(km.toFixed(1)));
        return `${text} km`;
    }
    return `${Math.round(meters)} m`;
};

const syncScaleFromLegend = () => {
    const root = document.querySelector(".mars3d-distance-legend") as HTMLElement | null;
    const labelEl = root?.querySelector(".legend-label");
    const barEl = root?.querySelector(".legend-scale-bar") as HTMLElement | null;
    const nativeLabel = labelEl?.textContent?.trim();
    if (nativeLabel) scaleLabel.value = nativeLabel;
    else if (distanceLegend?.distance) scaleLabel.value = formatScaleLabel(Number(distanceLegend.distance));

    const nativeWidth = barEl?.offsetWidth || 0;
    if (nativeWidth > 8) scaleBarWidth.value = nativeWidth;
};

const showMouseCoordinates = (event: any) => {
    const windowPosition = event.endPosition;
    const cartesian3 = map.getCurrentMousePosition(windowPosition);
    if (!cartesian3) return;
    const position = mars3d.Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian3);
    if (!position) return;
    lngText.value = mars3d.Cesium.Math.toDegrees(position.longitude).toFixed(6);
    latText.value = mars3d.Cesium.Math.toDegrees(position.latitude).toFixed(6);
};

onMounted(() => {
    map = new mars3d.Map("mars3dContainer", map3dConfig);
    mapMain = new main(map, $bus, store);

    new SingleLinkService(map, $bus);
    new SLPComputeService(map, $bus);
    new CommunicationAreaService(map, $bus);
    setMapInstance(map);

    map.on(mars3d.EventType.mouseMove, showMouseCoordinates);

    distanceLegend = (map as any).control?.distanceLegend || map.getControl("distanceLegend");
    if (distanceLegend?.on) {
        distanceLegend.on(mars3d.EventType.change, syncScaleFromLegend);
    }
    syncScaleFromLegend();
    window.setTimeout(syncScaleFromLegend, 300);

    nextTick(() => {
        syncHudSize();
        if (statusRef.value && typeof ResizeObserver !== "undefined") {
            statusObserver = new ResizeObserver(syncHudSize);
            statusObserver.observe(statusRef.value);
        }
    });
});

onBeforeUnmount(() => {
    if (map) map.off(mars3d.EventType.mouseMove, showMouseCoordinates);
    if (distanceLegend?.off) distanceLegend.off(mars3d.EventType.change, syncScaleFromLegend);
    statusObserver?.disconnect();
    statusObserver = null;
});
</script>

<style lang="scss">
.mars3dContainer {
    position: fixed;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
}

.cesium-viewer-toolbar {
    display: none !important;
}

.mars3d-distance-legend {
    visibility: hidden !important;
    pointer-events: none !important;
    left: -9999px !important;
}

.map-hud {
    --map-status-width: 240px;
    --map-status-height: 48px;
    position: fixed;
    right: 16px;
    bottom: 16px;
    z-index: 2400;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0;
    max-width: calc(100vw - 32px);
    pointer-events: none;
    box-sizing: border-box;
}

.map-toast-host {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    width: var(--map-status-width);
    height: calc(var(--map-status-height) * 3);
    margin-bottom: 10px;
    box-sizing: border-box;
    overflow: hidden;
}

.map-toast-host:empty {
    height: 0;
    margin-bottom: 0;
    overflow: hidden;
}

.map-status {
    pointer-events: none;
    display: flex;
    align-items: center;
    gap: 14px;
    min-height: 48px;
    padding: 8px 14px;
    border-radius: 12px;
    background: rgba(24, 26, 24, 0.82);
    border: 1px solid rgba(180, 200, 220, 0.18);
    box-shadow:
        0 18px 48px rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(22px) saturate(1.15);
    -webkit-backdrop-filter: blur(22px) saturate(1.15);
    color: rgba(235, 240, 245, 0.92);
    font-family: "IBM Plex Mono", "Noto Sans SC", monospace;
    box-sizing: border-box;
}

.map-status__scale {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-width: 72px;
}

.map-status__scale-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: rgba(235, 240, 245, 0.82);
    line-height: 1;
    white-space: nowrap;
}

.map-status__scale-bar {
    display: block;
    height: 8px;
    min-width: 36px;
    max-width: 120px;
    border-left: 1px solid rgba(235, 240, 245, 0.92);
    border-right: 1px solid rgba(235, 240, 245, 0.92);
    border-bottom: 1px solid rgba(235, 240, 245, 0.92);
    box-sizing: border-box;
}

.map-status__divider {
    width: 1px;
    height: 28px;
    background: rgba(180, 200, 220, 0.18);
    flex-shrink: 0;
}

.map-status__coord {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 11px;
    line-height: 1.2;
    color: rgba(235, 240, 245, 0.88);
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
</style>
