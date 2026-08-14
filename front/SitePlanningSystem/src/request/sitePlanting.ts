import service from "./request"


// 获取单链路记录
export function listSingleLink(query: any){
  return service({
    url: '/projects/singlelinks/',
    method: 'get',
    params: query
  });
}
// 删除单链路记录
export function deleteSingleLink(id: number){
  return service({
    url: `/projects/singlelinks/${id}/`,
    method: 'delete',
  });
}

  // 删除区域覆盖记录
  export function deleteAreaCoverage(id: number) {
    return service({
      url: `/projects/areacoverages/${id}/`,
      headers: {
        isToken: true
      },
      method: 'delete',
    })
  }


// 获取区域覆盖记录列表
export function listAreaCoverage(query: any){
  return service({
    url: '/projects/areacoverages/',
    method: 'get',
    params: query
  });
}
