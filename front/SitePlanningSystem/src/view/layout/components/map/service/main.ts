import { Map } from "mars3d";
import * as turf from "@turf/turf";
import { useRouter } from "vue-router";
import * as mars3d from "mars3d";
import nanChang from "../config/nanChang.json";
import $store from "@/store/index";
let qxsyUrl = import.meta.env.VITE_APP_QXSY_url;
let geoserverUrl = import.meta.env.VITE_APP_GEOSERVER_url;
import { useWebSocket } from "./websocketService";
import refreshToken from "@/request/refreshToken";
import { ElMessage } from "element-plus";

const Cesium = mars3d.Cesium;

// 定义事件参数的类型
// interface ManageLayerEvent {
//     layerName: string;
//     shouldAdd: boolean;
//     wmsUrl: string;
//     layersParam: string;
// }

export class main {
  map: Map;
  $bus: any;
  router = useRouter();
  // layers: { [layerName: string]: mars3d.layer.WmsLayer } = {}
  layersQXSY: mars3d.layer.TilesetLayer | null = null;
  isLayersQXSY: boolean;
  hgtQXSY: mars3d.layer.WmtsLayer | null = null;
  // 当前根页面-用于地图调整页面时判断是否为所需模块
  rootPagePath = "";
  $store: any;
  wsService: any;
  imageryLayers: mars3d.layer.GraphicLayer | null = null;
  constructor(map: Map, $bus: any, $store: any) {
    this.map = map;
    this.$bus = $bus;
    this.isLayersQXSY = false;
    this.$store = $store;

    this.imageryLayers = new mars3d.layer.GraphicLayer({
      name: "imageryLayers",
      show: false,
    });
    this.map.addLayer(this.imageryLayers);

    // 添加瓦片
// const wmtsMap = new mars3d.layer.WmtsLayer({
//     url: "http://192.100.30.16:8088/earthview/rest/services/tileserver/wmts",
//     layer: "sfsj",
//     style: "default",
//     crs: mars3d.CRS.EPSG4326,
//     tileMatrixSetID: "EPSG:4326",
//     format: "image/png",
//     // tileMatrixLabels:Array.from({ length: 11},(_,i)=>i.toString()),

//     // minimumLevel:0,
//     // maximumLevel:19,
//     // minimumTerrainLevel:9,
//     // maximumTerrainLevel:17,
//     queryParameters: {
//         serviceNmae: "sfsj",
//         token: "undefined"
//     },
//     enablePickFeatures: true,
// })
// map.addLayer(wmtsMap);
    // 添加路网
    // 添加 GeoServer WMS 图层
    // const geoserverWMS = new Cesium.WebMapServiceImageryProvider({
    //   url: "http://localhost:8080/geoserver/zero/wms", // 替换为你的 GeoServer 地址
    //   layers: "zero:DanDong", // 图层名称（工作区:图层）
    //   parameters: { service: "WMS", version: "1.1.1", // WMS 版本
    //   format: "image/png", // 输出格式
    //   transparent: true, // 允许透明
    //   srs: "EPSG:4326", // 坐标系（WGS84，与 Cesium 默认坐标系一致） },
    //   enablePickFeatures: true, // 允许点击获取要素信息
    // })
    const tileLayer = new mars3d.layer.WmsLayer({
      name: "路网",
      url: "/geoserver/zk/wms",
      // url: "/geoserver/zero/wms",
      layers: "zk:china_roadnet2",
      show: false,
      parameters: {
        service: "WMS", // 必选：指定服务类型
        version: "1.1.1", // 必选：与 GeoServer 支持的版本一致
        transparent: true,
        format: "image/png",
      },
      getFeatureInfoParameters: {
        feature_count: 10,
      },
      // 单击高亮及其样式
      highlight: {
        type: "wallP",
        diffHeight: 100,
        materialType: mars3d.MaterialType.LineFlow,
        materialOptions: {
          // image: "https://data.mars3d.cn/img/textures/fence.png",
          color: "#ffff00",
          speed: 10, // 速度，建议取值范围1-100
          axisY: true,
        },
      },
      // featureToGraphic: (feature, event) => {
      //   const data = feature.data;
      //   console.log("featureToGraphic", data);

      //   // 自行加解析data的代码，下面是测试演示
      //   const attr = {};
      //   attr["名称"] = "皇岗村文化广场及音乐喷水泉";
      //   attr["街道名称"] = "福田街道";
      //   attr["社区名称"] = "皇岗社区";

      //   // 返回graphic对应的构造参数
      //   return {
      //     type: "point",
      //     position: event.cartesian,
      //     style: {
      //       color: "#ff0000",
      //       pixelSize: 10,
      //       outlineColor: "#ffffff",
      //       outlineWidth: 2,
      //     },
      //     attr,
      //   };
      // },
      // popup: "all",
    });
    map.addLayer(tileLayer);

    // 将 WMS 图层添加到地图
    // this.imageryLayers.addImageryProvider(geoserverWMS);
    // this.map.addLayer(roadLayer);
    // $bus.on("demo1", (res: string) => {
    // console.log("接收事件总线指令", res)
    // })
    // $bus.on('manageLayer', (e: ManageLayerEvent) => {
    //     console.log(e);
    //     this.manageLayer(e.layerName, e.shouldAdd, e.layersParam, e.wmsUrl);
    // })
    const show3Dtitles = this.$store.getters.getIsShowMoudle;
    this.isLayersQXSY = show3Dtitles ? show3Dtitles : false;
    $bus.on("manageQXSY", () => {
      // this.flyToQXSY()
      this.isLayersQXSY = !this.isLayersQXSY;
      this.$store.commit("SET_MOUDEL", this.isLayersQXSY);
      if (this.layersQXSY) {
        this.layersQXSY.show = this.isLayersQXSY;
        if (this.isLayersQXSY) {
          // this.flyToQXSY()
        }
      } else {
        this.initQXSY();
      }
    });
    $bus.on("refreshQXSY", () => {
      this.refreshQXSY();
    });
    $bus.on("isShowHgtQXSY", (e: boolean) => {
      this.handleIsHgtQXSTY(e);
    });
    $bus.on("isShowQXSY", (e: boolean) => {
      this.handleIsLayersQXSY(e);
    });
    $bus.on("setMapCamera", (cameraData: any) => {
      this.setMapCamera(cameraData);
    });

    // 监听websocket发送消息
    $bus.on("sendMessage", (message: any) => {
      this.sendMessage(message);
    });
    // 监听设置路网图层显示
    $bus.on("setMapLayerShow", (e: any) => {
      this.setMapLayerShow(e);
    });

    // 飞行到
    //锁定相机
    $bus.on("SpaceCameraController", () => {
      //   alert("视角锁定");
      // 同时禁用旋转和缩放
      const cameraController = map.viewer.scene.screenSpaceCameraController;

      // 禁用旋转
      cameraController.enableRotate = false;

      // 禁用缩放（核心设置）
      cameraController.enableZoom = false;
    });
    //恢复相机
    $bus.on("openCameraController", () => {
      //   alert("视角锁定");
      // 同时禁用旋转和缩放
      const cameraController = map.viewer.scene.screenSpaceCameraController;

      // 禁用旋转
      cameraController.enableRotate = true;

      // 禁用缩放（核心设置）
      cameraController.enableZoom = true;
    });

    // 初始化页面自动调整功能
    // this.mapMatchingRoute()
    // 初始化倾斜摄影
    // this.initQXSY()
    // 添加电子围栏功能
    // this.addElectronicFence();
    // 添加地图影像
    // this.setWMSParams();

    // 初始化长连接
    this.initWebSocket();
    // 展示开场动画
    setTimeout(() => {
      this.openFlyAnimation();
    }, 1000);
  }

  // 设置地图图层显示
  setMapLayerShow(e: any) {
    const { name, show } = e;

    console.log(name, show, Boolean(show));

    this.map.eachLayer((layer: any) => {
      if (layer.name === name) {
        layer.show = show;
      }
    });
  }

  // 展示开场动画
  async openFlyAnimation() {
    // this.map.setCameraView(
    //     { "lat": 27.307725, "lng": 115.921197, "alt": 104673.4, "heading": 358.5, "pitch": -37.1 },
    //     {
    //         duration: 5,
    //         pitchAdjustHeight:10000,//如果相机飞得比这个值高，在飞行过程中自动调整俯仰以向下看，并保持地球在视口。过低就不生效了
    //     })
    await this.map.openFlyAnimation({
      center: {
        // lat: 27.307725,
        // lng: 115.921197,
        // alt: 104673.4,
        // heading: 358.5,
        // pitch: -37.1,
        lat: 37.144573,
        lng: 105.538571,
        alt: 5189361.1,
        heading: 359.6,
        pitch: -89.5,
      },
    });
    this.setRoute();
    // console.log('飞行完成，意味地图完成加载');
    this.$bus.emit("mapFlyOver");

    $store.commit("setMapAddStatus", true);
  }
  async initWebSocket() {
    // 在组件中导入
    const token = localStorage.getItem("userToken");

    const response = await fetch("/Config/config.json"); // 根路径直接访问
    if (!response.ok) throw new Error("配置文件加载失败");
    const config = await response.json();
    console.log("public 配置变量：", config);
    // 在setup中使用
    console.log(
      "长连接地址",
      config.VITE_APP_WS_url + "?token=" + token
    );

    this.wsService = useWebSocket({
      url: config.VITE_APP_WS_url + "?token=" + token,
      heartbeatInterval: 30000, // 30秒一次心跳
      reconnectInterval: 3000, // 3秒后尝试重连
      maxReconnectAttempts: Infinity,
    });

    // 监听连接打开
    this.wsService.onOpen(() => {
      console.log("WebSocket连接已打开");

      // 连接成功后可以发送初始化消息
      // wsService.send({
      //   type: 'init',
      //   data: { userId: '123456' }
      // });
    });

    // 退出登录后断开 WS，并清掉地球上的绘制
    this.$bus.on("Logout", () => {
      this.$bus.emit("cancelDrawPoint");
      this.$bus.emit("mapPickMode", false);
      this.$bus.emit("clearAll");
      if (this.imageryLayers) {
        this.imageryLayers.clear();
      }
      if (this.map && typeof (this.map as any).flyHome === "function") {
        (this.map as any).flyHome({ duration: 1.2 });
      }
      if (this.wsService) {
        this.wsService.close(1000, "用户主动断开连接");
      }
    });
    this.$bus.on("wsReconnect", () => {
      this.wsService?.ensureConnected?.();
    });
    // 监听消息接收
    this.wsService.onMessage((message: any) => {
      console.log("收到消息:", message);
      if (message.type === "error") {
        const text = typeof message.message === "string" ? message.message : "";
        if (text.includes("中止")) {
          if (message.task_id && $store.state.taskId && String(message.task_id) !== String($store.state.taskId)) {
            return;
          }
          this.$bus.emit("stopProgress", { task_id: message.task_id });
          ElMessage.warning(text);
          return;
        }
        this.$bus.emit("clusterAnalysisFailure");
        this.$bus.emit("closeLoading");

        const errText =
          typeof message.message === "string"
            ? message.message
            : typeof message.error === "string"
              ? message.error
              : "计算失败，请重试";
        ElMessage.error(errText);
        return;
      } else if (message.error) {
        this.$bus.emit("clusterAnalysisFailure");
        this.$bus.emit("closeLoading");

        ElMessage.error(typeof message.error === "string" ? message.error : "计算失败，请重试");
        return;
      }
      // 根据消息类型处理
      switch (message.type) {
        case "singlelink":
          // 处理通知消息

          const data = {
            id: message.id,
            distance: message.distance,
            median_loss: message.median_loss,
            residual_value: message.residual_value,
            reliability: message.reliability,
            tx_theta: message.tx_theta,
            rx_theta: message.rx_theta,
            tx_azimuth: message.tx_azimuth,
            rx_azimuth: message.rx_azimuth,
            theta_scatter: message.theta_scatter,
            recv_power: message.recv_power,
            area: message.area,
            image_url: message.image_url,
            elapsed: message.elapsed,
            scatterer_lon: message.scatterer_lon,
            scatterer_lat: message.scatterer_lat,
            scatterer_height: message.scatterer_height,
            comm_rate: message.comm_rate,
            rx_barrier_distance: message.rx_barrier_distance,
            tx_barrier_distance: message.tx_barrier_distance,
            tx_barrier_height: message.tx_barrier_height,
            rx_barrier_height: message.rx_barrier_height,
            tx_height: message.tx_height,
            rx_height: message.rx_height,
            max_height: message.max_height,
            min_height: message.min_height,
            profile_samples: message.profile_samples || [],
            scatterer_distance: message.scatterer_distance,
            tx_barrier_elev: message.tx_barrier_elev,
            rx_barrier_elev: message.rx_barrier_elev,
          };

          this.$bus.emit("singlelink", data);
          break;
        case "task_started":
          // 任务开始
          $store.commit("setTaskId", message.task_id);
          this.$bus.emit("taskStarted", message.task_id);
          break;
        case "task_stop_requested":
          // 任务停止
          this.$bus.emit("stopProgress", { task_id: message.task_id });
          break;
        case "singlelink progress":
          this.$bus.emit("singlelinkProgress", {
            progress: message.progress,
            task_id: message.task_id,
          });
          break;
        case "coverage progress":
          this.$bus.emit("coverageProgress", {
            progress: message.progress,
            task_id: message.task_id,
          });
          break;
        case "circle area":
          this.$bus.emit("circleArea", {
            id: message.id,
            png_image_url: message.png_image_url,
            tif_image_url: message.tif_image_url,
            task_id: message.task_id,
          });
          break;
        case "rectangle area":
          this.$bus.emit("rectangleArea", {
            id: message.id,
            png_image_url: message.png_image_url,
            tif_image_url: message.tif_image_url,
            task_id: message.task_id,
          });
          break;
        case "rectangle area clustering":
        case "circle area clustering":
          //  推荐站点计算结果
          this.$bus.emit("rectangleAreaClustering", {
            stations: message.stations,
            calculation_duration: message.calculation_duration,
            stations_type: message.stations_type,
          });
          this.$bus.emit("closeLoading");
          break;
        case "dataUpdate":
          // 处理数据更新
          break;
        // 其他消息类型...
      }
    });

    // 监听连接关闭
    this.wsService.onClose(async (code: any, reason: any) => {
      // 刷新 token
      await refreshToken();
      console.log(`WebSocket关闭: ${code} - ${reason}`);

      // 刷新 token
    });

    // 监听错误
    this.wsService.onError((error: any) => {
      console.error("WebSocket错误:", error);
    });
  }
  // 发送消息的示例方法
  sendMessage = (message: any) => {
    this.wsService.send({
      type: "singlelink",
      ...message,
    });
  };
  // 设置当前页面根路径
  setPageRootRoute(path: any) {
    // console.log(to.matched[0].path);
    this.rootPagePath = path;
  }

  // 设置地图飞行到指定位置
  setMapCamera(cameraData: any) {
    this.map.setCameraView(cameraData.center);
  }
  // 通过地图位置调整路由
  mapMatchingRoute() {
    // 鼠标滚轮事件
    // this.map.on("wheel", this.setRoute.bind(this))
    // 镜头移动结束事件
    // this.map.on("cameraMoveEnd", this.setRoute.bind(this))
  }
  setRoute() {
    if (this.rootPagePath != "/attractInvestment") {
      return;
    }
    // 屏幕范围经纬度
    let winExtent = this.map.getExtent();
    // console.log(winExtent);

    // 视角高度
    let cameraHeight = this.map.getCameraView().alt;

    // 屏幕范围区域
    let turfExtentData = turf.polygon([
      [
        [winExtent.xmax, winExtent.ymin],
        [winExtent.xmax, winExtent.ymax],
        [winExtent.xmin, winExtent.ymax],
        [winExtent.xmin, winExtent.ymin],
        [winExtent.xmax, winExtent.ymin],
      ],
    ]);

    // 区级范围匹配
    let districtPolygon = turf.polygon([
      [
        [115.67462, 28.451526],
        [115.67462, 28.774593],
        [115.886033, 28.774593],
        [115.886033, 28.451526],
        [115.67462, 28.451526],
      ],
    ]);
    // 区级范围匹配
    if (turf.booleanContains(turfExtentData, districtPolygon)) {
      this.router.push({
        path: "/attractInvestment/HongGuTan",
      });
      // // 无法看到全市
      // if (cameraHeight > 35000) {
      //     this.router.push({
      //         path: '/attractInvestment/HongGuTan'
      //     })
      // } else {
      //     this.router.push({
      //         path: '/attractInvestment/keyAreas'
      //     })
      // }
    }
    // // 市级范围区域
    let marketBoundary = turf.polygon([
      [
        [115.398037, 28.226198],
        [115.398037, 29.076391],
        [116.615309, 29.076391],
        [116.615309, 28.226198],
        [115.398037, 28.226198],
      ],
    ]);

    if (turf.booleanContains(turfExtentData, marketBoundary)) {
      this.router.push({
        path: "/attractInvestment/NanChangShi",
      });
    }
  }
  /**
   * params(layerName:图层名称，shouldAdd:勾选或者移除,wms:地图服务地址）
   * 图层管理
   * */
  // manageLayer(layerName: string, shouldAdd: boolean, layersParam: string, wmsUrl: string = '/geoserver/nanchang/wms') {
  //     if (shouldAdd) {
  //         this.addLayer(layerName, wmsUrl, layersParam);
  //     } else {
  //         this.removeLayer(layerName);
  //     }
  // }

  // addLayer(layerName: string, wmsUrl: string, layersParam: string) {
  //     console.log(wmsUrl);
  //     const wmsLayer = new mars3d.layer.WmsLayer({
  //         name: layerName,
  //         url: wmsUrl,
  //         layers: layersParam,
  //         parameters: {
  //             transparent: true,
  //             format: "image/png"
  //         },
  //         show: true,
  //         popup: "all",
  //         flyTo: true
  //     });
  //     this.map.addLayer(wmsLayer);
  //     this.layers[layerName] = wmsLayer; // 使用普通对象存储图层
  //     console.log(`已添加 WMS 图层: ${layerName}`);
  // }

  // // 移除指定名称的图层
  // removeLayer(layerName: string) {
  //     const layer = this.layers[layerName];
  //     if (layer) {
  //         this.map.removeLayer(layer);
  //         delete this.layers[layerName];
  //         console.log(`成功移除图层: ${layerName}`);
  //         return true;
  //     }
  //     console.log(`未找到指定图层: ${layerName}`);
  //     return false;
  // }

  initQXSY() {
    this.layersQXSY = new mars3d.layer.TilesetLayer({
      name: "layer区域",
      url: qxsyUrl + "/rts3d/nc_smjd_trb/tileset.json",
      maximumScreenSpaceError: 16,
      maximumMemoryUsage: 1024, // 最大缓存内存大小(MB)
      cullWithChildrenBounds: false,
      skipLevelOfDetail: true,
      preferLeaves: true,
      allowDrillPick: true,
      show: this.isLayersQXSY,
      // clampToGround:true,//设置贴地
      queryParameters: {
        // 可以传自定义url参数，如token等
      },
      clip: {
        area: [
          {
            positions: [
              [115.790707, 28.551067, 28.9],
              [115.790674, 28.550672, 26.9],
              [115.800944, 28.550397, 6],
              [115.800869, 28.550861, 6],
              [115.795119, 28.551037, 19.7],
              [115.790643, 28.551092, 28.6],
            ],
          },
        ],
      },
    });
    this.map.addLayer(this.layersQXSY);
    this.layersQXSY.readyPromise
      .then(function (layer) {
        console.log("倾斜摄影加载完成", layer);
      })
      .catch(function (error) {
        console.error("倾斜摄影加载失败", error);
      });
  }

  refreshQXSY() {
    if (this.layersQXSY) {
      this.layersQXSY.destroy();
      this.layersQXSY = null;
      console.log("刷新倾斜摄影数据，重新加载！");
      this.initQXSY();
    }
  }

  flyToQXSY() {
    if (this.layersQXSY) {
      try {
        const boundingSphere = this.layersQXSY.boundingSphere;
        if (boundingSphere) {
          const cartographic = Cesium.Cartographic.fromCartesian(
            boundingSphere.center
          );
          const longitude = Cesium.Math.toDegrees(cartographic.longitude);
          const latitude = Cesium.Math.toDegrees(cartographic.latitude);
          const height = cartographic.height;
          this.map.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(
              longitude,
              latitude,
              3000
            ),
            duration: 2, // 飞行时间，单位为秒
          });
        }
      } catch (error) {
        console.error("flyTo 方法调用出错:", error);
      }
    }
  }

  handleIsLayersQXSY(flag: boolean) {
    if (this.layersQXSY) {
      this.layersQXSY.show = flag;
    }
  }
  handleIsHgtQXSTY(flag: boolean) {
    if (this.hgtQXSY) {
      this.hgtQXSY.show = flag;
    }
  }

  // 添加电子围栏
  addElectronicFence() {
    // geojson 合肥边界线
    const geoJsonLayer = new mars3d.layer.GeoJsonLayer({
      // url: "https://data.mars3d.cn/file/geojson/areas/340100.json",
      mask: true, // 标识为遮罩层【重点参数】
      data: nanChang,
      symbol: {
        styleOptions: {
          fill: true,
          color: "#57FFF9",
          opacity: 0.2,
          outline: true,
          outlineColor: "#57FFF9",
          outlineWidth: 1,
          outlineOpacity: 0.8,
          arcType: Cesium.ArcType.GEODESIC,
          // global: false, // 是否全球遮罩，false时为中国区域
          clampToGround: true,
        },
      },
      // flyTo: true
    });
    this.map.addLayer(geoJsonLayer);
  }
  // 加载影响
  setWMSParams() {
    let _this = this;
    let rightWMSParams = {
      url: geoserverUrl + "geoserver/gwc/service/wmts",
      layer: "nanchang:nc_hgt_2025Q1_v1",
      show: true,
      format: "image/png",
      tileMatrixSetID: "EPSG:4326",
      crs: mars3d.CRS.EPSG4326,
      minimumLevel: 0,
      maximumLevel: 18,
      minimumTerrainLevel: 0,
      maximumTerrainLevel: 18,
      pickFeaturesUrl: geoserverUrl + "geoserver/nanchang/wms",
      enablePickFeatures: true,
      rectangle: {
        xmax: 115.876585,
        xmin: 115.666741,
        ymax: 28.76303,
        ymin: 28.351688,
      },
    };

    this.hgtQXSY = new mars3d.layer.WmtsLayer(rightWMSParams);
    this.map.addLayer(this.hgtQXSY);
  }

  clearLayerQXSY() {
    if (this.layersQXSY) {
      this.map.removeLayer(this.layersQXSY, true);
      console.log("清除数据！");
    }
  }
}
