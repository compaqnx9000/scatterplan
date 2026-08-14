import service from "./request";

// 用地规划页面接口
export function getTrafficConditions() {
  return service({
    url: "/sdap/land/use/getTrafficConditions",
    method: "get",
    params: {},
  });
}
// 土地利用现状
export function getAnalysisLandUseStatus() {
  return service({
    url: "/sdap/land/use/getAnalysisLandUseStatus",
    method: "get",
    params: {},
  });
}

// 用地变化
export function getAnalysisLandChange(params: any) {
  return service({
    url: "/sdap/land/use/getAnalysisLandChange",
    method: "get",
    params: {
      ...params
    },
  });
}

// 企业数量
export function getCompanyNumber() {
  return service({
    url: "/sdap/dataCenter/getCompanyNumber",
    method: "get",
    params: {},
  });
}

// 未来
export function futureForestList(params:any) {
  return service({
    url: "/sdap/futureForest/list",
    method: "get",
    params,
  });
}
