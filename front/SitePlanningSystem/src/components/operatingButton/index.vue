<template>
  <div
    class="operatingButton"
    :style="[{ right: right + 'px' }, { bottom: bottom + 'px' }]"
  >
    <div class="operatingButton_item" @click="handleView">
      {{ viewFlag ? "3D" : "2D" }}
    </div>
    <div class="operatingButton_item" @click="handleQXSY" :style="{opacity:store.getters.getIsShowMoudle?'1':'0.7'}">倾</div>
    <div class="operatingButton_item" @click="handleCenter">
      <img src="@/assets/images/components/center.png" alt="" srcset="" />
    </div>
    <div class="operatingButton_item" @click="handleCameraZoomIn(true)">
      <img src="@/assets/images/components/add.png" alt="" srcset="" />
    </div>
    <div class="operatingButton_item" @click="handleCameraZoomIn(false)">
      <el-icon><SemiSelect /></el-icon>
    </div>
    <div class="operatingButton_item" @click="handleISPanelShow" :style="{opacity:store.getters.getIsPanelShow?'1':'0.7'}">
      <el-icon><Menu /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import * as mars3d from "mars3d";
import { getMapInstance } from "@/assets/util/index";
import { UseoperatingButton } from "@/view/layout/components/map/service/UseoperatingButton";
import { useStore } from 'vuex';
defineProps({
  right: {
    type: Number,
    default: 380,
  },
  bottom: {
    type: Number,
    default: 200,
  },
});
let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

let MapContainer: mars3d.Map;

let operatingButton: UseoperatingButton;

const initMap = () => {
  operatingButton = new UseoperatingButton(MapContainer);
};

const handleCameraZoomIn = (e: boolean) => {
  operatingButton.handleCameraZoomIn(e);
};

const handleCenter = () => {
  operatingButton.flyToCenter({
    lng: 115.871897,
    lat: 28.693529,
    alt: 265381,
  });
};

const handleQXSY = () => {
  $bus.emit("manageQXSY");
};
const store = useStore();
const handleISPanelShow = () => {
  store.commit('SET_PANELSHOW', !store.getters.getIsPanelShow);
};

let viewFlag = ref(true);
const handleView = () => {
  viewFlag.value = !viewFlag.value;
  $bus.emit("isShowQXSY", viewFlag.value);
  $bus.emit("isShowHgtQXSY", viewFlag.value);
  if (viewFlag.value) {
    operatingButton.selectMap("腾讯影像");
  } else {
    operatingButton.selectMap("高德电子");
  }
};

onMounted(async () => {
  await nextTick(() => {
    MapContainer = getMapInstance();
    initMap();
  });
});
</script>

<style scoped lang="scss">
.operatingButton {
  position: absolute;
  bottom: 0px;
  right: 0;
  pointer-events: all;
  z-index: 99;
  * {
    cursor: pointer;
  }
  &_item {
    border: 1px solid #1c6f8d;
    box-shadow: 0px 0px 2px 0px #468fce;
    background: rgba(28, 111, 141, 0.5);
    padding: 5px;
    cursor: pointer;
    margin-bottom: 5px;
    text-align: center;
    img {
      width: 16px;
      height: 16px;
      object-fit: cover;
    }
  }
}
</style>
