import service from "./request"

// 道路名称
export function getRouteName(currentStatus?: string) {
    return service({
        url: '/sdap/pointAnnotation/list',
        method: 'get',
        params: {
            currentStatus,
            pageNum: 1,
            pageSize: 100000
        }
    })
}
