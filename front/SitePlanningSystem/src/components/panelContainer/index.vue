<template>
    <Teleport defer to="#layout__dom" :disabled="isDisabled">
        <div ref="panel" :class="isDisabled ? 'panel' : 'panel panelMax'" :style="isDisabled ? '' : scaleStyle">
            <div class="panel__title">
                <span v-if="title">{{ title }}</span>
                <slot v-else name="title"></slot>
                <slot name="btn">
                </slot>
                <div class="panel__title__FullScreen" v-if="showScreen" @click="isDisabled = !isDisabled">
                    <el-icon>
                        <FullScreen v-if="isDisabled" />
                        <Close v-else />
                    </el-icon>
                </div>
            </div>
            <div class="panel__main" :style="bg ? 'background: rgba(7, 7, 8, 0.30);backdrop-filter: blur(3px);' : ''">
                <slot></slot>
            </div>
        </div>
    </Teleport>
</template>

<script setup lang='ts'>
// @ts-nocheck
defineProps({
    title: {
        type: String,
        default: ''
    },
    bg: {
        type: Boolean,
        default: true
    },
    // 是否展示放大框按钮
    showScreen: {
        type: Boolean,
        default: true,
    }
});

// let teleportTo = ref('#layout__dom')
let isDisabled = ref(true)

let panel = ref()
let scaleStyle = ref()

onMounted(() => {
    nextTick(() => {
        let h = panel.value.offsetHeight > 500 ? 500 : panel.value.offsetHeight
        const w = panel.value.offsetWidth;

        scaleStyle.value = `transform-origin:50% 50%;transform: scale(1.8);width:${w}px;height:${h}px;margin-left:${-w / 2}px;margin-top:${-h / 2}px;`;
    })
})

</script>

<style scoped lang="scss">
.panelMax {
    position: fixed;
    background: #000000;
    // padding: 200px 400px;
    pointer-events: auto;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    // height: 0;
    z-index: 999;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 500px #000000;
}

.panel {
    // width: 100%;
    // height: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;

    &__title {
        height: 44px;
        background: no-repeat url("@/assets/images/components/panel_head.png"), linear-gradient(90deg, rgba(12, 25, 31, 0.80) 0%, rgba(11, 29, 37, 0.80) 100%);
        background-size: auto 100%;
        line-height: 44px;
        font-size: 22px;
        padding-left: 33px;
        display: flex;
        pointer-events: auto;

        span {
            font-family: 'youshebiaotihei', sans-serif;
            font-size: 22px;
        }

        &__FullScreen {
            margin-left: auto;
            margin-right: 10px;
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