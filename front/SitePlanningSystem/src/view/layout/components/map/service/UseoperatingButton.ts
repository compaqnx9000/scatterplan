import { Map } from "mars3d";
import * as mars3d from "mars3d";
import { map3dConfig } from "@/view/layout/components/map/config/config"
const Cesium = mars3d.Cesium;

interface Center {
  lng: number;
  lat: number;
  alt: number;
}

export class UseoperatingButton {
  map: mars3d.Map;

  constructor(map: Map) {
    this.map = map;
  }

  flyToCenter(center: Center) {
    this.map.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(center.lng, center.lat, center.alt),
      duration: 2, // 飞行时间，单位为秒
    });
  }

  handleCameraZoomIn(e: boolean) {
    if (e) {
      this.map.camera.zoomIn(10000);
    } else {
      this.map.camera.zoomOut(10000);
    }
  }

  selectMap(val:string) {
    map3dConfig.basemaps.forEach(item => {
      item.show = false
      if(item.name == val) {
        item.show = true
      }
    })
    this.map.setBasemapsOptions(map3dConfig.basemaps)
  }


  clearLayer() {}
}
