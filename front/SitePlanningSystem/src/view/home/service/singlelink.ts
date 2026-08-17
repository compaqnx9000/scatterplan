import { position } from "html2canvas/dist/types/css/property-descriptors/position";
import * as mars3d from "mars3d";
import { MAP_LABEL_FONT } from "./mapLabelStyle";
import { publicAsset } from "./publicAsset";
/**
 * 单链路图层和矢量管理服务
 */
export default class SingleLinkService {
  map: mars3d.Map;
  graphicLayer: mars3d.layer.GraphicLayer;
  linkGraphics: mars3d.graphic.BaseGraphic[] = [];
  $bus: any;
  constructor(map: mars3d.Map, bus: any) {
    this.map = map;
    this.graphicLayer = new mars3d.layer.GraphicLayer();
    this.map.addLayer(this.graphicLayer);
    this.$bus = bus;

    this.$bus.on("drawPoint", (params: { type: string; name: string }) => {
      // this.clearLinkGraphics();
      this.drawPoint(params.type, params.name);
    });

    this.$bus.on("cancelDrawPoint", () => {
      this.graphicLayer.clearDrawing();
      this.graphicLayer.stopDraw();
      this.$bus.emit("mapPickMode", false);
    });

    // 设置点位信息
    this.$bus.on(
      "setLaunchSite",
      (params: { type: string; lng: number; lat: number; height: number }) => {
        this.setPoint(params.type, params.lng, params.lat, params.height);
      }
    );

    // 设置点位name
    this.$bus.on(
      "setLaunchSiteName",
      (params: { type: string; point_name: string }) => {
        this.setPointName(params.type, params.point_name);
      }
    );

    this.$bus.on("clearAll", () => {
      this.graphicLayer.clear();
    });

    // this.bindLayerContextMenu();
  }

  /**
   * 设置点位信息
   * @param name 点位名称
   * @param lng 经度
   * @param lat 纬度
   */
  setPoint(type: string, lng: number, lat: number, height: number): void {
    console.log("setPoint", type, lng, lat, height);
    let isHavePoint = false;
    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === type) {
        isHavePoint = true;
        console.log("setPoint", type, lng, lat, height);
        graphicItem.setOptions({
          position: {
            lng,
            lat,
            alt: height,
          },
        });
      }
    });
    console.log("isHavePoint", isHavePoint);

    // 点位不存在时，添加点位
    if (!isHavePoint) {
      this.addPoint(type, lng, lat);
    }
  }

  /**
   * 设置点位名称
   * @param type 点位类型
   * @param point_name 点位名称
   */
  setPointName(type: string, point_name: string): void {
    console.log("setPointName", type, point_name);
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
        image: publicAsset("images/start_point.png"),
        horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
        verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
        scale: 0.4,
        // 贴地
        clampToGround: true,
        label: {
          // 不需要文字时，去掉label配置即可
          text: "站点1",
          ...MAP_LABEL_FONT,
          color: "#ffffff",
          outline: true,
          outlineColor: "#000000",
          pixelOffsetY: 20,
        },
      },
      attr: { remark: "站点1" },
    });
    this.graphicLayer.addGraphic(billboard);
    this.addDragListener(billboard);
  }

  /**
   * 绘制点位
   * @param type 点位类型
   * @param formData 表单数据对象
   * @param dialogState 对话框状态对象
   * @returns 绘制的图形对象
   */
  async drawPoint(
    type: string,
    name: string
  ): Promise<mars3d.graphic.BaseGraphic | null> {
    // 移除同类型的已有图形

    this.graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === type) {
        this.graphicLayer.removeGraphic(graphicItem);
      }
    });

    this.$bus.emit("mapPickMode", true);

    try {
      // 开始绘制新的图形
      const graphic = await this.graphicLayer.startDraw({
        name: type,
        type: "billboard",
        style: {
          // clampToGround: true,
          horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
          verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
          scale: 0.4,
          clampToGround: true,
          label: {
            // 不需要文字时，去掉label配置即可
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
          image: publicAsset("images/start_point.png"),
        },
      });
      // 添加到图层
      this.graphicLayer.addGraphic(graphic);
      this.addDragListener(graphic);
      this.$bus.emit("drawPointMsg", graphic);
      this.$bus.emit("drawPointEnd", { type, cancelled: false });

      return graphic;
    } catch (_err) {
      // Esc / 右键等取消标绘
      this.$bus.emit("drawPointEnd", { type, cancelled: true });
      return null;
    } finally {
      this.$bus.emit("mapPickMode", false);
    }
  }

  /**
   * 添加拖拽监听
   * @param graphic 图形对象
   */
  addDragListener(graphic: mars3d.graphic.BaseGraphic): void {
    this.graphicLayer.startEditing(graphic);
    const that = this;
    graphic.on(mars3d.EventType.updatePosition, function (event: any) {
      const position = event.target.point;
      // 同步更新点位名称
      that.$bus.emit("changeSingleLinkPoint", position);
    });
  }

  /**
   * 销毁服务，清理资源
   */
  destroy(): void {
    if (this.graphicLayer) {
      this.graphicLayer.clear();
      this.map.removeLayer(this.graphicLayer, true);
    }
    this.linkGraphics = [];
  }
}
