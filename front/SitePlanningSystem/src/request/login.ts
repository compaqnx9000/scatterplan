import service from "./request"

// 登录方法
export function login(username: string = 'admin', password: string = 'admin123') {
  const data = {
    username,
    password
  }
  return service({
    url: '/login',
    headers: {
      isToken: false
    },
    method: 'post',
    data: data
  })
}
