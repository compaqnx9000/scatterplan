import service from "./request";
// 获取单链路计算图片
export function getSingleLinkageImage(
  tx_lon: number,
  tx_lat: number,
  rx_lon: number,
  rx_lat: number
) {
  const data = {
    tx_lat,
    tx_lon,
    rx_lon,
    rx_lat,
  };
  return service({
    url: "/singlelink/calculate",
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}

// 获取聚类分析列表
export function getClusterAnalysisList(data: {
  tif_path: string;
  loss_threshold: string;
  eps_cells: string;
  min_samples: string;
  p: string;
}) {
  return service({
    url: "/projects/clustering/",
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}

// 使用站点
export function useSite(data: { project_id: number; site_id: number }) {
  return service({
    url: "/projects/station-selection/",
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}

// 删除站点
export function deleteSite(data: { project_id: number; site_id: number }) {
  return service({
    url: `/projects/singlelinks/${data.site_id}/`,
    headers: {
      isToken: true,
    },
    method: "delete",
    data: data,
  });
}

// 导出excel
export function exportExcel(data: { id: number; cluster_stats: number }) {
  return service({
    url: `/projects/station-export-excel/`,
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}

// 设置颜色重新生成图像
export function setColorGenerateImage(data: {
  id: number | string;
  tif_path: string;
  png_path: string;
  colors: Array<string>;
  min_val: number;
  max_val: number;
}) {
  return service({
    url: `/projects/ribbon-setting/`,
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}
// 获取站点推荐列表
export function getRecommendSiteList(data: {
  area_coverage_id: number;
}) {
  return service({
    url: "/projects/areacoverages/",
    headers: {
      isToken: true,
    },
    method: "get",
    params: data,
  });
}

// 保存站点推荐信息
export function saveRecommendSiteList(data: {
  id: number;
  name: string;
  number : number;
}) {
  return service({
    url: `/projects/stations/${data.id}/`,
    headers: {
      isToken: true,
    },
    method: "patch",
    data: {
      name: data.name,
      number: data.number,
    },
  });
}

// 速率计算可靠度
export function calculateReliability(data: {
  id: number;
  comm_rate: string;
}) {
  return service({
    url: "/projects/recalculate-fade-margin/",
    headers: {
      isToken: true,
    },
    method: "post",
    data: data,
  });
}
