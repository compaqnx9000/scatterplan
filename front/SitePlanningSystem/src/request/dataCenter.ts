import service from "./request"

// 数据中心相关接口

// 三维立体展示-年份数据
export function infrastructureMergingList() {
    return service({
        url: '/sdap/infrastructureMerging/list',
        method: 'get'
    })
}

// 三维立体展示-建筑变化数据
export function infrastructureMergingListBase(baseMapId: string) {
    return service({
        url: '/sdap/infrastructureBase/listBaseVO',
        method: 'get',
        params: {
            baseMapId,
            pageNum: 1,
            pageSize: 100000
        }
    })
}

// 项目超支总览
export function getProjectOverBudget() {
    return service({
        url: '/sdap/monitor/getOverBudget',
        method: 'get'
    })
}

// 项目产业资源数量统计
export function projectMonitorStatistics() {
    return service({
        url: '/sdap/monitor/statistics',
        method: 'get'
    })
}
// 项目监控列表数据
export function projectMonitorList(params: any) {
    return service({
        url: '/sdap/monitor/list',
        method: 'get',
        params
    })
}

// 状态检测 - 土地利用列表数据
export function detectionLandList(params: any) {
    return service({
        url: '/sdap/detectionLand/list',
        method: 'get',
        params
    })
}

// 状态检测 - 自然资源列表数据
export function detectionNaturalList(params: any) {
    return service({
        url: '/sdap/detectionNatural/list',
        method: 'get',
        params
    })
}

// 状态检测 - 项目工程列表数据
export function detectionProjectList(params: any) {
    return service({
        url: '/sdap/detectionProject/list',
        method: 'get',
        params
    })
}

// 数据可视化与决策支持-项目进程
export function getDataVisualization(params: any) {
    return service({
        url: '/sdap/dataCenter/getDataVisualization',
        method: 'get',
        params
    })
}

// 用地规划大数据中心与可视化-未利用地块面积
export function getUnusedTotalArea(params: any) {
    return service({
        url: '/sdap/dataCenter/getUnusedTotalArea',
        method: 'get',
        params
    })
}

// 项目监控平台数据
export function getProjectMonitorData(params: any) {
    return service({
        url: '/sdap/dataCenter/getProjectMonitorData',
        method: 'get',
        params
    })
}

// 数据中心-产业分布-产业资源数量
export function getComNumByZone(params: any) {
    return service({
        url: '/sdap/company/getComNumByZone',
        method: 'get',
        params
    })
}

// 数据中心-产业分布-资源面积
export function getListByLastYear(params: any) {
    return service({
        url: '/sdap/area/getListByLastYear',
        method: 'get',
        params
    })
}