<template>
  <div class="tiff-loader-container">
    <!-- 地图容器 -->
    <div ref="mapContainer" class="map-view"></div>

    <!-- 加载状态提示 -->
    <div v-if="loading" class="loading-mask">
      <div class="loading-text">正在加载 TIFF 数据...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-message">
      {{ errorMsg }}
    </div>

    <!-- <FloatingBall></FloatingBall> -->
    <template>
      <div v-html="contentHtml"></div>
    </template>
  </div>
</template>

<script setup lang="ts">
//@ts-nocheck

import { ref, onMounted, onUnmounted } from 'vue';
import mars3d from 'mars3d';
import { fromUrl } from 'geotiff';
import { getMapInstance } from "@/assets/util/index";
import FloatingBall from "@/components/FloatingBall/FloatingBall.vue";
import { getContentHtml } from "@/request/attractInvestment";
import axios from "axios"
import { log } from 'geotiff/dist-node/logging';
let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;
let MapContainer: mars3d.Map;
// ------------- 需要用户提供的参数（必选）-------------
// TIFF 文件的 URL 路径（放在 public 目录下或通过服务器访问）
const TIFF_URL = 'http://localhost:8086/public/tif/monalisa-20x20.tiff';

// TIFF 数据对应的地理范围（经纬度：[最小经度, 最小纬度, 最大经度, 最大纬度]）
const TIFF_BOUNDS = [116.3, 39.8, 116.5, 40.0];

// ------------- 可选参数（可根据需要调整）-------------
const TILE_SIZE = 256; // 瓦片大小
const MAX_LEVEL = 15; // 最大缩放级别
const LAYER_NAME = 'TIFF 影像图层'; // 图层名称


const contentHtml = ref('')

// 组件内部状态
const mapContainer = ref<HTMLDivElement | null>(null);
const map = ref<mars3d.Map | null>(null);
const loading = ref(true);
const errorMsg = ref('');
let tiffLayer: mars3d.layer.ImageLayer | null = null;



// 加载并解析 TIFF 数据
const loadTiffData = async () => {
  try {
    // 1. 加载 TIFF 文件
    const tiff = await fromUrl(TIFF_URL);
    console.log('tiff', tiff);

    const image = await tiff.getImage();
    console.log('image', image);

    // 2. 直接从 image 对象获取元数据（无需 getMetadata）
    const fileDirectory = image.fileDirectory;
    const tiffWidth = fileDirectory.ImageWidth;
    const tiffHeight = fileDirectory.ImageLength;
    const samplesPerPixel = fileDirectory.SamplesPerPixel; // 波段数
    const tiffData = await image.readRasters();

    // 2. 创建自定义影像提供者
    const provider = new mars3d.Cesium.ImageryProvider({
      getTileUrl: () => '', // 占位，实际通过 requestImage 生成
      requestImage: async (x: number, y: number, level: number) => {
        return createTileCanvas(x, y, level, tiffData, meta);
      },
      rectangle: mars3d.Cesium.Rectangle.fromDegrees(
        TIFF_BOUNDS[0], TIFF_BOUNDS[1],
        TIFF_BOUNDS[2], TIFF_BOUNDS[3]
      ),
      tileWidth: TILE_SIZE,
      tileHeight: TILE_SIZE,
      maximumLevel: MAX_LEVEL
    });

    // 3. 创建并添加图层
    tiffLayer = new mars3d.layer.ImageLayer({
      name: LAYER_NAME,
      provider,
      visible: true
    });
    map.value?.addLayer(tiffLayer);

    // 4. 定位到图层范围
    map.value?.flyTo(tiffLayer);
    loading.value = false;
  } catch (err) {
    console.error('TIFF 加载失败:', err);
    errorMsg.value = `加载失败: ${err instanceof Error ? err.message : '未知错误'}`;
    loading.value = false;
  }
};

// 创建瓦片图像
const createTileCanvas = (
  x: number, y: number, level: number,
  tiffData: Uint16Array | Uint32Array,
  meta: { width: number; height: number; samplesPerPixel: number }
) => {
  // 创建画布
  const canvas = document.createElement('canvas');
  canvas.width = TILE_SIZE;
  canvas.height = TILE_SIZE;
  const ctx = canvas.getContext('2d');
  if (!ctx) return canvas;

  const imageData = ctx.createImageData(TILE_SIZE, TILE_SIZE);
  const pixels = imageData.data;

  // 计算瓦片对应的 TIFF 像素范围
  const rect = mars3d.Cesium.Rectangle.fromDegrees(
    TIFF_BOUNDS[0], TIFF_BOUNDS[1],
    TIFF_BOUNDS[2], TIFF_BOUNDS[3]
  );
  const tilingScheme = new mars3d.Cesium.WebMercatorTilingScheme();
  const tileRect = tilingScheme.tileXYToRectangle(x, y, level);

  // 填充像素数据（简化版，处理单波段和 RGB 波段）
  const { width: tiffWidth, height: tiffHeight, samplesPerPixel } = meta;
  const xRatio = tiffWidth / (rect.east - rect.west);
  const yRatio = tiffHeight / (rect.north - rect.south);

  for (let cy = 0; cy < TILE_SIZE; cy++) {
    for (let cx = 0; cx < TILE_SIZE; cx++) {
      // 计算当前像素对应的 TIFF 坐标
      const lon = tileRect.west + (cx / TILE_SIZE) * (tileRect.east - tileRect.west);
      const lat = tileRect.north - (cy / TILE_SIZE) * (tileRect.north - tileRect.south);

      const tiffX = Math.floor((lon - rect.west) * xRatio);
      const tiffY = Math.floor((rect.north - lat) * yRatio);

      // 检查边界
      if (tiffX < 0 || tiffX >= tiffWidth || tiffY < 0 || tiffY >= tiffHeight) continue;

      // 计算索引
      const tiffIndex = (tiffY * tiffWidth + tiffX) * samplesPerPixel;
      const pixelIndex = (cy * TILE_SIZE + cx) * 4;

      // 设置颜色（根据波段数处理）
      if (samplesPerPixel === 1) {
        // 单波段（灰度图）
        const val = normalizeValue(tiffData[tiffIndex]);
        pixels[pixelIndex] = val;
        pixels[pixelIndex + 1] = val;
        pixels[pixelIndex + 2] = val;
        pixels[pixelIndex + 3] = 255;
      } else if (samplesPerPixel === 3) {
        // RGB 三波段
        pixels[pixelIndex] = normalizeValue(tiffData[tiffIndex]);
        pixels[pixelIndex + 1] = normalizeValue(tiffData[tiffIndex + 1]);
        pixels[pixelIndex + 2] = normalizeValue(tiffData[tiffIndex + 2]);
        pixels[pixelIndex + 3] = 255;
      }
    }
  }

  ctx.putImageData(imageData, 0, 0);
  return canvas;
};

// 归一化值到 0-255
const normalizeValue = (value: number) => {
  // 注意：实际使用时需根据你的 TIFF 数据范围调整（如最小值 0，最大值 1000）
  const min = 0;
  const max = 255; // 若你的数据范围不同，修改此处
  return Math.max(0, Math.min(255, Math.round((value - min) / (max - min) * 255)));
};

// 生命周期
onMounted(async () => {
  await nextTick(() => {
    MapContainer = getMapInstance()
    axios.get('http://localhost:8086/FloatingBall/floating-ball.html').then(res=>{
      console.log('res',res);
      contentHtml.value = res.data
    })
    
    // initPoint();
    // initData()
  });
  // 等待地图初始化完成
  setTimeout(() => {
    loadTiffData();
  }, 500);
});

onUnmounted(() => {
  // 移除图层
  if (map.value && tiffLayer) {
    map.value.removeLayer(tiffLayer);
  }
  // 销毁地图
  if (map.value) {
    map.value.destroy();
    map.value = null;
  }
});
</script>

<style scoped>
.map-view {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-text {
  color: white;
  font-size: 18px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
}

.error-message {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #f44336;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  z-index: 100;
}
</style>
