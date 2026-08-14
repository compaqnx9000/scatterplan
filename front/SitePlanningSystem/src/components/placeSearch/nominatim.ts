export type PlaceHit = {
  place_id: number;
  title: string;
  subtitle: string;
  lng: number;
  lat: number;
  xmin: number;
  xmax: number;
  ymin: number;
  ymax: number;
};

type NominatimItem = {
  place_id: number;
  display_name: string;
  name?: string;
  lon: string;
  lat: string;
  boundingbox?: [string, string, string, string];
};

type PhotonFeature = {
  geometry?: { coordinates?: number[] };
  properties?: {
    osm_id?: number;
    name?: string;
    country?: string;
    state?: string;
    city?: string;
    district?: string;
    extent?: number[];
  };
};

const NOMINATIM_URL = import.meta.env.DEV
  ? "/nominatim/search"
  : "https://nominatim.openstreetmap.org/search";

const splitDisplayName = (displayName: string, name?: string) => {
  const parts = displayName.split(",").map((s) => s.trim()).filter(Boolean);
  const title = name || parts[0] || displayName;
  const subtitle = parts.filter((p) => p !== title).join(" · ");
  return { title, subtitle };
};

async function searchNominatim(query: string, signal?: AbortSignal): Promise<PlaceHit[]> {
  const url = new URL(NOMINATIM_URL, window.location.origin);
  url.searchParams.set("q", query);
  url.searchParams.set("format", "json");
  url.searchParams.set("limit", "6");
  url.searchParams.set("addressdetails", "0");
  url.searchParams.set("accept-language", "zh-CN");

  const res = await fetch(url.toString(), {
    method: "GET",
    signal,
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Nominatim ${res.status}`);

  const data = (await res.json()) as NominatimItem[];
  if (!Array.isArray(data)) return [];

  return data.map((item) => {
    const { title, subtitle } = splitDisplayName(item.display_name, item.name);
    const south = Number(item.boundingbox?.[0]);
    const north = Number(item.boundingbox?.[1]);
    const west = Number(item.boundingbox?.[2]);
    const east = Number(item.boundingbox?.[3]);
    return {
      place_id: item.place_id,
      title,
      subtitle,
      lng: Number(item.lon),
      lat: Number(item.lat),
      xmin: Number.isFinite(west) ? west : Number(item.lon),
      xmax: Number.isFinite(east) ? east : Number(item.lon),
      ymin: Number.isFinite(south) ? south : Number(item.lat),
      ymax: Number.isFinite(north) ? north : Number(item.lat),
    };
  });
}

async function searchPhoton(query: string, signal?: AbortSignal): Promise<PlaceHit[]> {
  const url = new URL("https://photon.komoot.io/api/");
  url.searchParams.set("q", query);
  url.searchParams.set("lang", "zh");
  url.searchParams.set("limit", "6");

  const res = await fetch(url.toString(), { method: "GET", signal });
  if (!res.ok) throw new Error(`Photon ${res.status}`);

  const data = (await res.json()) as { features?: PhotonFeature[] };
  const features = Array.isArray(data?.features) ? data.features : [];

  return features
    .map((feature, index) => {
      const coords = feature.geometry?.coordinates || [];
      const lng = Number(coords[0]);
      const lat = Number(coords[1]);
      if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null;
      const props = feature.properties || {};
      const subtitle = [props.city, props.state, props.country].filter(Boolean).join(" · ");
      const extent = props.extent || [];
      return {
        place_id: Number(props.osm_id) || index,
        title: props.name || query,
        subtitle,
        lng,
        lat,
        xmin: Number.isFinite(extent[0]) ? extent[0] : lng,
        xmax: Number.isFinite(extent[1]) ? extent[1] : lng,
        ymin: Number.isFinite(extent[2]) ? extent[2] : lat,
        ymax: Number.isFinite(extent[3]) ? extent[3] : lat,
      } as PlaceHit;
    })
    .filter((item): item is PlaceHit => !!item);
}

export async function searchPlaces(query: string, signal?: AbortSignal): Promise<PlaceHit[]> {
  const text = query.trim();
  if (!text) return [];

  try {
    const hits = await searchNominatim(text, signal);
    if (hits.length) return hits;
  } catch {
    // public Nominatim may reject browser clients; Photon is the fallback
  }
  return searchPhoton(text, signal);
}
