<template>
    <div v-if="!$slots.planBtn" class="suggestion__btn" @click="showBox = !showBox">
        <svg xmlns="http://www.w3.org/2000/svg" width="8" height="8" viewBox="0 0 8 8" fill="none">
            <rect x="0.5" y="-0.5" width="7" height="7" transform="matrix(1 0 0 -1 0 7)" stroke="#00B2FF"
                stroke-opacity="0.2" />
            <rect x="2.72217" y="2.72266" width="2.55556" height="2.55556" fill="#00B2FF" stroke="#00B2FF" />
        </svg>
        建议反馈
    </div>
    <div @click="showBox = !showBox">
        <slot name="planBtn"></slot>
    </div>

    <!-- 因为最外层使用了transform布局，会导致position:fixed定位不到最外层，会变为父元素，所以这里使用dom发送，将内容发送到最外层 layout__dom 元素下展示 -->
    <Teleport defer to="#layout__dom">
        <div class='suggestion__layout' v-if="showBox">
            <div class="suggestion__layout__header">
                <div class="suggestion__layout__header__title">
                    反馈意见
                </div>
                <div class="suggestion__layout__header__close" @click="showBox = !showBox">
                    <el-icon>
                        <CloseBold />
                    </el-icon>
                </div>
            </div>
            <div class="suggestion__layout__body">
                <el-form :model="suggestionParams" ref="queryForm" size="small" :inline="true" label-width="60px">
                    <el-form-item label="标题" prop="landType" style="margin-top: 20px;">
                        <el-input v-model="suggestionParams.title"></el-input>
                    </el-form-item>
                    <el-form-item label="描述" prop="landType">
                        <el-input class="suggestion__textarea" type="textarea"
                            v-model="suggestionParams.desc"></el-input>
                    </el-form-item>
                    <el-form-item label=" ">
                        <div style="display: flex;">
                            <div class="suggestion__layout__btn" size="default" @click="close()">
                                <div>
                                    取消
                                </div>
                            </div>
                            <div class="suggestion__layout__selBtn" size="default" @click="getListData()"
                                style="margin-left: 10px;">
                                <div>
                                    确定
                                </div>
                            </div>
                        </div>
                    </el-form-item>
                </el-form>
            </div>
        </div>
    </Teleport>
</template>

<script setup lang='ts'>
// @ts-nocheck
// 这个页面不能校验，现在好像打包时会把 Teleport 错误判断为jsx的报错，无法解决
import { ElMessage } from 'element-plus'
import { feedback } from '@/request/publicApi'

let showBox = ref(false)

let suggestionParams = ref({
    title: "",
    desc: ""
})

function close() {
    showBox.value = !showBox.value
}

async function getListData() {
    if (!suggestionParams.value.title) {
        ElMessage.error('请输入意见标题')
        return
    }
    if (!suggestionParams.value.desc) {
        ElMessage.error('请输入意见内容')
        return
    }
    try {
        let res = await feedback(suggestionParams.value)
        // console.log(res);
        ElMessage.success('意见已反馈，感谢您的支持')
        close()
    } catch (error) {
        
    }

}

</script>

<style lang='scss'>
.suggestion__btn {
    display: flex;
    height: 28px;
    padding: 0px 18px;
    align-items: center;
    border: 0.5px solid rgba(0, 178, 255, 0.50);
    background: linear-gradient(90deg, rgba(0, 134, 192, 0.30) 0%, rgba(0, 221, 255, 0.30) 100%);

    svg {
        margin-right: 10px;
    }
}

.suggestion__textarea {
    width: 200px;
    height: 230px;
    border-radius: 4px;
    border: 1px solid #007384;
    background: rgba(0, 221, 255, 0.20);

    textarea {
        height: 100%;
    }
}

.suggestion__layout {
    pointer-events: auto;
    position: fixed;
    width: 324px;
    left: 0;
    right: 0;
    top: 300px;
    margin: 0 auto;
    z-index: 9999;
    height: 422px;
    background: url('@/assets/images/attractInvestment/mapRegionAddressBg.png') no-repeat;
    background-size: 100% 100%;
    backdrop-filter: blur(2px);
    display: flex;
    flex-direction: column;

    &__header {
        display: flex;
        align-items: center;
        line-height: 38px;
        padding: 0 10px;
        border: 1px solid rgba(0, 221, 255, 0.10);
        background: linear-gradient(270deg, rgba(0, 221, 255, 0.00) 0%, rgba(0, 221, 255, 0.65) 100%);
        box-shadow: 0px 5px 5px 0px rgba(0, 42, 48, 0.30);

        &__title {
            flex: 1;
        }

        &__close {
            width: 20px;
            height: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(0, 0, 0, 0.30);
        }
    }

    &__body {
        flex: 1;
        margin: 0 16px 16px 16px;
        display: flex;
        flex-direction: column;

        &__pdf {
            flex: 1;

            iframe {
                width: 100%;
                height: 100%;
            }
        }
    }

    &__btn {
        width: 100px;
        height: 30px;
        transform: skewX(-30deg);
        border-radius: 0;
        text-align: center;
        line-height: 30px;
        border: 2px solid #1A9AD9;

        div {
            transform: skewX(30deg);
        }
    }

    &__selBtn {
        width: 100px;
        height: 30px;
        transform: skewX(-30deg);
        border-radius: 0;
        text-align: center;
        line-height: 30px;
        border: 2px solid #1A9AD9;

        background: linear-gradient(180deg, #0087FF40 0%, #0087FF85 100%);

        div {
            transform: skewX(30deg);
        }

    }
}
</style>