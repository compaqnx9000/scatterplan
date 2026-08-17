<template>
    <div class='layout'>
        <div class="layout__dom" :class="{ 'is-pick-locked': mapPickLocked }" :style="scaleStyle">
            <appHeader v-show="isLoggedIn"></appHeader>
            <div class="layout__body" id="layout__dom">
                <router-view v-slot="{ Component }">
                    <transition name="fade-transform" mode="out-in">
                        <keep-alive :include="isCached">
                            <div style="display: flex;flex: 1;flex-direction: column;height: 0;">
                                <component :is="Component" />
                            </div>
                        </keep-alive>
                    </transition>
                </router-view>
            </div>
            <mapToolbar v-show="isLoggedIn" />
        </div>
        <wcMap></wcMap>
        <SitePlanningResults v-if="isLoggedIn" v-model:visible="showSitePlanningResults" />
        <LoginModal :visible="!isLoggedIn" />
    </div>
</template>

<script lang="ts" setup>
// @ts-nocheck
import { computed, getCurrentInstance, onBeforeUnmount, ref } from "vue";
import wcMap from "./components/map/index.vue"
import appHeader from './components/appHeader.vue'
import mapToolbar from "@/components/mapToolbar/index.vue"
import LoginModal from "@/view/login/LoginModal.vue"
import SitePlanningResults from "@/view/sitePlanning/index.vue"
import store from "@/store/index";

import { useRoute } from 'vue-router';
let currentInstance = getCurrentInstance()
let $bus = currentInstance?.appContext.config.globalProperties.$bus
let isCached: Array<string> = []//缓存组件列表
let showChat = ref(false);
const showSitePlanningResults = ref(false);
const mapPickLocked = ref(false);

let scaleStyle = ref();

const isLoggedIn = computed(() => {
  return !!(store.state.token || store.getters.getToken);
});

// keep vuex token in sync with localStorage on first paint
if (!store.state.token && localStorage.getItem("userToken")) {
  store.commit("setToken", localStorage.getItem("userToken"));
}

function chatClick() {
  showChat.value = true;
}
function closeChat() {
  showChat.value = false;
}

$bus.on('chatContainerPanel',(e:boolean) => {
    showChat.value = e
})

const onMapPickMode = (active: boolean) => {
  mapPickLocked.value = !!active;
};
$bus.on("mapPickMode", onMapPickMode);

const onOpenSitePlanningResults = () => {
  showSitePlanningResults.value = true;
};
$bus.on("openSitePlanningResults", onOpenSitePlanningResults);

onBeforeUnmount(() => {
  $bus.off("mapPickMode", onMapPickMode);
  $bus.off("openSitePlanningResults", onOpenSitePlanningResults);
});
/**
 * 一般情况下下面的布局方式都是单独使用的
 */
// 宽高等比缩放布局
function adaptation() {
    const w = document.documentElement.clientWidth;
    const h = document.documentElement.clientHeight;
    const nw = 1920;
    const nh = 1080;
    let scale = 1;
    scale = h / nh;
    if (w / h > nw / nh) {
    } else {
        scale = w / nw;
    }
    const left = (w - nw * scale) / 2;
    const top = (h - nh * scale) / 2;
    console.log('adaptation', w, h, nw, nh, scale, left, top);
    // scaleStyle.value = `transform-origin:left top;transform: scale(${scale});width:${nw}px;height:${nh}px;margin-left:${left}px;margin-top:${top}px;`;
    
}


// 定义需要添加样式的路由名称
const route = useRoute();
// 定义动态样式变量





adaptation();

window.addEventListener("load", () => {
    adaptation();
});
window.addEventListener("resize", () => {
    adaptation();
});
</script>
<style lang='scss'>
.layout {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: 0;
    color: #fff;
    &__dom {
        position: relative;
        z-index: 5;
        display: flex;
        flex-direction: column;
        pointer-events: none;
    height: 100vh;

        /* 选点中：禁用所有 UI 交互，事件穿透到下方地球 */
        &.is-pick-locked {
            .app-header,
            .map-toolbar,
            .menu_btns,
            .fixed-color-bar {
                opacity: 0.55;
            }

            * {
                pointer-events: none !important;
            }
        }
    }

    &__body {
        flex: 1;
        pointer-events: none;
        display: flex;
        height: 0;
        flex-direction: column;
        // background: radial-gradient(circle, rgba(0, 0, 0, 0) 60%, rgba(0, 0, 0, 1) 100%);
    }

  .chatContainer{
    position: absolute;
    z-index: 99999;
    right: 0px;
    bottom: 150px;
    pointer-events: auto;
    // 强制创建新的合层，防止缩放后子元素的毛玻璃效果失效
    will-change: transform;
  }
}

</style>
