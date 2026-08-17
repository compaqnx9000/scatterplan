import * as mars3d from "mars3d";
import { MAP_LABEL_FONT } from "./mapLabelStyle";
import { publicAsset } from "./publicAsset";

/**
 * 单链路计算接受点图层服务配置
 */
export default class SLPComputeService {
  map: mars3d.Map;
  graphicLayer: mars3d.layer.GraphicLayer;
  $bus: any;

  constructor(map: mars3d.Map, bus: any) {
    this.map = map;
    this.graphicLayer = new mars3d.layer.GraphicLayer({
      name: "单链路计算接受点",
    });
    this.$bus = bus;
    this.map.addLayer(this.graphicLayer);

    this.$bus.on(
      "setSLPCompute",
      (params: { type: string; lng: number; lat: number; height: number }) => {
        this.setPoint(params.type, params.lng, params.lat, params.height);
      }
    );

    this.$bus.on(
      "setSLPComputeName",
      (params: { type: string; point_name: string }) => {
        this.setPointName(params.type, params.point_name);
      }
    );

    this.$bus.on("drawSLPPoint", (params: { type: string; name: string }) => {
      // this.clearLinkGraphics();
      this.drawPoint(params.type, params.name);
    });

    this.$bus.on("cancelDrawPoint", () => {
      this.graphicLayer.clearDrawing();
      this.graphicLayer.stopDraw();
      this.$bus.emit("mapPickMode", false);
    });

    this.$bus.on("setSingleLink", (message: any) => {
      //   设置连接线
      this.setLink(message);
    });

    this.$bus.on("HideAllSLPCompute", () => {
      this.graphicLayer.eachGraphic((graphicItem) => {
        graphicItem.show = false;
      });
    });
    this.$bus.on("showAllSLPCompute", () => {
      this.graphicLayer.eachGraphic((graphicItem) => {
        graphicItem.show = true;
      });
    });
    this.$bus.on("clearAll", () => {
      //   this.graphicLayer.remove();
      this.graphicLayer.clear();
    });
  }

  /**
   * 设置计算接受点
   * @param type 类型
   * @param name 名称
   * @param lng 经度
   * @param lat 纬度
   * @param height 高度
   */
  setPoint(type: string, lng: number, lat: number, height: number): void {
    let isHavePoint = false;
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === type) {
        isHavePoint = true;
        graphicItem.setOptions({
          position: {
            lng,
            lat,
            alt: height,
          },
        });
      }
    });
    if (!isHavePoint) {
      this.addPoint(type, lng, lat);
    }
  }

  /**
   * 设置计算接受点名称
   */
  setPointName(type: string, point_name: string): void {
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === type) {
        graphicItem.setOptions({
          style: {
            label: {
              text: point_name,
            },
          },
        });
      }
    });
  }

  /**
   * 绘制计算接受点
   */
  async drawPoint(
    type: string,
    name: string
  ): Promise<mars3d.graphic.BaseGraphic | null> {
    console.log("drawPoint", type);
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === type) {
        this.graphicLayer.removeGraphic(graphicItem);
      }
    });

    this.$bus.emit("mapPickMode", true);

    try {
      const graphic = await this.graphicLayer.startDraw({
        name: type,
        type: "billboard",
        style: {
          horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
          verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
          scale: 0.4,
          clampToGround: true,
          label: {
            text: name,
            ...MAP_LABEL_FONT,
            color: "#ffffff",
            outline: true,
            outlineColor: "#000000",
            pixelOffsetY: 20,
          },
        },
      });

      if (!graphic) {
        this.$bus.emit("drawPointEnd", { type, cancelled: true });
        return null;
      }

      graphic.setOptions({
        style: {
          image: publicAsset("images/end_point.png"),
        },
      });
      this.graphicLayer.addGraphic(graphic);
      this.addDragListener(graphic);
      this.$bus.emit("drawSLPPointMsg", graphic);
      this.$bus.emit("drawPointEnd", { type, cancelled: false });
      return graphic;
    } catch (_err) {
      this.$bus.emit("drawPointEnd", { type, cancelled: true });
      return null;
    } finally {
      this.$bus.emit("mapPickMode", false);
    }
  }

  /**
   * 添加点位
   * @param type 点位类型
   * @param name 点位名称
   * @param lng 经度
   * @param lat 纬度
   * @param height 高度
   */
  addPoint(type: string, lng: number, lat: number): void {
    const billboard = new mars3d.graphic.BillboardEntity({
      name: type,
      position: [lng, lat],
      style: {
        image: publicAsset("images/end_point.png"),
        horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
        verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
        scale: 0.4,
        // 贴地
        clampToGround: true,
        label: {
          // 不需要文字时，去掉label配置即可
          text: "站点2",
          ...MAP_LABEL_FONT,
          color: "#ffffff",
          outline: true,
          outlineColor: "#000000",
          pixelOffsetY: 20,
        },
      },
      attr: { remark: "示例4" },
    });
    this.graphicLayer.addGraphic(billboard);
    this.addDragListener(billboard);
  }

  /**
   * 设置链路
   * @param message 链路数据
   */
  setLink(message: any): void {
    const toPos = (lng: unknown, lat: unknown, alt: unknown): [number, number, number] | null => {
      const x = Number(lng);
      const y = Number(lat);
      const z = Number(alt);
      if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
      return [x, y, Number.isFinite(z) ? z : 0];
    };

    const start = Array.isArray(message.startPoint)
      ? toPos(message.startPoint[0], message.startPoint[1], message.startPoint[2])
      : toPos(message.tx_lon, message.tx_lat, message.tx_height);
    const end = Array.isArray(message.endPoint)
      ? toPos(message.endPoint[0], message.endPoint[1], message.endPoint[2])
      : toPos(message.rx_lon, message.rx_lat, message.rx_height);
    const scatterer = toPos(message.scatterer_lon, message.scatterer_lat, message.scatterer_height);
    if (!start || !end || !scatterer) return;

    const graphics = [...this.graphicLayer.getGraphics()];
    graphics.forEach((graphicItem) => {
      if (graphicItem && graphicItem.name === "linkageCalculation") {
        this.graphicLayer.removeGraphic(graphicItem);
      }
    });

    const txRxLine = new mars3d.graphic.PolylineEntity({
      name: "linkageCalculation",
      positions: [start, end],
      style: {
        width: 2,
        clampToGround: false,
        materialType: mars3d.MaterialType.PolylineDash,
        materialOptions: {
          color: "#FFA21A",
        },
      },
      attr: { remark: "收发连线" },
    });

    const scattererPoint = new mars3d.graphic.PointEntity({
      name: "linkageCalculation",
      position: scatterer,
      style: {
        pixelSize: 10,
        color: "#FF391A",
        clampToGround: false,
        label: {
          text: "散射体",
          ...MAP_LABEL_FONT,
          color: "#ffffff",
          outline: true,
          outlineColor: "#000000",
          pixelOffsetY: -10,
        },
      },
      attr: { remark: "散射体" },
    });

    const txScattererLine = new mars3d.graphic.PolylineEntity({
      name: "linkageCalculation",
      positions: [start, scatterer],
      style: {
        width: 2,
        clampToGround: false,
        materialType: mars3d.MaterialType.Color,
        materialOptions: {
          color: "#FF391A",
        },
      },
      attr: { remark: "发射点-散射体" },
    });

    const scattererRxLine = new mars3d.graphic.PolylineEntity({
      name: "linkageCalculation",
      positions: [end, scatterer],
      style: {
        width: 2,
        clampToGround: false,
        materialType: mars3d.MaterialType.Color,
        materialOptions: {
          color: "#FF391A",
        },
      },
      attr: { remark: "散射体-接收点" },
    });

    this.graphicLayer.addGraphic(txScattererLine);
    this.graphicLayer.addGraphic(scattererRxLine);
    this.graphicLayer.addGraphic(scattererPoint);
    this.graphicLayer.addGraphic(txRxLine);
  }

  /**
     * 添加拖拽监听
     * @param graphic 图形对象
     */
    addDragListener(graphic: mars3d.graphic.BaseGraphic): void {
      this.graphicLayer.startEditing(graphic);
      const that = this
      graphic.on(mars3d.EventType.updatePosition, function (event: any) {
        const position = event.target.point;
        // 同步更新点位名称
        that.$bus.emit("changeSLPPoint", position);
      });
    }
}
