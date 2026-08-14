<template>
  <div class="subPanelTitle">{{ title }}</div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: "",
  },
});
</script>

<style lang="scss" scoped>
.subPanelTitle {
  width: 375px;
  height: 40px;
  background-image: url("@/assets/images/components/sub_panel_title.png");
  background-size: cover;
  background-repeat: no-repeat;
  font-size: 16px;
  color: #fff;
  line-height: 40px;
  padding-left: 40px;
  box-sizing: border-box;
}
</style>
