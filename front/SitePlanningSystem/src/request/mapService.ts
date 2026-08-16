import service from "./request";

export type MapServiceType = "wms" | "wmts" | "xyz";

export interface MapTileServiceItem {
  id?: number;
  name: string;
  service_type: MapServiceType;
  url: string;
  layers?: string;
  format?: string;
  tile_matrix_set_id?: string;
  description?: string;
  enabled?: boolean;
  show_default?: boolean;
  sort_order?: number;
  created_at?: string;
  updated_at?: string;
}

export function listMapServices() {
  return service({
    url: "/projects/map-services/",
    method: "get",
    headers: { isToken: true },
  });
}

export function createMapService(data: MapTileServiceItem) {
  return service({
    url: "/projects/map-services/",
    method: "post",
    data,
    headers: { isToken: true },
  });
}

export function updateMapService(data: MapTileServiceItem) {
  return service({
    url: `/projects/map-services/${data.id}/`,
    method: "put",
    data,
    headers: { isToken: true },
  });
}

export function deleteMapService(id: number) {
  return service({
    url: `/projects/map-services/${id}/`,
    method: "delete",
    headers: { isToken: true },
  });
}
