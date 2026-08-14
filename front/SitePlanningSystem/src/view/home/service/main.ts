import { Map } from "mars3d";
import * as mars3d from "mars3d";

export default class Main {
  map: mars3d.Map;
  layers: mars3d.layer.GraphicLayer | null = null;

  constructor(map: Map) {
    this.map = map;
    
  }

  

  clearLayer() {
    if (this.layers) {
      this.map.removeLayer(this.layers, true);
      // console.log("清除数据！");
    }
  }
}
