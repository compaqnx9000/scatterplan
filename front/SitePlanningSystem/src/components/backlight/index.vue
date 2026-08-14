<template>
  <div class="container" :style="isBackground()" v-show="store.getters.getIsPanelShow">
    <div class="container_left">
      <div class="container_left_box" v-if="$slots.left">
        <slot name="left"></slot>
      </div>
      <div class="container_left_resources">
        <slot name="center"></slot>
      </div>
    </div>
    <div class="container_right">
      <div class="container_right_box" v-if="$slots.right">
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import containerBgc from "@/assets/images/components/container_bgc.png";
import mainBackground from "@/assets/images/components/main_background.png";
import noBackground from "@/assets/images/components/no_background.png";
import { useSlots } from "vue";
import { useStore } from 'vuex';
const store = useStore();
const slots = useSlots();
const isBackground = () => {
  if (slots.left && slots.right) {
    return `background:url(${mainBackground}) no-repeat;`;
  } else if (!slots.left && !slots.right) {
    return `background:url(${noBackground}) no-repeat;`;
  } else if (slots.left && !slots.right) {
    return `background:url(${containerBgc}) no-repeat;`;
  }
};
</script>

<style lang="scss" scoped>
.container {
  width: 100%;
  height: 100%;
  display: flex;
  pointer-events: none;
  background-size: cover;

  &_left {
    width: 50%;
    position: relative;
    /* background: url("@/assets/images/components/left_bgc.png") no-repeat; */
    display: flex;

    &_box {
      width: 374px;
      height: 100%;
      padding-left: 24px;
      padding-top: 24px;
      box-sizing: border-box;
      backdrop-filter: blur(3px);
    }

    &_resources {
      width: 200px;
      padding: 10px;
    }
  }

  &_right {
    position: relative;
    width: 50%;
    /* background: url("@/assets/images/components/right_bgc.png") no-repeat; */

    &_box {
      position: absolute;
      right: 0;
      width: 374px;
      height: 100%;
      backdrop-filter: blur(3px);
      /* background: linear-gradient(to right, #051014, #111d1e); */
      padding-right: 24px;
      padding-top: 24px;
      box-sizing: border-box;
    }
  }
}
</style>
