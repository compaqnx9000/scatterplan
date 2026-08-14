/**
 * 出发点经纬度+方位角+距离，计算到达点经纬度 https://blog.csdn.net/qq_27361945/article/details/79032508
 */


//定义一些常量
let x_PI = 3.14159265358979324 * 3000.0 / 180.0;
let PI = 3.1415926535897932384626;
let a = 6378245.0;
let ee = 0.00669342162296594323;
/**
 * 百度坐标系 (BD-09) 与 火星坐标系 (GCJ-02)的转换
 * 即 百度 转 谷歌、高德
 * @param bd_lon
 * @param bd_lat
 * @returns {*[]}
 */
export function bd09togcj02(bd_lon:number, bd_lat:number) {
	let x_pi = 3.14159265358979324 * 3000.0 / 180.0;
	let x = bd_lon - 0.0065;
	let y = bd_lat - 0.006;
	let z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * x_pi);
	let theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * x_pi);
	let gg_lng = z * Math.cos(theta);
	let gg_lat = z * Math.sin(theta);
	return [gg_lng, gg_lat]
}
/**
 * 火星坐标系 (GCJ-02) 与百度坐标系 (BD-09) 的转换
 * 即谷歌、高德 转 百度
 * @param lng
 * @param lat
 * @returns {*[]}
 */
export function gcj02tobd09(lng:number, lat:number) {
	let z = Math.sqrt(lng * lng + lat * lat) + 0.00002 * Math.sin(lat * x_PI);
	let theta = Math.atan2(lat, lng) + 0.000003 * Math.cos(lng * x_PI);
	let bd_lng = z * Math.cos(theta) + 0.0065;
	let bd_lat = z * Math.sin(theta) + 0.006;
	return [bd_lng, bd_lat]
}
/**
 * WGS84转GCj02
 * @param lng
 * @param lat
 * @returns {*[]}
 */
export function wgs84togcj02(lng:number, lat:number) {
	if (out_of_china(lng, lat)) {
		return [lng, lat]
	} else {
		let dlat = transformlat(lng - 105.0, lat - 35.0);
		let dlng = transformlng(lng - 105.0, lat - 35.0);
		let radlat = lat / 180.0 * PI;
		let magic = Math.sin(radlat);
		magic = 1 - ee * magic * magic;
		let sqrtmagic = Math.sqrt(magic);
		dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
		dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
		let mglat = lat + dlat;
		let mglng = lng + dlng;
		return [mglng, mglat]
	}
}
/**
 * GCJ02 转换为 WGS84
 * @param lng
 * @param lat
 * @returns {*[]}
 */
export function gcj02towgs84(lng:number, lat:number) {
	if (out_of_china(lng, lat)) {
		return [lng, lat]
	} else {
		let dlat = transformlat(lng - 105.0, lat - 35.0);
		let dlng = transformlng(lng - 105.0, lat - 35.0);
		let radlat = lat / 180.0 * PI;
		let magic = Math.sin(radlat);
		magic = 1 - ee * magic * magic;
		let sqrtmagic = Math.sqrt(magic);
		dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
		dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
		let mglat = lat + dlat;
		let mglng = lng + dlng;
		return [lng * 2 - mglng, lat * 2 - mglat]
	}
}

function transformlat(lng:number, lat:number) {
	let ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
	ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
	ret += (20.0 * Math.sin(lat * PI) + 40.0 * Math.sin(lat / 3.0 * PI)) * 2.0 / 3.0;
	ret += (160.0 * Math.sin(lat / 12.0 * PI) + 320 * Math.sin(lat * PI / 30.0)) * 2.0 / 3.0;
	return ret
}

function transformlng(lng:number, lat:number) {
	let ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
	ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
	ret += (20.0 * Math.sin(lng * PI) + 40.0 * Math.sin(lng / 3.0 * PI)) * 2.0 / 3.0;
	ret += (150.0 * Math.sin(lng / 12.0 * PI) + 300.0 * Math.sin(lng / 30.0 * PI)) * 2.0 / 3.0;
	return ret
}
/**
 * 判断是否在国内，不在国内则不做偏移
 * @param lng
 * @param lat
 * @returns {boolean}
 */
function out_of_china(lng:number, lat:number) {
	return (lng < 72.004 || lng > 137.8347) || ((lat < 0.8293 || lat > 55.8271) || false);
}


// 计算距离 方法定义 lat,lng 返回值单位：km
export function GetDistance(lat1:number, lng1:number, lat2:number, lng2:number) {
	let radLat1 = lat1 * Math.PI / 180.0;
	let radLat2 = lat2 * Math.PI / 180.0;
	let a = radLat1 - radLat2;
	let b = lng1 * Math.PI / 180.0 - lng2 * Math.PI / 180.0;
	let s = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(a / 2), 2) +
		Math.cos(radLat1) * Math.cos(radLat2) * Math.pow(Math.sin(b / 2), 2)));
	s = s * 6378.137; // EARTH_RADIUS;
	s = Math.round(s * 10000) / 10000;
	return s;
}


// 计算航向角度
export function getAngle(lng_a:number, lat_a:number, lng_b:number, lat_b:number) {
	let y = Math.sin(lng_b - lng_a) * Math.cos(lat_b);
	let x =
		Math.cos(lat_a) * Math.sin(lat_b) -
		Math.sin(lat_a) * Math.cos(lat_b) * Math.cos(lng_b - lng_a);
	let angle = Math.atan2(y, x);
	angle = (180 * angle) / Math.PI;
	//下面是根据自己的图片初始方向进行校准----不同的图片这里校准是不一样的，需要自行处理
	if (angle < 0) {
		angle = -angle;
	} else {
		angle = 360 - angle;
	}
	return angle;
}
