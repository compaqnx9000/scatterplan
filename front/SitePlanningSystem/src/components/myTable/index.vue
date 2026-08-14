<template>
    <div class='myTable'>
        <div class="myTable__header">
            <div class="myTable__header__item" v-for="(i, c) in tableHeader" :key="c">
                {{ i.text }}
            </div>
        </div>
        <div class="myTable__body">
            <div class="myTable__body__list" v-for="(i, c) in tableData" :key="c" @click="selRowInfo(i)">
                <div class="myTable__body__list__item" v-for="(j, k) in tableHeader" :key="k">
                    <el-tooltip :content="i[j.key]">
                        {{ i[j.key] }}
                    </el-tooltip>
                </div>
            </div>
            <div v-if="tableData.length == 0" style="padding: 20px;text-align: center;color: #a0a0a0;">*暂无数据
            </div>
        </div>
        <el-pagination layout="prev, pager, next" :total="queryParams.total" :pageSize="queryParams.pageSize"
            @change="handleCurrentChange" style="justify-content: flex-end" />
    </div>
</template>

<script setup lang='ts'>
// import { detectionList } from '@/request/dataCenter'

let props = defineProps({
    tableHeader: {
        type: Array<any>,
        default: () => {
            return [];
        },
    },
    tableData: {
        type: Array<any>,
        default: () => {
            return [];
        },
    },
    pageParams: {
        type: Object,
        defaultu: {}
    }
})

let queryParams = ref<any>({
    pageNum: 1,
    pageSize: 10,
    total: 0,
})


watch(() => props.pageParams, () => {
    if (props.pageParams) {
        for (const key in queryParams.value) {
            queryParams.value[key] = props.pageParams[key]
        }
    }
}, {
    deep: true,
    immediate: true
})

let emits = defineEmits(['syncPageParams', 'selRowInfo'])
const handleCurrentChange = (val: number) => {
    queryParams.value.pageNum = val;
    emits('syncPageParams', queryParams.value)
};

function selRowInfo(rowInfo: any) {
    emits('selRowInfo', rowInfo)
}

</script>

<style lang='scss'>
.myTable {
    pointer-events: auto;
    flex: 1;
    height: 0;
    display: flex;
    flex-direction: column;
    margin-top: 10px;

    &__header {
        width: calc(100% - 4px);
        height: 28px;
        line-height: 28px;
        background: no-repeat url('@/assets/images/dataCenter/icon2.png') #1A9AF340;
        background-size: 100% 100%;
        display: flex;

        &__item {
            flex: 1;
            padding-left: 8px;
        }
    }

    &__body {
        // max-height: 200px;
        flex: 1;
        height: 0;
        overflow-y: scroll;
        margin-top: 4px;

        &__list {
            margin-bottom: 4px;
            display: flex;

            &__item {
                flex: 1;
                line-height: 28px;
                background: var(--1, rgba(20, 112, 199, 0.20));
                padding-left: 8px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }
}
</style>