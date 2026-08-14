<template>
    <div class="echarts">
        <div class="echarts__label">{{ title }}</div>
        <div class="echarts__value" ref="chartRef"></div>
    </div>
</template>

<script setup lang='ts'>
import { onMounted, ref, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
    title: {
        type: String,
        default: ''
    },
    colors: {
        type: Array,
        default: () => {
            return ['rgba(5, 138, 161, 0.5)', 'rgba(24, 255, 213, 0.1)']

        }
    },
    lineColor: {
        type: String,
        default: 'rgba(1, 226, 235)'
    },
    showX: {
        type: Boolean,
        default: false
    },
    unit:{
        type: String,
        default: '亿元'
    }
});

const chartRef = ref(null);

let myChart: any;
let option: any = null
const initEcharts = () => {
    myChart = echarts.init(chartRef.value);
    option = {
        title: {
            show: false
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            },
            formatter: function(params: any) {
                let result = `<div style="color:white;">${params[0].name}</div>`;
                params.forEach((param: any) => {
                    result += `<div">● ${param.seriesName}: ${param.value}${props.unit}</div>`;
                });
                // console.log(params);
                
                return result;
            }
        },
        toolbox: {
            show: false
        },
        grid: {
            left: 0,
            right: 0,
            top: 0,
            bottom: props.showX ? 20 : 0
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            color: "#fff",
            axisLabel: {
                show: props.showX,
                color: 'white',
                //@ts-ignore
                formatter: function (value, index) {
                    const data = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];
                    if (index === 0) {
                        return '{leftText|' + value.padStart(value.length + 8) + '}';
                    } else if (index === data.length - 1) {
                        return '{rightText|' + value.padEnd(value.length + 12) + '}';
                    }
                    return value;
                },
                rich: {
                    leftText: {
                        align: 'left'
                    },
                    rightText: {
                        align: 'right'
                    }
                }
            },
            data: ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
        },
        yAxis: {
            show: false,
            min: function (value:any) {
                return value.min;
            },
            max: function (value:any) {
                return value.max;
            }
        },
        series: [
            {
                name: '数据',
                type: 'line',
                stack: '总量',
                data: [120, 132, 101, 134, 90, 230, 210, 101, 230, 260],
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    color: props.lineColor
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0, color: props.colors[0]
                            },
                            {
                                offset: 1, color: props.colors[1]
                            }
                        ],

                        global: false
                    }
                },
            },
        ]
    };

    myChart.setOption(option);
}

function setChartData(xData: Array<any>, yData: Array<any>) {
    if (myChart) {
        myChart.setOption({
            xAxis: {
                data: xData,
            },
            series: [
                {
                    data: yData,
                }
            ]
        })
    }
}
// 暴漏给父组件使用
defineExpose({ setChartData })

onMounted(() => {
    initEcharts()
})

const resizeChart = () => {
    myChart?.resize();
};

window.addEventListener('resize', resizeChart);

onUnmounted(() => {
    window.removeEventListener('resize', resizeChart);
    myChart.dispose();
});


</script>

<style scoped lang="scss">
.echarts {
    width: 100%;
    height: 100%;
    display: flex;
    pointer-events: all;

    &__label {
        width: 120px;
        height: 28px;
        margin-right: 5px;
        background: url("@/assets/images/components/footer_label.png") no-repeat;
        background-size: cover;
        text-align: center;
        line-height: 28px;
        flex-shrink: 0;
        margin-top: 10px;
        font-size: 16px;
        align-self: center;
    }

    &__value {
        flex: 1;
    }
}
</style>