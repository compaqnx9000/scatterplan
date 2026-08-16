import { Map } from "mars3d";
import * as mars3d from "mars3d";
import { MAP_LABEL_FONT } from "@/view/home/service/mapLabelStyle";
const Cesium = mars3d.Cesium;
export class Tool {
  map: mars3d.Map;
  // 测量点位
  measure;
  // 绘制图层
  graphicLayer;
  constructor(map: Map) {
    if (!map) {
      throw new Error("map 实例不能为空");
    }
    this.map = map;
    this.graphicLayer = new mars3d.layer.GraphicLayer();
    map.addLayer(this.graphicLayer);
    this.measure = new mars3d.thing.Measure({
      label: {
        color: "#ffffff",
        ...MAP_LABEL_FONT,
        background: true,
      },
    });
    map.addThing(this.measure);

    // 绑定图层右键菜单
    this.bindLayerContextMenu();
  }

  // 面积测量
  area() {
    return this.measure.area({
      style: {
        clampToGround: true,
      },
    });
  }

  // 距离测量
  distance() {
    return this.measure.distance({
      style: {
        clampToGround: true,
      },
    });
  }

  // 绘制线条
  // 开始绘制
  async startDrawLine() {
    const graphic = await this.graphicLayer.startDraw({
      type: "polyline",
      // maxPointNum: 2, //可以限定最大点数，2个点绘制后自动结束
      // hasMidPoint: false,
      style: {
        color: "#55ff33",
        width: 3,
        clampToGround: true,
        label: {
          ...MAP_LABEL_FONT,
          color: "#ffffff",
          distanceDisplayCondition: true,
          distanceDisplayCondition_far: 500000,
          distanceDisplayCondition_near: 0,
        },
      },
    });
    console.log("标绘完成", graphic.toJSON());
  }

  // 绘制面
  async startDrawGraphic() {
    const graphic = await this.graphicLayer.startDraw({
      type: "polygon",
      style: {
        color: "#29cf34",
        clampToGround: true,
        opacity: 0.5,
        outline: true,
        outlineWidth: 3,
        outlineColor: "#ffffff",
        label: {
          // text: "我是火星科技",
          // font_size: 18,
          // color: "#ffffff",
          distanceDisplayCondition: true,
          distanceDisplayCondition_far: 500000,
          distanceDisplayCondition_near: 0,
        },
      },
    });
    // graphic.positions = mars3d.PointUtil.setPositionsHeight(graphic.positionsShow, 2000)
    console.log("标绘完成", graphic.toJSON());
  }

  // 绑定右键菜单
  bindLayerContextMenu() {
    this.graphicLayer.bindContextMenu([
      {
        text: "删除对象",
        icon: "fa fa-trash-o",
        show: (event) => {
          const graphic = event.graphic;
          if (
            !graphic ||
            graphic.isDestroy ||
            graphic.isPrivate ||
            graphic.graphicIds
          ) {
            return false;
          } else {
            return true;
          }
        },
        callback: (e) => {
          const graphic = e.graphic;
          if (!graphic) {
            return;
          }
          const parent = graphic.parent; // 右击是编辑点时
          this.graphicLayer.removeGraphic(graphic);
          if (parent) {
            this.graphicLayer.removeGraphic(parent);
          }
        },
      },
    ]);
  }

  clear() {
    this.measure.clear();
    this.graphicLayer.clear();
  }
  destroy() {
    this.map.removeLayer(this.graphicLayer);
    this.map.removeThing(this.measure);
  }
}
