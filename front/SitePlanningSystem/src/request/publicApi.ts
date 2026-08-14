/**
 * 用于存放公共接口
 */
import service from "./request"

// 查看方案文档
export function getPlanFileManagement(key: string) {
    return service({
        url: '/sdap/planFileManagement/getByKey?key=' + key,
        method: 'get',
    })
}

// 意见反馈
export function feedback(data: any) {
    return service({
        url: '/sdap/feedback',
        method: 'post',
        data
    })
}
