import service from "./request"

//检索条件列表
export function getProjectList() {
  return service({
    url: '/sdap/projectManage',
    method: 'get',
  })
}

//检索
export function getProPoint(data: any) {
  return service({
    url: '/sdap/projectManage/search',
    method: 'post',
    data
  })
}
// 查找图片
export function getForDaPing(projectId: any) {
  return service({
    url: '/sdap/documents/getForDaPing/' + projectId,
    method: 'get',
  })
}
// 营销进展
export function getmarking(projectId: any) {
  return service({
    url: '/sdap/marketing/getListOfLast/' + projectId,
    method: 'get',
  })
}
// 前期进展
export function getfirst(projectId: any) {
  return service({
    url: '/sdap/preparation/getListOfLast/' + projectId,
    method: 'get',
  })
}
// 施工进展
export function getlastlist(projectId: any) {
  return service({
    url: '/sdap/construction/getListOfLast/' + projectId,
    method: 'get',
  })
}