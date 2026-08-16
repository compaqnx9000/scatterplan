
// 居中展示一个 黑色的描述信息
export function Toast(msg:string, duration:number) {
    duration = duration ? 3000 : duration;
    var m = document.createElement('div');
    m.innerHTML = msg;
    m.style.cssText = `
        font-size: 14px;
        color: rgb(255, 255, 255);
        background-color: rgba(0, 0, 0, .8);
        padding: 10px 16px;
        margin: 0;
        border-radius: 8px;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: auto;
        max-width: 80vw;
        z-index:9999999;
        overflow:hidden;
        text-align: center;
        white-space: nowrap;`;
    document.body.appendChild(m);
    setTimeout(function() {
        var d = 0.5;
        m.style.opacity = '0';
        setTimeout(function() { document.body.removeChild(m) }, d * 1000);
    }, duration);
}


// 获取map实例
import * as mars3d from "mars3d";
const Cesium = mars3d.Cesium;


let mapInstance: mars3d.Map;

export function setMapInstance(map: mars3d.Map) {
  mapInstance = map;
}

export function getMapInstance() {
  return mapInstance;
}


// 随机值
export function generateRandomId() {
  const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let id = letters.charAt(Math.floor(Math.random() * letters.length));
  for (let i = 1; i < 8; i++) {
      id += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return id;
}

// 定义坐标类型
type Position = [number, number] | [number, number, number];

// 定义几何类型
interface Geometry {
    type: string;
}

interface Point extends Geometry {
    type: 'Point';
    coordinates: Position;
}

interface MultiPoint extends Geometry {
    type: 'MultiPoint';
    coordinates: Position[];
}

interface LineString extends Geometry {
    type: 'LineString';
    coordinates: Position[];
}

interface MultiLineString extends Geometry {
    type: 'MultiLineString';
    coordinates: Position[][];
}

interface Polygon extends Geometry {
    type: 'Polygon';
    coordinates: Position[][];
}

interface MultiPolygon extends Geometry {
    type: 'MultiPolygon';
    coordinates: Position[][][];
}

type GeometryObject = Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon;

// 定义 Feature 类型
interface Feature<G extends GeometryObject = GeometryObject, P = any> {
    type: 'Feature';
    geometry: G | null;
    properties: P | null;
    id?: string | number;
}

// 定义 FeatureCollection 类型
export interface FeatureCollection<G extends GeometryObject = GeometryObject, P = any> {
    type: 'FeatureCollection';
    features: Feature<G, P>[];
}

// 定义函数来获取 GeoJSON 的最大最小经纬度
export function getGeoJsonBounds(geojson: FeatureCollection): { minLon: number; maxLon: number; minLat: number; maxLat: number } {
  let minLon = Infinity;
  let maxLon = -Infinity;
  let minLat = Infinity;
  let maxLat = -Infinity;

  // 遍历 GeoJSON 中的每个 feature
  geojson.features.forEach((feature) => {
      const geometry = feature.geometry;
      if (geometry) {
          if (geometry.type === 'Point') {
              const [lon, lat] = geometry.coordinates;
              minLon = Math.min(minLon, lon);
              maxLon = Math.max(maxLon, lon);
              minLat = Math.min(minLat, lat);
              maxLat = Math.max(maxLat, lat);
          } else if (geometry.type === 'LineString' || geometry.type === 'MultiPoint') {
              geometry.coordinates.forEach(([lon, lat]) => {
                  minLon = Math.min(minLon, lon);
                  maxLon = Math.max(maxLon, lon);
                  minLat = Math.min(minLat, lat);
                  maxLat = Math.max(maxLat, lat);
              });
          } else if (geometry.type === 'Polygon' || geometry.type === 'MultiLineString') {
              geometry.coordinates.forEach((ring) => {
                  ring.forEach(([lon, lat]) => {
                      minLon = Math.min(minLon, lon);
                      maxLon = Math.max(maxLon, lon);
                      minLat = Math.min(minLat, lat);
                      maxLat = Math.max(maxLat, lat);
                  });
              });
          } else if (geometry.type === 'MultiPolygon') {
              geometry.coordinates.forEach((polygon) => {
                  polygon.forEach((ring) => {
                      ring.forEach(([lon, lat]) => {
                          minLon = Math.min(minLon, lon);
                          maxLon = Math.max(maxLon, lon);
                          minLat = Math.min(minLat, lat);
                          maxLat = Math.max(maxLat, lat);
                      });
                  });
              });
          }
      }
  });

  return {
      minLon,
      maxLon,
      minLat,
      maxLat
  };
}


// 定义函数来获取 GeoJSON 的四个角的经纬度
export function getGeoJsonCorners(geojson: FeatureCollection): {
  topLeft: [number, number];
  topRight: [number, number];
  bottomLeft: [number, number];
  bottomRight: [number, number];
} {
  const bounds = getGeoJsonBounds(geojson);
  const { minLon, maxLon, minLat, maxLat } = bounds;

  return {
      topLeft: [minLon, maxLat],
      topRight: [maxLon, maxLat],
      bottomLeft: [minLon, minLat],
      bottomRight: [maxLon, minLat]
  };
}

// 定义 GeoJSON 相关类型
type GeoJSONPoint = {
    type: 'Point';
    coordinates: [number, number];
};

type GeoJSONMultiPoint = {
    type: 'MultiPoint';
    coordinates: [number, number][];
};

type GeoJSONLineString = {
    type: 'LineString';
    coordinates: [number, number][];
};

type GeoJSONMultiLineString = {
    type: 'MultiLineString';
    coordinates: [number, number][][];
};

type GeoJSONPolygon = {
    type: 'Polygon';
    coordinates: [number, number][][];
};

type GeoJSONMultiPolygon = {
    type: 'MultiPolygon';
    coordinates: [number, number][][][];
};

type GeoJSONGeometry =
    | GeoJSONPoint
    | GeoJSONMultiPoint
    | GeoJSONLineString
    | GeoJSONMultiLineString
    | GeoJSONPolygon
    | GeoJSONMultiPolygon;

type GeoJSONFeature = {
    type: 'Feature';
    geometry: GeoJSONGeometry;
    properties: Record<string, any>;
};

type GeoJSONFeatureCollection = {
    type: 'FeatureCollection';
    features: GeoJSONFeature[];
};

type GeoJSON = GeoJSONFeatureCollection | GeoJSONFeature | GeoJSONGeometry;
// 计算 GeoJSON 中心点的函数
export function calculateGeoJSONCenter(geojson: GeoJSON): [number, number] | null {
    let allCoordinates: [number, number][] = [];

    function extractCoordinates(geometry: GeoJSONGeometry) {
        if (geometry.type === 'Point') {
            allCoordinates.push(geometry.coordinates);
        } else if (geometry.type === 'MultiPoint' || geometry.type === 'LineString') {
            allCoordinates = allCoordinates.concat(geometry.coordinates);
        } else if (geometry.type === 'MultiLineString' || geometry.type === 'Polygon') {
            geometry.coordinates.forEach((coordArray) => {
                allCoordinates = allCoordinates.concat(coordArray);
            });
        } else if (geometry.type === 'MultiPolygon') {
            geometry.coordinates.forEach((polygon) => {
                polygon.forEach((coordArray) => {
                    allCoordinates = allCoordinates.concat(coordArray);
                });
            });
        }
    }

    if (geojson.type === 'FeatureCollection') {
        geojson.features.forEach((feature) => {
            extractCoordinates(feature.geometry);
        });
    } else if (geojson.type === 'Feature') {
        extractCoordinates(geojson.geometry);
    } else {
        extractCoordinates(geojson as GeoJSONGeometry);
    }

    if (allCoordinates.length === 0) {
        return null;
    }

    let sumX = 0;
    let sumY = 0;

    allCoordinates.forEach(([x, y]) => {
        sumX += x;
        sumY += y;
    });

    const centerX = sumX / allCoordinates.length;
    const centerY = sumY / allCoordinates.length;

    return [centerX, centerY];
}




export function getCenterPoint(data: any[]) {
    let xSum = 0;
    let ySum = 0;
    let zSum = 0;
    const numPoints = data.length;

    for (let i = 0; i < numPoints; i++) {
        const point = data[i];
        xSum += point.x;
        ySum += point.y;
        zSum += point.z;
    }

    const center = {
        x: Cesium.Math.toDegrees(xSum / numPoints),
        y: Cesium.Math.toDegrees(ySum / numPoints),
        z: zSum / numPoints
    }
    return center;
}


// 16进制颜色转为rgba

export function hexToRgba(hex: string, alpha: number = 1): string {
    // 移除#号
    hex = hex.replace('#', '');
    
    // 解析颜色值
    let r: number, g: number, b: number, a: number | undefined;
    
    // 处理3位、4位、6位和8位十六进制颜色值
    if (hex.length === 3 || hex.length === 4) {
        r = parseInt(hex[0] + hex[0], 16);
        g = parseInt(hex[1] + hex[1], 16);
        b = parseInt(hex[2] + hex[2], 16);
        if (hex.length === 4) {
            a = Math.round((parseInt(hex[3] + hex[3], 16) / 255) * 100) / 100;
        }
    } else if (hex.length === 6 || hex.length === 8) {
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
        if (hex.length === 8) {
            a = Math.round((parseInt(hex.substring(6, 8), 16) / 255) * 100) / 100;
        }
    } else {
        throw new Error('无效的十六进制颜色格式');
    }
    
    // 如果没有从hex中解析出alpha值，则使用传入的alpha参数
    if (a === undefined) {
        a = alpha;
    }
    
    // 确保alpha值在有效范围内
    a = Math.max(0, Math.min(1, a));
    
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}