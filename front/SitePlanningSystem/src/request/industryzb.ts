import service from "./request"

//GDP生产总值
export function getindustGdp(startYear:any,endYear:any) {
  return service({
    url: `/sdap/gdp/getListByYear?startYear=${startYear}&endYear=${endYear}`,
    method: 'get',
  })
}

//财政收支明细列表
export function getindustSzList(startYear:any,endYear:any) {
  return service({
    url: `/sdap/fiscal/getListByYear?startYear=${startYear}&endYear=${endYear}`,
    method: 'get',
  })
}

//固定资产明细列表
export function geGdList(yeard:any) {
  return service({
    url: `/sdap/investment/getListByYear?year=${yeard}`,
    method: 'get',
  })
}

//工业增长列表
export function geGyGrouwthList(startYear:any,endYear:any) {
 return service({
    url: `/sdap/industry/getListByYear?startYear=${startYear}&endYear=${endYear}`,
    method: 'get',
  })
}

//市场规模列表
export function getMarketList(yeard:any) {
  return service({
    url: `/sdap/market/getListByYear?year=${yeard}`,
    method: 'get',
  })
}

//竞争格局--人口
export function getJzPatternList(startYear:any,endYear:any) {
 return service({
    url: `/sdap/population/getListByYear?startYear=${startYear}&endYear=${endYear}`,
    method: 'get',
  })
}

//竞争格局--教育
export function getJzEduList(yeard:any) {
 return service({
    url: `/sdap/education/getListByYear?year=${yeard}`,
    method: 'get',
  })
}

//科技创新
export function getTechList(yeard:any) {
 return service({
    url: `/sdap/technology/getListByYear?year=${yeard}`,
    method: 'get',
  })
}

//人民生活
export function getLvingList(yeard:any) {
 return service({
    url: `/sdap/living/getListByYear?year=${yeard}`,
    method: 'get',
  })
}