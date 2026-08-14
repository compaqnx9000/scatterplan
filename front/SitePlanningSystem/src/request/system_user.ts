import service from "./request"

// 获取用户列表
export function listUser(query: any){
  return service({
    url: '/users/',
    method: 'get',
    params: query
  });
}

// 添加用户
export function addUser(data: any){
  return service({
    url: '/users/',
    method: 'post',
    data: data
  });
}

// 删除用户
export function delUser(userId: number){
  return service({
    url: '/users/' + userId + '/',
    method: 'delete'
  });
}

// 修改用户
export function updateUser(data: any){
  return service({
    url: '/users/' + data.id + '/',
    method: 'put',
    data: data
  });
}


// 批量删除
export function batchDelUser(userIds: number[]){
  return service({
    url: '/users/batch_delete/',
    method: 'delete',
    data: {
      ids: userIds
    }
  });
}