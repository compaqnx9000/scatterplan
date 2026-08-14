<template>
  <div class="panel">
    <div class="panel__title">
      <span @click="menuList = !menuList">{{ titleValue }}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="36"
        height="24"
        viewBox="0 0 36 24"
        fill="none"
      >
        <g filter="url(#filter0_dd_823_7696)">
          <path
            d="M16.6 14.55C16.2444 14.8167 15.7556 14.8167 15.4 14.55L6.4 7.8C5.63119 7.22339 6.03899 6 7 6L25 6C25.961 6 26.3688 7.22339 25.6 7.8L16.6 14.55Z"
            fill="url(#paint0_linear_823_7696)"
          />
        </g>
        <defs>
          <filter
            id="filter0_dd_823_7696"
            x="-0.00195312"
            y="0"
            width="35.5039"
            height="23.25"
            filterUnits="userSpaceOnUse"
            color-interpolation-filters="sRGB"
          >
            <feFlood flood-opacity="0" result="BackgroundImageFix" />
            <feColorMatrix
              in="SourceAlpha"
              type="matrix"
              values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
              result="hardAlpha"
            />
            <feOffset dx="5" dy="4" />
            <feGaussianBlur stdDeviation="2.25" />
            <feComposite in2="hardAlpha" operator="out" />
            <feColorMatrix
              type="matrix"
              values="0 0 0 0 0.709804 0 0 0 0 0.956863 0 0 0 0 0.992157 0 0 0 0.14 0"
            />
            <feBlend
              mode="normal"
              in2="BackgroundImageFix"
              result="effect1_dropShadow_823_7696"
            />
            <feColorMatrix
              in="SourceAlpha"
              type="matrix"
              values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
              result="hardAlpha"
            />
            <feOffset />
            <feGaussianBlur stdDeviation="3" />
            <feComposite in2="hardAlpha" operator="out" />
            <feColorMatrix
              type="matrix"
              values="0 0 0 0 0.333333 0 0 0 0 0.678431 0 0 0 0 1 0 0 0 0.15 0"
            />
            <feBlend
              mode="normal"
              in2="effect1_dropShadow_823_7696"
              result="effect2_dropShadow_823_7696"
            />
            <feBlend
              mode="normal"
              in="SourceGraphic"
              in2="effect2_dropShadow_823_7696"
              result="shape"
            />
          </filter>
          <linearGradient
            id="paint0_linear_823_7696"
            x1="17.875"
            y1="13"
            x2="14.6875"
            y2="3.4375"
            gradientUnits="userSpaceOnUse"
          >
            <stop stop-color="#95F1FF" />
            <stop offset="1" stop-color="white" />
          </linearGradient>
        </defs>
      </svg>
      <div class="panel__title__list" v-show="menuList">
        <div
          class="panel__title__list__item"
          v-for="item in list"
          :key="item.label"
          @click="handleItem(item.label)"
        >
          {{ item.label }}
        </div>
      </div>
    </div>
    <div
      class="panel__main"
      :style="
        bg ? 'background: rgba(7, 7, 8, 0.30);backdrop-filter: blur(3px);' : ''
      "
    >
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType } from "vue";
interface ListItem {
  label: string;
}
const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  bg: {
    type: Boolean,
    default: true,
  },
  list: {
    type: Array as PropType<ListItem[]>,
    default: () => [],
  },
});
let emit = defineEmits(["syncMenuOptions"]);
const menuList = ref(false);
const handleItem = (val: string) => {
  emit("syncMenuOptions", val);
  titleValue.value = val;
  menuList.value = false;
};

const titleValue = ref("");
const init = () => {
  nextTick(() => {
    titleValue.value = props.list[0]?.label;
  });
};
init();
</script>

<style scoped lang="scss">
.panel {
  // width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;

  &__title {
    height: 44px;
    background: no-repeat url("@/assets/images/components/panel_head.png"),
      linear-gradient(
        90deg,
        rgba(12, 25, 31, 0.8) 0%,
        rgba(11, 29, 37, 0.8) 100%
      );
    background-size: auto 100%;
    line-height: 44px;
    font-size: 22px;
    padding-left: 33px;
    display: flex;
    align-items: center;
    position: relative;
    * {
      cursor: pointer;
    }

    span {
      font-family: "youshebiaotihei", sans-serif;
      font-size: 22px;
    }
    &__list {
      position: absolute;
      left: 0;
      top: 46px;
      min-width: 280px;
      z-index: 99999;
      backdrop-filter: blur(2.5px);
      background: linear-gradient(
        180deg,
        rgba(19, 54, 64, 0.8) 0%,
        rgba(6, 27, 35, 0.8) 100%
      );
      border: 1px solid rgba(0, 221, 255, 0.6);
      &__item {
        cursor: pointer;
        padding-left: 10px;
      }
      &__item:hover {
        cursor: pointer;
        padding-left: 10px;
        background: #f0f0f030;
      }
    }
  }

  &__main {
    flex: 1;
    margin-top: 3px;
    padding: 12px;
    border: 1px solid #1a3642;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    height: 0;
    // justify-content: center;
    // align-items: center;
    // background: rgba(7, 7, 8, 0.30);
    // backdrop-filter: blur(3px);
  }
}
</style>
