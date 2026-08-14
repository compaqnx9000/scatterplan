import service from "./request";
// 登录
export function login(username: string, password: string){
  return service({
    url: '/login/',
    method: 'post',
    data: {
      username,
      password:password,
      // code,
      // uuid
    },
    headers: {
      isToken: false,
    },
  });
}
// 获取验证码
export function captchaImage(){
  return service({
    url: '/captchaImage',
    method: 'get',
    headers: {
      isToken: false,
    },
  });
}
// 获取我的详细信息
export function getInfo(){
  return service({
    url: '/getInfo',
    method: 'get'
  });
}
// 退出方法
export function logout(){
  return service({
    url: '/logout',
    method: 'post'
  });
}
// 修改我的信息
export function updateUserProfile(data: any){
  return service({
    url: '/system/user/profile',
    method: 'put',
    data
  });
}
// 用户密码重置
export function updateUserPwd(oldPassword: string, newPassword: string){
  const data = {
    oldPassword,
    newPassword
  }
  return service({
    url: '/system/user/profile/updatePwd',
    method: 'put',
    params: data
  });
}
// 查询用户列表
export function listUser(query: any){
  return service({
    url: '/system/user/list',
    method: 'get',
    params: query
  });
}
// 新增用户
export function addUser(data:any){
  return service({
    url: '/system/user',
    method: 'post',
    data: data
  });
}
// 删除用户
export function delUser(userId:number){
  return service({
    url: '/system/user/' + userId,
    method: 'delete'
  });
}
// 用户禁用启用
export function changeStatus(userId:number,status:string){
  return service({
    url: '/system/user/changeStatus',
    method: 'put',
    data:{
      userId,status
    }
  });
}
// 查询用户详细
export function getUser(userId:number){
  return service({
    url: "/system/user/" + userId,
    method: "get",
  });
}
// 修改用户信息
export function updateUser(data:any){
  return service({
    url: "/system/user",
    method: "put",
    data: data,
  });
}
// 用户密码重置
export function resetUserPwd(userId:string, password:string){
  const data = {
    userId,
    password
  }
  return service({
    url: '/system/user/resetPwd',
    method: 'put',
    data: data
  });
}