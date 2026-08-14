import service from "./request"


export function listProjects(query: any) {
  return service({
    url: "/projects/plans/",
    method: "get",
    params: query,
  });
}

export function createProject(data: { name: string }) {
  return service({
    url: "/projects/plans/",
    method: "post",
    data,
  });
}

export function getProject(id: number | string) {
  return service({
    url: `/projects/plans/${id}/`,
    method: "get",
  });
}

export function deleteProject(id: number | string) {
  return service({
    url: `/projects/plans/${id}/`,
    method: "delete",
  });
}

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
