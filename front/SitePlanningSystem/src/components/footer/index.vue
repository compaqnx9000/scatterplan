<template>
    <div class="footer">
        <div class="footer__title">
            <slot name="head"></slot>
        </div>
        <div class="footer__main">
            <slot name="main"></slot>
        </div>
    </div>
</template>

<script setup lang='ts'>

</script>

<style lang="scss" scoped>
.footer {
    width: 100%;
    box-sizing: border-box;
    padding: 0 24px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(3px);


    &__title {
        background: url("@/assets/images/components/footer_bgc.png") no-repeat;
        background-size: cover;
        height: 34px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        padding: 0 30px;
        box-sizing: border-box;
    }

    &__main {
        flex: 1;
        border: 1px solid #1a3642;
        padding: 2px 20px;
    }
}
</style>