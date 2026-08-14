import service from "./request"
// 登录
export function getGeoJson(name:string) {
    return service({
      url: `https://mars3d.ppcloud.link/geoserver/nanchang/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=nanchang:${name}&outputFormat=application/json`,
      method: 'get'
    })
  }
  