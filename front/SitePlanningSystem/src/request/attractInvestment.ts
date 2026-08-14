import service from "./request"

//查询产业分布接口
export function getqyfbList(data: any) {
  return service({
    url: '/sdap/company/search',
    method: 'post',
    data
  })
}
// 招商引资页面接口

// 查询人口统计信息
export function getCountPopulation(districtCode: number) {
    return service({
        url: '/sdap/popData/list',
        method: 'get',
        params: {
            districtCode,
            year: new Date().getFullYear() -1
        }
    })
}

// 获取按年份范围获取人口统计信息
export function getCountPopulationList(districtCode: number, startYear: number, endYear: number) {
    return service({
        url: '/sdap/popData/list',
        method: 'get',
        params: {
            districtCode,
            endYear,
            startYear
        }
    })
}

// 获取gdp信息
export function getGdpData(districtCode: number) {
    return service({
        url: '/sdap/gdpData/list',
        method: 'get',
        params: {
            districtCode,
            year: new Date().getFullYear() -1
        }
    })
}

// 获取按年份范围获取gdp信息列表
export function getGdpDataList(districtCode: number, startYear: number, endYear: number) {
    return service({
        url: '/sdap/gdpData/list',
        method: 'get',
        params: {
            districtCode,
            endYear,
            startYear
        }
    })
}

// 获取城市优势标签
export function getCityAdvantage(districtCode: number | string) {
    return service({
        url: '/sdap/cityAdvantage/list',
        method: 'get',
        params: {
            districtCode
        }
    })
}

// 获取土地详细信息
export function getSpanInfo(landId: number) {
    return service({
        url: '/sdap/info/' + landId,
        method: 'get',
    })
}

// 新增招商方案
export function addPlan(data: any) {
    return service({
        url: '/sdap/investmentPlan',
        method: 'post',
        data
    })
}

// 招商方案列表
export function getPlanList(data: any) {
    return service({
        url: '/sdap/investmentPlan/list',
        method: 'get',
        params: data
    })
}

// 招商方案删除
export function delPlan(planId: number) {
    return service({
        url: '/sdap/investmentPlan/' + planId,
        method: 'delete',
    })
}

// 招商方案详情
export function getPlanDetail(id: any) {
    return service({
        url: '/sdap/investmentPlan/' + id,
        method: 'get',
    })
}

// 获取用地规划平台-主干道占用面积
// export function getMainRoadOccupyArea() {
//     return service({
//         url: '/sdap/dataCenter/getMainRoadOccupyArea',
//         method: 'get',
//     })
// }

// 用地规划平台-主干道地块数量
export function getMainRoadPlotArea() {
    return service({
        url: '/sdap/dataCenter/getMainRoadPlotArea',
        method: 'get',
    })
}

// 用地规划平台-道路网络数量
export function getRoadNetwork() {
    return service({
        url: '/sdap/dataCenter/getRoadNetwork',
        method: 'get',
    })
}

// 用地规划平台-未用地面积
export function getUnusedArea() {
    return service({
        url: '/sdap/dataCenter/getUnusedArea',
        method: 'get',
    })
}

// 用地规划平台-产业功能区分布面积
export function getIndustrialArea() {
    return service({
        url: '/sdap/dataCenter/getIndustrialArea',
        method: 'get',
    })
}

// 查询重点区域列表
export function listArea(query: any) {
    return service({
        url: '/sdap/focusArea/list',
        method: 'get',
        params: query
    })
}
// 查询企业信息列表
export function listCompany(query: any) {
    return service({
        url: '/sdap/company/list',
        method: 'get',
        params: query
    })
}
// 查询区域
export function getComNumByZone(query: any) {
    return service({
        url: '/sdap/company/getComNumByZone',
        method: 'get',
        params: query
    })
}

export function getListByLastYear(query: any) {
    return service({
        url: '/sdap/area/getListByLastYear',
        method: 'get',
        params: query
    })
}


// 获取产业分布列表
export function getClassification(query: any) {
    return service({
        url: '/sdap/classification/getList',
        method: 'get',
        params: query
    })
}

// 获取产业链文件
export function getPlanFile(query:any){
    return service({
        url: '/sdap/classification/getPlanFile',
        method: 'get',
        params: query
    })
}


// 获取招商楼宇列表
export function getMerchantsBuilding(query:any){
    return service({
        url: '/sdap/merchantsBuilding/list',
        method: 'get',
        params: query
    })
}

// 获取产业招商列表
export function getMerchantsIndustry(query:any){
    return service({
        url: '/sdap/merchantsIndustry/list',
        method: 'get',
        params: query
    })
}

// 获取项目信息列表
export function getMerchantsProject(query:any){
    return service({
        url: '/sdap/merchantsProject/list',
        method: 'get',
        params: query
    })
}
//获取AI历史记录会话
// http://192.168.5.10:8080/doc.html#/default/ai%E5%8E%86%E5%8F%B2%E6%95%B0%E6%8D%AE/addUsingPOST_1
export function getAiHistory(query:any){
    return service({
        url: '/sdap/aiHistory/list',
        method: 'get',
        params: query
    })
}

export function addHistory(data:any){
    return service({
        url: '/sdap/aiHistory',
        method: 'post',
        data
    })
}
// 获取园区楼宇信息
export function getFocusAreaBuilding(query:any){
    return service({
        url: '/sdap/focusAreaBuilding/getListByKey',
        method: 'get',
        params: query
    })
}

// 获取园区楼宇信息
export function getAreaData(query:any){
    return service({
        url: '/sdap/areaData/list',
        method: 'get',
        params: query
    })
}

// 获取红谷滩简介信息
export function getHgtIntroduction(query:any){
    return service({
        url: '/sdap/hgtIntroduction/list',
        method: 'get',
        params: query
    })
}

// 获取红谷滩简介信息
export function getContentHtml(url:any){
    return service({
        url: url,
        method: 'get',
    })
}