<template>
  <div
    class="operatingButton"
    :style="[{ right: right + 'px' }, { bottom: bottom + 'px' }]"
  >
    <div class="operatingButton_item">
      <img src="@/assets/images/components/chat.svg" alt="" srcset="" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import * as mars3d from "mars3d";
import { getMapInstance } from "@/assets/util/index";
import { UseoperatingButton } from "@/view/layout/components/map/service/UseoperatingButton";
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

let viewFlag = ref(true);
const handleView = () => {
  viewFlag.value = !viewFlag.value;
  $bus.emit("isShowQXSY", viewFlag.value);
  if (viewFlag.value) {
    operatingButton.selectMap("天地图影像");
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
  &_item {
    padding: 5px;
    cursor: pointer;
    margin-bottom: 5px;
    text-align: center;
    img {
      object-fit: cover;
    }
  }
}
</style>
