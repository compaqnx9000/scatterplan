<template>
  <div class="tool">
    <div
      class="tool-item"
      v-for="(item, index) in toolList"
      :key="item.label"
      @click="item?.onClick"
    >
      <img :src="item.img" alt="" style="cursor: pointer" />
      <div style="cursor: pointer">{{ item.label }}</div>
      <div class="line" v-if="index != toolList.length - 1"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import icon01 from "@/assets/images/components/icon01.png";
import icon02 from "@/assets/images/components/icon02.png";
import icon03 from "@/assets/images/components/icon03.png";
import icon04 from "@/assets/images/components/icon04.png";
import icon05 from "@/assets/images/components/icon05.png";
import { onMounted, onUnmounted } from "vue";
import { getMapInstance } from "@/assets/util/index";
import { Tool } from "./service";
let MapContainer: Tool;
const toolList = ref([
  {
    label: "面积",
    img: icon01,
    onClick: () => {
      MapContainer?.area();
    },
  },
  {
    label: "距离",
    img: icon02,
    onClick: () => {
      MapContainer?.distance();
    },
  },
  {
    label: "多边形",
    img: icon03,
    onClick: () => {
      MapContainer?.startDrawGraphic();
    },
  },
  {
    label: "画线",
    img: icon04,
    onClick: () => {
      MapContainer?.startDrawLine();
    },
  },
  {
    label: "清除",
    img: icon05,
    onClick: () => {
      MapContainer?.clear();
    },
  },
]);

onMounted(async () => {
  await nextTick(() => {
    MapContainer = new Tool(getMapInstance());
  });
});

onUnmounted(() => {
  MapContainer.destroy()
})
</script>

<style scoped lang="scss">
.tool {
  background: rgba(11, 52, 69, 0.8);
  display: flex;
  padding: 10px;
  cursor: pointer;
  height: 30px;
  white-space: nowrap;

  .tool-item {
    display: flex;
    align-items: center;
    cursor: pointer;
    .line {
      border: 1px dashed #fff; /* 1px宽的黑色虚线 */
      height: 100%;
      margin: 0 15px;
    }
    img {
      width: 32px;
      height: 32px;
      cursor: pointer;
    }
  }
}
</style>
