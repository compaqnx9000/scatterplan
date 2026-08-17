import { color } from "echarts";
import * as mars3d from "mars3d";
import { Label } from "mars3d-cesium";
import { MAP_LABEL_FONT } from "./mapLabelStyle";
import { parseLongitude, parseLatitude } from "./rules";
import { publicAsset } from "./publicAsset";

export interface CommunicationArea {
  id: number;
  name: string;
  type: string;
  geometry: {
    type: string;
    coordinates: number[][];
  };
}

const toLng = (value: any) => {
  const n = parseLongitude(value);
  return Number.isFinite(n) ? n : NaN;
};

const toLat = (value: any) => {
  const n = parseLatitude(value);
  return Number.isFinite(n) ? n : NaN;
};

const isValidLngLat = (lng: number, lat: number) =>
  Number.isFinite(lng) &&
  Number.isFinite(lat) &&
  lng >= -180 &&
  lng <= 180 &&
  lat >= -90 &&
  lat <= 90;
export default class CommunicationAreaService {
  map: mars3d.Map;
  graphicLayer: mars3d.layer.GraphicLayer;
  linkGraphics: mars3d.graphic.BaseGraphic[] = [];
  $bus: any;
  cluster_point_layer: mars3d.layer.GraphicLayer; /// 聚类点图层
  relay_cluster_point_layer: mars3d.layer.GraphicLayer; /// 中继聚类点图层
  smallRectangleLayer: mars3d.layer.GraphicLayer; /// 小矩形通信区
  prohibitedCommunicationAreaLayer: mars3d.layer.GraphicLayer; /// 限制通信区
  relayRectangleLayer: mars3d.layer.GraphicLayer; /// 中继矩形通信区
  constructor(map: mars3d.Map, bus: any) {
    this.map = map;
    this.graphicLayer = new mars3d.layer.GraphicLayer();
    this.cluster_point_layer = new mars3d.layer.GraphicLayer();
    this.relay_cluster_point_layer = new mars3d.layer.GraphicLayer(); /// 中继聚类点图层
    this.smallRectangleLayer = new mars3d.layer.GraphicLayer();
    this.prohibitedCommunicationAreaLayer = new mars3d.layer.GraphicLayer();
    this.relayRectangleLayer = new mars3d.layer.GraphicLayer(); /// 中继矩形通信区
    this.map.addLayer(this.graphicLayer);
    this.map.addLayer(this.cluster_point_layer);
    this.map.addLayer(this.smallRectangleLayer);
    this.map.addLayer(this.relay_cluster_point_layer); /// 中继聚类点图层
    this.map.addLayer(this.prohibitedCommunicationAreaLayer);
    this.map.addLayer(this.relayRectangleLayer); /// 中继矩形通信区
    this.$bus = bus;

    this.$bus.on("setCommunicationArea", (data: CommunicationArea) => {
      this.setCommunicationArea(data);
    });

    // 设置限制通信区
    this.$bus.on(
      "setProhibitedCommunicationArea",
      (data: CommunicationArea) => {
        this.setProhibitedCommunicationArea(data);
      },
    );

    // 添加矩形通信区
    this.$bus.on("addRectangleAreaImg", (data: any) => {
      this.addRectanglePrimitive(data);
    });

    // 添加圆形通信区
    this.$bus.on("addCircleAreaImg", (data: any) => {
      this.addCirclePrimitive(data);
    });

    this.$bus.on("drawCommunicationArea", (type: string) => {
      this.drawGraph(type);
    });

    this.$bus.on("cancelDrawPoint", () => {
      this.stopAreaDrawing();
      this.$bus.emit("mapPickMode", false);
    });

    // 二次绘制区域
    this.$bus.on("drawSmallCommunicationArea", (type: string) => {
      this.drawSmallGraph(type);
    });

    // 绘制中继区域
    this.$bus.on("drawRelayCommunicationArea", (type: string) => {
      this.drawRelayGraph(type);
    });

    // 显示通信区
    this.$bus.on("showCommunicationArea", (name: string) => {
      this.showCommunicationArea(name);
    });
    // 显示限制通信区
    this.$bus.on("showProhibitedCommunicationArea", (name: string) => {
      this.showProhibitedCommunicationArea(name);
    });

    this.$bus.on("HideAllCommunicationArea", () => {
      this.graphicLayer.eachGraphic((graphicItem) => {
        graphicItem.show = false;
      });
      this.cluster_point_layer.eachGraphic((graphicItem) => {
        graphicItem.show = false;
      });
      this.smallRectangleLayer.eachGraphic((graphicItem) => {
        graphicItem.show = false;
      });
      this.prohibitedCommunicationAreaLayer.eachGraphic((graphicItem) => {
        graphicItem.show = false;
      });
    });

    this.$bus.on(
      "showAllCommunicationArea",
      (params: { activeName: string; area_type: string }) => {
        console.log(
          "showAllCommunicationArea",
          params.activeName,
          params.area_type,
        );

        this.graphicLayer.eachGraphic((graphicItem) => {
          graphicItem.show = true;
        });
        this.cluster_point_layer.eachGraphic((graphicItem) => {
          graphicItem.show = true;
        });
        this.smallRectangleLayer.eachGraphic((graphicItem) => {
          if (graphicItem && graphicItem.name === params.area_type) {
            graphicItem.show = true;
          }
        });
        this.prohibitedCommunicationAreaLayer.eachGraphic((graphicItem) => {
          if (graphicItem && graphicItem.name === params.area_type) {
            graphicItem.show = true;
          }
        });
      },
    );

    this.$bus.on("setCircleAreaImg", (data: any) => {
      this.setCircleAreaImg(data);
    });

    this.$bus.on("setRectangleAreaImg", (data: any) => {
      this.setRectangleAreaImg(data);
    });

    // 切换矩形贴图显示/隐藏
    this.$bus.on("toggleRectangleImg", (show?: boolean) => {
      this.toggleRectangleImg(show);
    });

    this.$bus.on("addClusterPoint", (data: CommunicationArea[]) => {
      this.addClusterPoint(data);
    });

    // 添加中继聚类点
    this.$bus.on("addRelayClusterPoint", (data: CommunicationArea[]) => {
      this.addRelayClusterPoint(data);
    });

    // 添加中继站点
    this.$bus.on("addRelayStationImg", (center: any) => {
      this.addRelayStationImg(center);
    });

    this.$bus.on("setClusterPoint", (data: CommunicationArea[]) => {
      this.setClusterPoint(data);
    });

    this.$bus.on("setAreaPng", (data: any) => {
      this.setAreaPng(data);
    });
    this.$bus.on("clearAll", () => {
      this.graphicLayer.clear();
      this.cluster_point_layer.clear();
      this.smallRectangleLayer.clear();
      this.prohibitedCommunicationAreaLayer.clear();
      this.relay_cluster_point_layer.clear(); /// 中继聚类点图层
      this.relayRectangleLayer.clear(); /// 中继矩形通信区
    });

    // 添加二次绘制矩形区
    this.$bus.on("addSmallRectangleAreaImg", (data: any) => {
      this.addSmallRectanglePrimitive(data);
    });
    // 添加二次绘制圆形区
    this.$bus.on("addSmallCircleAreaImg", (data: any) => {
      this.addSmallCirclePrimitive(data);
    });

    // 切换二次绘制区域类型
    this.$bus.on("changeCommunicationAreaType", (type: string) => {
      this.changeCommunicationAreaType(type);
    });
    // 切换中继区域类型
    this.$bus.on("changeRelayCommunicationAreaType", (type: string) => {
      this.changeRelayCommunicationAreaType(type);
    });

    // 添加禁止通信区
    this.$bus.on("addProhibitedCommunicationAreaImg", (data: any) => {
      this.addProhibitedCommunicationAreaImg(data);
    });

    // 清理中继区域
    this.$bus.on("clearRelayArea", () => {
      this.relayRectangleLayer.clear(); /// 中继矩形通信区
      this.relay_cluster_point_layer.clear(); /// 中继聚类点图层
    });
    // 清理限制区域
    this.$bus.on("clearProhibitedArea", () => {
      this.prohibitedCommunicationAreaLayer.clear(); /// 限制矩形通信区
    });
  }
  /**
   * 设置通信区
   * @param data
   */
  setCommunicationArea(data: any) {
    let isHave = false;
    console.log("data", data);

    const initialLng = toLng(data.initialPointLng);
    const initialLat = toLat(data.initialPointLat);
    const destLng = toLng(data.destinationPointLng);
    const destLat = toLat(data.destinationPointLat);
    const centerLng = toLng(data.centerPointLng);
    const centerLat = toLat(data.centerPointLat);
    const radiusKm = Number(data.radius);
    const areaKind = data.activeName || data.area_type;

    if (data.activeName === "Rectangle" || data.activeName === "round") {
      this.graphicLayer.eachGraphic((graphicItem) => {
        if (graphicItem && graphicItem.name === data.activeName) {
          isHave = true;
          if (data.activeName === "Rectangle") {
            if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) return;
            graphicItem.setOptions({
              positions: [
                [initialLng, initialLat],
                [destLng, destLat],
              ],
            });
          } else if (data.activeName === "round") {
            if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) return;
            graphicItem.setOptions({
              position: [centerLng, centerLat],
              style: {
                radius: radiusKm * 1000,
              },
            });
          }
        }
      });
    } else if (
      data.area_type === "smallRectangle" ||
      data.area_type === "smallRound"
    ) {
      this.smallRectangleLayer.eachGraphic((graphicItem) => {
        console.log("graphicItem", graphicItem, data.area_type);
        if (graphicItem && graphicItem.name === data.area_type) {
          isHave = true;
          if (data.area_type === "smallRectangle") {
            if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) return;
            graphicItem.setOptions({
              positions: [
                [initialLng, initialLat],
                [destLng, destLat],
              ],
            });
          } else if (data.area_type === "smallRound") {
            if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) return;
            graphicItem.setOptions({
              position: [centerLng, centerLat],
              style: {
                radius: radiusKm * 1000,
              },
            });
          }
        }
      });
    } else if (
      data.area_type === "relayRectangle" ||
      data.area_type === "relayRound"
    ) {
      this.relayRectangleLayer.eachGraphic((graphicItem) => {
        console.log("graphicItem", graphicItem, data.area_type);
        if (graphicItem && graphicItem.name === data.area_type) {
          isHave = true;
          if (data.area_type === "relayRectangle") {
            if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) return;
            graphicItem.setOptions({
              positions: [
                [initialLng, initialLat],
                [destLng, destLat],
              ],
            });
          } else if (data.area_type === "relayRound") {
            if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) return;
            graphicItem.setOptions({
              position: [centerLng, centerLat],
              style: {
                radius: radiusKm * 1000,
              },
            });
          }
        }
      });
    }

    if (isHave) {
      return;
    }
    if (data) {
      switch (areaKind) {
        case "smallRectangle":
        case "Rectangle":
        case "relayRectangle":
          if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) break;
          const graphicRectangle = new mars3d.graphic.RectanglePrimitive({
            name: areaKind,
            positions: [
              [initialLng, initialLat],
              [destLng, destLat],
            ],
            style: {
              opacity: 0.4,
              clampToGround: true,
              color: "#02D4FD",
            },
            attr: { remark: "示例1" },
          });
          if (areaKind === "smallRectangle") {
            this.smallRectangleLayer.addGraphic(graphicRectangle);
          } else if (areaKind === "Rectangle") {
            this.graphicLayer.addGraphic(graphicRectangle);
          } else if (areaKind === "relayRectangle") {
            this.relayRectangleLayer.addGraphic(graphicRectangle);
          }
          break;
        case "smallRound":
        case "round":
        case "relayRound":
          if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) break;
          const graphicRound = new mars3d.graphic.CircleEntity({
            name: areaKind,
            position: new mars3d.LngLatPoint(centerLng, centerLat, 0),
            style: {
              radius: radiusKm,
              opacity: 0.4,
              clampToGround: true,
              color: "#02D4FD",
            },
            attr: { remark: "示例10" },
          });
          if (areaKind === "smallRound") {
            this.smallRectangleLayer.addGraphic(graphicRound);
          } else if (areaKind === "round") {
            this.graphicLayer.addGraphic(graphicRound);
          } else if (areaKind === "relayRound") {
            this.relayRectangleLayer.addGraphic(graphicRound);
          }
          break;
      }
    }
  }

  /**
   * 设置限制通信区
   * @param data
   */
  setProhibitedCommunicationArea(data: any) {
    let isHave = false;
    console.log("data", data);

    const initialLng = toLng(data.initialPointLng);
    const initialLat = toLat(data.initialPointLat);
    const destLng = toLng(data.destinationPointLng);
    const destLat = toLat(data.destinationPointLat);
    const centerLng = toLng(data.centerPointLng);
    const centerLat = toLat(data.centerPointLat);
    const radiusKm = Number(data.radius);
    const areaKind =
      data.activeName ||
      (data.activeProhibitedName === "Rectangle"
        ? "prohibitedRectangle"
        : data.activeProhibitedName === "Round"
          ? "prohibitedRound"
          : "");

    if (
      areaKind === "prohibitedRectangle" ||
      areaKind === "prohibitedRound"
    ) {
      this.prohibitedCommunicationAreaLayer.eachGraphic((graphicItem) => {
        if (graphicItem && graphicItem.name === areaKind) {
          isHave = true;
          if (areaKind === "prohibitedRectangle") {
            if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) return;
            graphicItem.setOptions({
              positions: [
                [initialLng, initialLat],
                [destLng, destLat],
              ],
            });
          } else if (areaKind === "prohibitedRound") {
            if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) return;
            graphicItem.setOptions({
              position: [centerLng, centerLat],
              style: {
                radius: radiusKm * 1000,
              },
            });
          }
        }
      });
    }

    if (isHave) {
      return;
    }
    if (data) {
      switch (areaKind) {
        case "prohibitedRectangle":
          if (!isValidLngLat(initialLng, initialLat) || !isValidLngLat(destLng, destLat)) break;
          const graphicRectangle = new mars3d.graphic.RectanglePrimitive({
            name: areaKind,
            positions: [
              [initialLng, initialLat],
              [destLng, destLat],
            ],
            style: {
              opacity: 0.4,
              clampToGround: true,
              color: "rgba(243, 42, 7, 0.2)",
            },
            attr: { remark: "示例1" },
          });
          this.prohibitedCommunicationAreaLayer.addGraphic(graphicRectangle);
          break;
        case "prohibitedRound":
          if (!isValidLngLat(centerLng, centerLat) || !Number.isFinite(radiusKm)) break;
          const graphicRound = new mars3d.graphic.CircleEntity({
            name: areaKind,
            position: new mars3d.LngLatPoint(
              centerLng,
              centerLat,
              0,
            ),
            style: {
              radius: radiusKm,
              opacity: 0.4,
              clampToGround: true,
              color: "rgba(243, 42, 7, 0.2)",
            },
            attr: { remark: "示例10" },
          });
          this.prohibitedCommunicationAreaLayer.addGraphic(graphicRound);
          break;
      }
    }
  }

  stopAreaDrawing() {
    this.graphicLayer.clearDrawing();
    this.graphicLayer.stopDraw();
    this.prohibitedCommunicationAreaLayer.clearDrawing();
    this.prohibitedCommunicationAreaLayer.stopDraw();
    this.smallRectangleLayer.clearDrawing();
    this.smallRectangleLayer.stopDraw();
    this.relayRectangleLayer.clearDrawing();
    this.relayRectangleLayer.stopDraw();
  }

  /**
   * 绘制通信区
   * @param type 绘制类型
   */
  async drawGraph(type: string) {
    // 限制区域清空
    this.prohibitedCommunicationAreaLayer.eachGraphic((graphicItem) => {
      if (
        type === "prohibitedRound" &&
        graphicItem.name === "prohibitedRound"
      ) {
        this.prohibitedCommunicationAreaLayer.removeGraphic(graphicItem);
      }
      if (
        type === "prohibitedRectangle" &&
        graphicItem.name === "prohibitedRectangle"
      ) {
        this.prohibitedCommunicationAreaLayer.removeGraphic(graphicItem);
      }
    });
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (!graphicItem) {
        return;
      }
      if (graphicItem && graphicItem.name === type) {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (type === "Rectangle" && graphicItem.name === "Rectangle") {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (type === "round" && graphicItem.name === "round") {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (type === "smallRound" && graphicItem.name === "smallRound") {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (type === "smallRectangle" && graphicItem.name === "smallRectangle") {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (
        type === "prohibitedRound" &&
        graphicItem.name === "prohibitedRound"
      ) {
        this.graphicLayer.removeGraphic(graphicItem);
      }
      if (
        type === "prohibitedRectangle" &&
        graphicItem.name === "prohibitedRectangle"
      ) {
        this.graphicLayer.removeGraphic(graphicItem);
      }
    });
    this.$bus.emit("mapPickMode", true);
    let cancelled = false;
    try {
      switch (type) {
        case "round":
        case "smallRound": {
          const graphic = await this.graphicLayer.startDraw({
            name: type,
            type: "circleP",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              opacity: 0.6,
              clampToGround: false,
              label: {
                text: "",
                ...MAP_LABEL_FONT,
                color: "#ffffff",
                distanceDisplayCondition: true,
                distanceDisplayCondition_far: 500000,
                distanceDisplayCondition_near: 0,
              },
            },
          });
          if (!graphic) {
            cancelled = true;
            break;
          }
          if (type === "round") {
            this.$bus.emit("drawCommunicationAreaMsg", graphic);
          }
          if (type === "smallRound") {
            this.$bus.emit("drawSmallCommunicationAreaMsg", graphic);
          }
          break;
        }
        case "Rectangle":
        case "smallRectangle": {
          const rectangle = await this.graphicLayer.startDraw({
            name: type,
            type: "rectangle",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              outline: true,
              opacity: 0.6,
              clampToGround: false,
              outlineWidth: 1,
              outlineColor: "#51D2D4",
            },
            success: (graphic) => {
              console.log("rectangle", graphic.toJSON());
              if (type === "Rectangle") {
                this.$bus.emit("drawCommunicationAreaMsg", graphic);
              }
              if (type === "smallRectangle") {
                this.$bus.emit("drawSmallCommunicationAreaMsg", graphic);
              }
            },
          });
          if (!rectangle) {
            cancelled = true;
          }
          break;
        }
        case "prohibitedRound": {
          const prohibitedGraphic =
            await this.prohibitedCommunicationAreaLayer.startDraw({
              name: type,
              type: "circleP",
              style: {
                color: "rgba(243, 42, 7, 0.2)",
                opacity: 0.6,
                clampToGround: false,
                label: {
                  text: "",
                  ...MAP_LABEL_FONT,
                  color: "#ffffff",
                  distanceDisplayCondition: true,
                  distanceDisplayCondition_far: 500000,
                  distanceDisplayCondition_near: 0,
                },
              },
            });
          if (!prohibitedGraphic) {
            cancelled = true;
            break;
          }
          this.$bus.emit("drawProhibitedCommunicationAreaMsg", prohibitedGraphic);
          break;
        }
        case "prohibitedRectangle": {
          const prohibitedRectangle =
            await this.prohibitedCommunicationAreaLayer.startDraw({
              name: type,
              type: "rectangle",
              style: {
                color: "rgba(243, 42, 7, 0.2)",
                outline: true,
                opacity: 0.6,
                clampToGround: false,
                outlineWidth: 1,
                outlineColor: "#d45151ff",
              },
              success: (graphic) => {
                console.log("rectangle", type, graphic.toJSON());
                if (type === "prohibitedRectangle") {
                  this.$bus.emit("drawProhibitedCommunicationAreaMsg", graphic);
                }
              },
            });
          if (!prohibitedRectangle) {
            cancelled = true;
          }
          break;
        }
        default:
          break;
      }
    } catch (_err) {
      cancelled = true;
    } finally {
      this.$bus.emit("mapPickMode", false);
      this.$bus.emit("drawCommunicationAreaEnd", { type, cancelled });
    }
  }

  /**
   * 显示通信区
   * @param name 通信区名称
   */
  showCommunicationArea(name: string) {
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem.name === name) {
        graphicItem.show = true;
      } else {
        graphicItem.show = false;
      }
    });
  }

  /**
   * 显示限制通信区
   * @param name 限制通信区名称
   */
  showProhibitedCommunicationArea(name: string) {
    console.log("showProhibitedCommunicationArea", name);

    this.prohibitedCommunicationAreaLayer.eachGraphic((graphicItem) => {
      if (graphicItem.name === name) {
        graphicItem.show = true;
      } else {
        graphicItem.show = false;
      }
    });
  }
  /**
   * 设置圆形通信区图片
   * @param data
   */
  setCircleAreaImg(data: any) {
    console.log("setCircleAreaImg", data);
    const existing: any[] = [];
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem?.name === "round") existing.push(graphicItem);
    });
    existing.forEach((graphicItem) => this.graphicLayer.removeGraphic(graphicItem));
    if (!data?.centerPoint || data.radius == null || !data.png_image_url) return;
    const graphic = new mars3d.graphic.CirclePrimitive({
      name: "round",
      position: new mars3d.LngLatPoint(
        data.centerPoint[0],
        data.centerPoint[1],
        700,
      ),
      style: {
        radius: data.radius * 1000,
        opacity: 0.6,
        image: data.png_image_url,
        clampToGround: true,
      },
      attr: { remark: "示例2" },
    });
    this.graphicLayer.addGraphic(graphic);
  }

  /**
   * 设置矩形通信区图片
   * @param data
   */
  setRectangleAreaImg(data: any) {
    console.log("setRectangleAreaImg", data);
    const existing: any[] = [];
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem?.name === "Rectangle") existing.push(graphicItem);
    });
    existing.forEach((graphicItem) => this.graphicLayer.removeGraphic(graphicItem));
    this.addRectanglePrimitive(data);
  }
  /**
   * 添加聚类点
   * @param data
   */
  addClusterPoint(data: any) {
    console.log("data", data);
    this.cluster_point_layer.clear();
    console.log("清理完毕", this.graphicLayer);

    (data || []).forEach((item: any, index: number) => {
      const lng = toLng(item.longitude ?? item.center_longitude);
      const lat = toLat(item.latitude ?? item.center_latitude);
      if (!isValidLngLat(lng, lat)) {
        console.warn("跳过无效聚类点坐标", item);
        return;
      }
      const graphicPoint = new mars3d.graphic.BillboardEntity({
        name: "cluster_point" + index,
        position: [lng, lat],
        style: {
          image: publicAsset("images/def2_point.png"),
          horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
          verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
          scale: 0.3,
          clampToGround: true,
          label: {
            text: item.name,
            ...MAP_LABEL_FONT,
            color: "#ffffff",
            outline: true,
            outlineColor: "#000000",
            pixelOffsetY: 20,
          },
        },
        attr: { remark: "聚类点" },
      });
      this.cluster_point_layer.addGraphic(graphicPoint);
    });
  }

  /**
   * 添加中继聚类点
   * @param data
   */
  addRelayClusterPoint(data: any) {
    this.relay_cluster_point_layer.clear();
    console.log("清理完毕", this.relay_cluster_point_layer);
    console.log("data", data);

    (data || []).forEach((item: any, index: number) => {
      const lng = toLng(item.longitude ?? item.center_longitude);
      const lat = toLat(item.latitude ?? item.center_latitude);
      if (!isValidLngLat(lng, lat)) {
        console.warn("跳过无效中继聚类点坐标", item);
        return;
      }
      const graphicPoint = new mars3d.graphic.BillboardEntity({
        name: "relay_cluster_point" + index,
        position: [lng, lat],
        style: {
          image: publicAsset("images/def2_point.png"),
          horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
          verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
          scale: 0.3,
          clampToGround: true,
          label: {
            text: item.name,
            ...MAP_LABEL_FONT,
            color: "#ffffff",
            outline: true,
            outlineColor: "#000000",
            pixelOffsetY: 20,
          },
        },
        attr: { remark: "聚类点" },
      });
      this.relay_cluster_point_layer.addGraphic(graphicPoint);
    });
  }

  /**
   * 添加中继站点图片
   * @param center 中继站点坐标
   */
  addRelayStationImg(center: any) {
    console.log("addRelayStationImg", center);
    this.relay_cluster_point_layer.clear();
    // 点矢量
    const graphicPoint = new mars3d.graphic.BillboardEntity({
      name: "relay_station",
      position: [center.center[0], center.center[1]],
      style: {
        image: publicAsset("images/def2_point.png"),
        horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
        verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
        scale: 0.3,
        clampToGround: true,
        label: {
          // 不需要文字时，去掉label配置即可
          text: "中继站点",
          ...MAP_LABEL_FONT,
          color: "#ffffff",
          outline: true,
          outlineColor: "#000000",
          pixelOffsetY: 20,
        },
      },
      attr: { remark: "中继站点" },
    });
    this.relay_cluster_point_layer.addGraphic(graphicPoint);
  }

  /**
   * 设置聚类点
   * @param data
   */
  setClusterPoint(data: any) {
    console.log("setClusterPoint", data);
    data.forEach((item: any, index: number) => {
      this.cluster_point_layer.eachGraphic((graphicItem) => {
        console.log("graphicItem", graphicItem.toJSON());

        if (graphicItem.name === "cluster_point" + index) {
          graphicItem.setOptions({
            style: {
              label: {
                text: item.name,
              },
            },
          });
        }
      });
    });
  }

  /**
   * 设置通信区图片
   * @param data
   */
  setAreaPng(data: any) {
    console.log("setAreaPng", data);
    const imageUrl = data.png_image_url || data.tif_image_url;
    const isCircle = data.type === "round" || data.type === "Round";
    if (isCircle) {
      this.setCircleAreaImg({
        ...data,
        png_image_url: imageUrl,
      });
      return;
    }
    this.setRectangleAreaImg({
      ...data,
      png_image_url: imageUrl,
    });
  }

  /**
   * 添加矩形通信区
   * @param data
   */
  addRectanglePrimitive(data: any) {
    console.log("addRectanglePrimitive", data);
    if (!data?.initialPoint || !data?.destinationPoint || !data.png_image_url) return;
    const graphic = new mars3d.graphic.RectanglePrimitive({
      name: "Rectangle",
      positions: [
        [data.initialPoint[0], data.initialPoint[1]],
        [data.destinationPoint[0], data.destinationPoint[1]],
      ],
      style: {
        height: 100,
        opacity: 0.6,
        image: data.png_image_url,
        clampToGround: true,
      },
      attr: { remark: "示例3" },
    });
    this.graphicLayer.addGraphic(graphic);
  }

  /**
   * 切换矩形/圆形损耗贴图显示/隐藏
   */
  toggleRectangleImg(show?: boolean) {
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && (graphicItem.name === "Rectangle" || graphicItem.name === "round")) {
        graphicItem.show = typeof show === "boolean" ? show : !graphicItem.show;
      }
    });
  }

  /**
   * 添加圆形通信区
   * @param data
   */
  addCirclePrimitive(data: any) {
    console.log("addCirclePrimitive", data);
    const graphic = new mars3d.graphic.CirclePrimitive({
      name: "round",
      position: new mars3d.LngLatPoint(data.center[0],data.center[1]),
      style: {
        radius: data.radius,
        opacity: 0.6,
        image: data.png_image_url,
        clampToGround: true,
      },
      attr: { remark: "示例2" },
    });
    console.log("graphic", graphic.toJSON());
    this.graphicLayer.addGraphic(graphic);
  }

  /**
   * 添加二次绘制矩形区
   * @param data
   */
  addSmallRectanglePrimitive(data: any) {
    console.log("addSmallRectanglePrimitive", data);
    const graphic = new mars3d.graphic.RectanglePrimitive({
      name: "smallRectangle",
      positions: [
        new mars3d.LngLatPoint(data.initialPoint[0], data.initialPoint[1], 700),
        new mars3d.LngLatPoint(
          data.destinationPoint[0],
          data.destinationPoint[1],
          700,
        ),
      ],
      style: {
        color: "rgba(81, 210, 212, 0.2)",
        outline: true,
        opacity: 0.6,
        clampToGround: true,
      },
      attr: { remark: "示例3" },
    });
    this.smallRectangleLayer.addGraphic(graphic);
  }
  /**
   * 添加二次绘制圆形区
   * @param data
   */
  addSmallCirclePrimitive(data: any) {
    console.log("addSmallCirclePrimitive", data);
    const graphic = new mars3d.graphic.CirclePrimitive({
      name: "smallRound",
      position: new mars3d.LngLatPoint(data.center[0], data.center[1], 700),
      style: {
        radius: data.radius,
        color: "rgba(81, 210, 212, 0.2)",
        outline: true,
        opacity: 0.6,
        clampToGround: true,
      },
      attr: { remark: "示例2" },
    });
    this.smallRectangleLayer.addGraphic(graphic);
  }

  /**
   * 添加禁止通信区图片
   * @param data
   */
  addProhibitedCommunicationAreaImg(data: any) {
    console.log("addProhibitedCommunicationAreaImg", data);
    if (data.type === "Round") {
      const graphic = new mars3d.graphic.CirclePrimitive({
        name: "Round",
        position: new mars3d.LngLatPoint(data.center[0], data.center[1], 700),
        style: {
          radius: data.radius,
          color: "rgba(243, 42, 7, 0.2)",
          outline: true,
          opacity: 0.6,
          clampToGround: true,
        },
        attr: { remark: "示例2" },
      });
      this.prohibitedCommunicationAreaLayer.addGraphic(graphic);
      // this.addRectanglePrimitive(data);
    } else if (data.type === "Rectangle") {
      const graphic = new mars3d.graphic.RectanglePrimitive({
        name: "Rectangle",
        positions: [
          new mars3d.LngLatPoint(
            data.initialPoint[0],
            data.initialPoint[1],
            700,
          ),
          new mars3d.LngLatPoint(
            data.destinationPoint[0],
            data.destinationPoint[1],
            700,
          ),
        ],
        style: {
          color: "rgba(243, 42, 7, 0.2)",
          outline: true,
          opacity: 0.6,
          clampToGround: true,
        },
        attr: { remark: "示例3" },
      });
      this.prohibitedCommunicationAreaLayer.addGraphic(graphic);
      // this.addCirclePrimitive(data);
    }
  }

  /**
   * 二次绘制通信区
   * @param name
   */
  async drawSmallGraph(type: string) {
    this.smallRectangleLayer.eachGraphic((graphicItem) => {
      if (!graphicItem) {
        return;
      }
      if (graphicItem && graphicItem.name === type) {
        this.smallRectangleLayer.removeGraphic(graphicItem);
      }
      if (type === "smallRound" && graphicItem.name === "smallRound") {
        this.smallRectangleLayer.removeGraphic(graphicItem);
      }
      if (type === "smallRectangle" && graphicItem.name === "smallRectangle") {
        this.smallRectangleLayer.removeGraphic(graphicItem);
      }
    });
    this.$bus.emit("mapPickMode", true);
    let cancelled = false;
    try {
      switch (type) {
        case "smallRound": {
          const graphic = await this.smallRectangleLayer.startDraw({
            name: type,
            type: "circleP",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              opacity: 0.6,
              clampToGround: false,
              label: {
                text: "",
                ...MAP_LABEL_FONT,
                color: "#ffffff",
                distanceDisplayCondition: true,
                distanceDisplayCondition_far: 500000,
                distanceDisplayCondition_near: 0,
              },
            },
          });
          if (!graphic) {
            cancelled = true;
            break;
          }
          this.$bus.emit("drawSmallCommunicationAreaMsg", graphic);
          break;
        }
        case "smallRectangle": {
          const rectangle = await this.smallRectangleLayer.startDraw({
            name: type,
            type: "rectangle",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              outline: true,
              opacity: 0.6,
              clampToGround: false,
              outlineWidth: 1,
              outlineColor: "#51D2D4",
            },
            success: (graphic) => {
              if (type === "smallRectangle") {
                this.$bus.emit("drawSmallCommunicationAreaMsg", graphic);
              }
            },
          });
          if (!rectangle) {
            cancelled = true;
          }
          break;
        }
        default:
          break;
      }
    } catch (_err) {
      cancelled = true;
    } finally {
      this.$bus.emit("mapPickMode", false);
      this.$bus.emit("drawCommunicationAreaEnd", { type, cancelled });
    }
  }

  /**
   * 绘制中继区域
   * @param type
   */
  async drawRelayGraph(type: string) {
    this.relayRectangleLayer.eachGraphic((graphicItem) => {
      if (!graphicItem) {
        return;
      }
      if (graphicItem && graphicItem.name === type) {
        this.relayRectangleLayer.removeGraphic(graphicItem);
      }
      if (type === "relayRound" && graphicItem.name === "relayRound") {
        this.relayRectangleLayer.removeGraphic(graphicItem);
      }
      if (type === "relayRectangle" && graphicItem.name === "relayRectangle") {
        this.relayRectangleLayer.removeGraphic(graphicItem);
      }
    });
    this.$bus.emit("mapPickMode", true);
    let cancelled = false;
    try {
      switch (type) {
        case "relayRound": {
          const graphic = await this.relayRectangleLayer.startDraw({
            name: type,
            type: "circleP",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              opacity: 0.6,
              clampToGround: false,
              label: {
                text: "",
                ...MAP_LABEL_FONT,
                color: "#ffffff",
                distanceDisplayCondition: true,
                distanceDisplayCondition_far: 500000,
                distanceDisplayCondition_near: 0,
              },
            },
          });
          if (!graphic) {
            cancelled = true;
            break;
          }
          this.$bus.emit("drawRelayCommunicationAreaMsg", graphic);
          break;
        }
        case "relayRectangle": {
          const rectangle = await this.relayRectangleLayer.startDraw({
            name: type,
            type: "rectangle",
            style: {
              color: "rgba(81, 210, 212, 0.2)",
              outline: true,
              opacity: 0.6,
              clampToGround: false,
              outlineWidth: 1,
              outlineColor: "#51D2D4",
            },
            success: (graphic) => {
              if (type === "relayRectangle") {
                this.$bus.emit("drawRelayCommunicationAreaMsg", graphic);
              }
            },
          });
          if (!rectangle) {
            cancelled = true;
          }
          break;
        }
        default:
          break;
      }
    } catch (_err) {
      cancelled = true;
    } finally {
      this.$bus.emit("mapPickMode", false);
      this.$bus.emit("drawCommunicationAreaEnd", { type, cancelled });
    }
  }

  /**
   * 切换二次绘制区域类型
   * @param type
   */
  changeCommunicationAreaType(type: string) {
    // this.currentCommunicationAreaType = type;
    console.log("changeCommunicationAreaType", this.smallRectangleLayer);

    this.smallRectangleLayer.eachGraphic((graphicItem) => {
      console.log(graphicItem, graphicItem.name, type);

      if (!graphicItem) {
        return;
      }

      if (graphicItem && graphicItem.name === type) {
        graphicItem.show = true;
      } else {
        graphicItem.show = false;
      }
    });
  }

  /**
   * 切换中继区域类型
   * @param type
   */
  changeRelayCommunicationAreaType(type: string) {
    // this.currentRelayCommunicationAreaType = type;
    console.log("changeRelayCommunicationAreaType", this.relayRectangleLayer);

    this.relayRectangleLayer.eachGraphic((graphicItem) => {
      console.log(graphicItem, graphicItem.name, type);

      if (!graphicItem) {
        return;
      }

      if (graphicItem && graphicItem.name === type) {
        graphicItem.show = true;
      } else {
        graphicItem.show = false;
      }
    });
  }
}
