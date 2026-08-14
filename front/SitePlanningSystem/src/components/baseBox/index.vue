<template>
    <div class="baseBox">
        <div class="baseBox__title">
            <span v-if="title">{{ title }}</span>
            <slot v-else name="title"></slot>
        </div>
        <div class="baseBox__main">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang='ts'>

defineProps({
    title: {
        type: String,
        default: ''
    }
});

</script>

<style scoped lang="scss">
.baseBox {
    width: 100%;
    display: flex;
    flex-direction: column;
    // box-sizing: border-box;
    flex: 1;
    overflow: hidden;

    &__title {
        height: 44px;
        max-width: 400px;
        background: url("@/assets/images/components/panel_head.png") no-repeat;
        background-size: 100% 100%;
        line-height: 44px;
        font-size: 22px;
        padding-left: 33px;
        font-family: 'youshebiaotihei', sans-serif;

        span {
            font-size: 22px;
        }
    }

    &__main {
        height: 0;
        flex: 1;
        margin-top: 3px;
        overflow-y: scroll;
        padding: 12px;
        margin-bottom: 12px;
        background: rgba(7, 7, 8, 0.30);
        border: 1px solid #1a3642;
        display: flex;
        flex-direction: column;
        // box-sizing: border-box;
        // backdrop-filter: blur(3px);
    }
}
</style>