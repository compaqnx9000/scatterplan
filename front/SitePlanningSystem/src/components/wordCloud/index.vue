<template>
    <div class="wordCloud__layout" ref="wordCloudLayout">
    </div>
</template>

<script setup lang='ts'>
// @ts-ignore
import SimpleWordCloud from "./index"

let props = defineProps({
    dataList: Array
})

let wordCloud: any
watch(() => props.dataList, () => {
    if (wordCloud) {
        wordCloud.render(props.dataList, () => { })
        wordCloud.resize()
    }
}, {
    deep: true,
})

let wordCloudLayout = ref()


onMounted(() => {
    window.addEventListener("resize", function () {
        const width = window.innerWidth;
        // 1960px对应14px，计算比例​
        const minFontSize = (width / 1960) * 20;
        const maxFontSize = (width / 1960) * 30;
        // console.log(minFontSize, maxFontSize);
        // console.log(wordCloudLayout.value.offsetWidth);

        wordCloud.updateOption({
            minFontSize: minFontSize,
            maxFontSize: maxFontSize,
            fontFamily: '微软雅黑, Microsoft YaHei',
            fontWeight: 400,
            fontStyle: '',
            fontSizeScale: 0.3,
            rotateType: 'none',
            space: 1.5,//词间距
            colorList: ['#ffffff'],
            transition: 'all 0.5s ease',
            // smallWeightInCenter: true
        })
        wordCloud.render(props.dataList, () => { })
        wordCloud.resize()
    });

    nextTick(() => {
        // console.log(wordCloudLayout.value.offsetWidth);
        
        wordCloud = new SimpleWordCloud({
            el: wordCloudLayout.value
        })

        
        const width = window.innerWidth;
        // 1960px对应14px，计算比例​
        const minFontSize = (width / 1960) * 20;
        const maxFontSize = (width / 1960) * 30;
        // console.log(minFontSize, maxFontSize);

        wordCloud.updateOption({
            minFontSize: minFontSize,
            maxFontSize: maxFontSize,
            fontFamily: '微软雅黑, Microsoft YaHei',
            fontWeight: 400,
            fontStyle: '',
            fontSizeScale: 0.3,
            rotateType: 'none',
            space: 1.5,//词间距
            colorList: ['#ffffff'],
            transition: 'all 0.5s ease',
            // smallWeightInCenter: true
        })
        // console.log(props.dataList);

        let data = props.dataList ? props.dataList : [
            ['暂无数据', 2], ['暂无数据', 23]
        ]

        wordCloud.render(data, () => { })
    })
})



</script>

<style scoped lang="scss">
.wordCloud__layout {
    width: 100%;
    height: 100%;
    // border: 1px solid red;
}
</style>