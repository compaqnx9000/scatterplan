<template>
  <transition name="station-fade">
    <div ref="panelRef" class="results-panel" :style="panelStyle">
      <div class="results-panel__panel">
        <div class="results-panel__header" @mousedown="startDrag">
          <div class="results-panel__title">站点规划结果</div>
          <button class="results-panel__close" type="button" title="关闭" @click="handleClose" @mousedown.stop>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>

        <div class="results-panel__toolbar">
          <label class="results-panel__field">
            <span>站点规划名称</span>
            <el-input v-model="queryParams.search" placeholder="请输入站点规划名称" clearable />
          </label>
          <label class="results-panel__field">
            <span>用户名称</span>
            <el-input v-model="queryParams.user__username" placeholder="请输入用户名称" clearable />
          </label>
          <div class="results-panel__actions">
            <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="handleReset">重置</button>
            <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleSearch">查询</button>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="results-panel-tabs">
          <el-tab-pane label="单链路" name="singleLink" />
          <el-tab-pane label="区域覆盖" name="areaCoverage" />
        </el-tabs>

        <div class="results-panel__table">
          <el-table
            v-loading="loading"
            :data="tableData"
            @selection-change="handleSelectionChange"
            style="width: 100%"
            header-row-class-name="results-table-header"
            :row-style="{ height: '40px' }"
            :row-class-name="tableRowClassName"
          >
            <template v-if="activeTab === 'singleLink'">
              <el-table-column type="selection" width="40" align="center" />
              <el-table-column label="序号" type="index" width="70" align="center" />
              <el-table-column prop="name" label="工程名称" align="center" min-width="120" show-overflow-tooltip />
              <el-table-column prop="username" label="用户名称" align="center" min-width="90" show-overflow-tooltip />
              <el-table-column prop="distance_km" label="工程距离（km）" align="center" min-width="120">
                <template #default="scope">
                  {{ Number(scope.row.distance_km).toFixed(6) }}
                </template>
              </el-table-column>
              <el-table-column prop="tx_lon" label="站点经度（°）" align="center" min-width="120" />
              <el-table-column prop="tx_lat" label="站点纬度（°）" align="center" min-width="120" />
              <el-table-column prop="calculation_duration" label="计算耗时" align="center" min-width="100" />
              <el-table-column prop="updated_at" label="更新时间" align="center" min-width="160" />
            </template>
            <template v-else>
              <el-table-column type="selection" width="40" align="center" />
              <el-table-column label="序号" type="index" width="70" align="center" />
              <el-table-column prop="name" label="工程名称" align="center" min-width="120" show-overflow-tooltip />
              <el-table-column prop="username" label="用户名称" align="center" min-width="90" show-overflow-tooltip />
              <el-table-column prop="coverage_type" label="区域类型" width="90" align="center">
                <template #default="scope">
                  {{ scope.row.coverage_type === "rectangle" ? "矩形区域" : "圆形区域" }}
                </template>
              </el-table-column>
              <el-table-column prop="tx_longitude" label="站点经度（°）" align="center" min-width="120" />
              <el-table-column prop="tx_latitude" label="站点纬度（°）" align="center" min-width="120" />
              <el-table-column prop="frequency" label="信号频率（MHz）" align="center" min-width="120" />
              <el-table-column prop="calculation_area" label="区域面积（km²）" align="center" min-width="130">
                <template #default="scope">
                  {{ Number(scope.row.calculation_area).toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="calculation_duration" label="计算耗时" align="center" min-width="100" />
              <el-table-column prop="updated_at" label="更新时间" width="168" align="center" />
            </template>

            <el-table-column label="操作" align="center" width="150" fixed="right">
              <template #default="scope">
                <div class="results-panel__row-actions">
                  <button class="results-panel__link" type="button" @click="handleView(scope.row)">查看详情</button>
                  <button class="results-panel__link results-panel__link--danger" type="button" @click="handleDelete(scope.row)">
                    删除
                  </button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="results-panel__footer">
          <el-pagination
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="queryParams.page"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, prev, pager, next, jumper"
            :total="total"
          />
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck

import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listSingleLink, deleteSingleLink, listAreaCoverage, deleteAreaCoverage } from "@/request/sitePlanting";
import { useRouter } from "vue-router";

const router = useRouter();
const queryParams = ref({
  page: 1,
  search: "",
  user__username: "",
});

const activeTab = ref("singleLink");
watch(
  () => activeTab.value,
  (newVal) => {
    queryParams.value.search = "";
    queryParams.value.user__username = "";
    queryParams.value.page = 1;
    getList(newVal);
  }
);

let tableData: any = reactive([]);
const total = ref(0);
const loading = ref(false);
const ids = ref<number[]>([]);
const multiple = ref(true);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 24, y: 72 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 1280;

const panelStyle = computed(() => ({
  left: `${panelPos.value.x}px`,
  top: `${panelPos.value.y}px`,
  width: `${Math.min(PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const getDefaultPanelPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 620;
  return {
    x: Math.max(24, Math.round((window.innerWidth - width) / 2)),
    y: Math.max(72, Math.round((window.innerHeight - height) / 2)),
  };
};

const centerPanel = async () => {
  panelPos.value = getDefaultPanelPos();
  await nextTick();
  const el = panelRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  panelPos.value = getDefaultPanelPos({ width: rect.width, height: rect.height });
};

const startDrag = (e: MouseEvent) => {
  if (e.button !== 0) return;
  dragging.value = true;
  dragOffset.value = {
    x: e.clientX - panelPos.value.x,
    y: e.clientY - panelPos.value.y,
  };
  window.addEventListener("mousemove", onDrag);
  window.addEventListener("mouseup", stopDrag);
};

const onDrag = (e: MouseEvent) => {
  if (!dragging.value) return;
  const width = Math.min(PANEL_WIDTH, window.innerWidth - 48);
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(0, window.innerHeight - 80);
  panelPos.value = {
    x: Math.min(maxX, Math.max(0, e.clientX - dragOffset.value.x)),
    y: Math.min(maxY, Math.max(0, e.clientY - dragOffset.value.y)),
  };
};

const stopDrag = () => {
  dragging.value = false;
  window.removeEventListener("mousemove", onDrag);
  window.removeEventListener("mouseup", stopDrag);
};

const handleClose = () => {
  router.push("/");
};

const onEsc = (e: KeyboardEvent) => {
  if (e.key === "Escape") handleClose();
};

const isoToNormalTime = (isoTime) => {
  const date = new Date(isoTime);
  if (isNaN(date.getTime())) {
    return isoTime;
  }
  const padZero = (num) => num.toString().padStart(2, "0");
  const year = date.getFullYear();
  const month = padZero(date.getMonth() + 1);
  const day = padZero(date.getDate());
  const hour = padZero(date.getHours());
  const minute = padZero(date.getMinutes());
  const second = padZero(date.getSeconds());
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
};

const getList = async (type?: string) => {
  loading.value = true;
  const Type = type ? type : activeTab.value;
  try {
    if (Type === "singleLink") {
      const res: any = await listSingleLink(queryParams.value);
      tableData = res.results || [];
      tableData.forEach((item: any) => {
        item.updated_at = isoToNormalTime(item.updated_at);
      });
      total.value = res.count || 0;
      return;
    } else if (Type === "areaCoverage") {
      const res: any = await listAreaCoverage(queryParams.value);
      tableData = res.results || [];
      tableData.forEach((item: any) => {
        item.updated_at = isoToNormalTime(item.updated_at);
      });
      total.value = res.count || 0;
      return;
    }
  } catch (error) {
    // ElMessage.error("加载失败");
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (val: number) => {
  queryParams.value.page = val;
  getList();
};

const handleCurrentChange = (val: number) => {
  queryParams.value.page = val;
  getList();
};

const handleSearch = () => {
  queryParams.value.page = 1;
  getList();
};

const handleReset = () => {
  queryParams.value.search = "";
  queryParams.value.user__username = "";
  queryParams.value.page = 1;
  getList();
};

const handleSelectionChange = (selection: any[]) => {
  ids.value = selection.map((item: any) => item.id);
  multiple.value = !selection.length;
};

const handleView = (row: any) => {
  if (activeTab.value === "singleLink") {
    router.push({
      path: "/",
      query: {
        type: "singleLink",
        id: row.id,
        name: row.name,
        tx_lon: row.tx_lon,
        tx_lat: row.tx_lat,
        tx_height: row.tx_terrain_height,
        rx_height: row.rx_terrain_height,
        rx_lon: row.rx_lon,
        rx_lat: row.rx_lat,
        tx_gain: row.tx_gain,
        rx_gain: row.rx_gain,
        freq: row.freq,
        trans_power: row.trans_power,
        diversity_order: row.diversity_order,
        median_loss: row.median_loss.toFixed(2),
        tx_theta: row.tx_theta.toFixed(2),
        rx_theta: row.rx_theta.toFixed(2),
        theta_scatter: row.theta_scatter.toFixed(2),
        area: row.area,
        max_height: row.max_height,
        scatterer_lon: row.scatterer_lon,
        scatterer_lat: row.scatterer_lat,
        scatterer_height: row.scatterer_height,
        image_path: row.image_path,
        created_at: row.created_at,
        user: row.user,
        distance_km: row.distance_km,
        residual_value: row.residual_value.toFixed(2),
        reliability: row.reliability,
        recv_power: row.recv_power.toFixed(2),
        tx_azimuth: row.tx_azimuth.toFixed(2),
        rx_azimuth: row.rx_azimuth.toFixed(2),
        comm_rate: row.comm_rate,
        tx_barrier_distance: row.tx_barrier_distance.toFixed(2),
        rx_barrier_distance: row.rx_barrier_distance.toFixed(2),
        tx_barrier_height: row.tx_barrier_height,
        rx_barrier_height: row.rx_barrier_height,
        tx_station_name: row.tx_station_name,
        rx_station_name: row.rx_station_name,
      },
    });
  } else {
    router.push({
      path: "/",
      query: {
        type: "areaCoverage",
        id: row.id,
        name: row.name,
        tx_gain: row.tx_gain,
        rx_gain: row.rx_gain,
        trans_power: row.trans_power,
        diversity_order: row.diversity_order,
        tx_lon: row.tx_longitude,
        tx_lat: row.tx_latitude,
        tx_height: row.tx_terrain_height,
        freq: row.frequency,
        coverage_type: row.coverage_type,
        rectangle_min_longitude: row.rectangle_min_longitude,
        rectangle_max_longitude: row.rectangle_max_longitude,
        rectangle_min_latitude: row.rectangle_min_latitude,
        rectangle_max_latitude: row.rectangle_max_latitude,
        circle_center_longitude: row.circle_center_longitude,
        circle_center_latitude: row.circle_center_latitude,
        circle_radius: row.circle_radius,
        tif_path: row.tif_path,
        image_path: row.image_path,
        loss_threshold: row.loss_threshold,
        eps_cells: row.eps_cells,
        min_samples: row.min_samples,
        p: row.p,
        number: row.number,
        rx_center_longitude: row.rx_center_longitude,
        rx_center_latitude: row.rx_center_latitude,
        to_road_name: row.to_road_name,
        to_road_slope: row.to_road_slope,
        to_road_distance: row.to_road_distance,
        created_at: row.created_at,
        user: row.user,
        image_colors: row.image_colors,
        image_max: row.image_max,
        image_min: row.image_min,
        comm_rate: row.comm_rate,
        tx_station_name: row.tx_station_name,
        subrange_circle_center_latitude: row.subrange_circle_center_latitude,
        subrange_circle_center_longitude: row.subrange_circle_center_longitude,
        subrange_circle_radius: row.subrange_circle_radius,
        subrange_rectangle_max_latitude: row.subrange_rectangle_max_latitude,
        subrange_rectangle_max_longitude: row.subrange_rectangle_max_longitude,
        subrange_rectangle_min_latitude: row.subrange_rectangle_min_latitude,
        subrange_rectangle_min_longitude: row.subrange_rectangle_min_longitude,
        subrange_type: row.subrange_type,
        prohibited_area_type: row.prohibited_area_type,
        prohibited_min_longitude: row.prohibited_min_longitude,
        prohibited_min_latitude: row.prohibited_min_latitude,
        prohibited_max_longitude: row.prohibited_max_longitude,
        prohibited_max_latitude: row.prohibited_max_latitude,
        prohibited_center_longitude: row.prohibited_center_longitude,
        prohibited_center_latitude: row.prohibited_center_latitude,
        prohibited_radius: row.prohibited_radius,
        relay_longitude: row.relay_longitude,
        relay_latitude: row.relay_latitude,
      },
    });
  }
};

const handleDelete = (row?: any) => {
  const deleteIds = row ? [row.id] : ids.value;
  ElMessageBox.confirm("确认删除选中数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    customClass: "gotham-message-box",
  })
    .then(() => {
      if (activeTab.value === "singleLink") {
        deleteSingleLink(deleteIds)
          .then(() => {
            ElMessage.success("删除成功");
            getList();
          })
          .catch(() => {});
      } else {
        deleteAreaCoverage(deleteIds)
          .then(() => {
            ElMessage.success("删除成功");
            getList();
          })
          .catch(() => {});
      }
    })
    .catch(() => {});
};

const tableRowClassName = ({ rowIndex }: { rowIndex: number }) => {
  if (rowIndex % 2 === 0) {
    return "even-row";
  }
  return "odd-row";
};

onMounted(() => {
  getList();
  centerPanel();
  window.addEventListener("keydown", onEsc);
});

onBeforeUnmount(() => {
  stopDrag();
  window.removeEventListener("keydown", onEsc);
});
</script>

<style lang="scss" scoped>
@import "@/styles/gotham-panel.scss";

.results-panel-tabs {
  margin-bottom: 4px;

  :deep(.el-tabs__header) {
    margin: 0 0 12px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: rgba(180, 200, 220, 0.16);
  }

  :deep(.el-tabs__item) {
    height: 40px;
    padding: 0 20px;
    color: rgba(220, 228, 236, 0.7);
    font-size: 13px;
    font-family: inherit;
  }

  :deep(.el-tabs__item:hover) {
    color: #ffffff;
  }

  :deep(.el-tabs__item.is-active) {
    color: #ffffff;
    font-weight: 600;
  }

  :deep(.el-tabs__active-bar) {
    height: 2px;
    background-color: #00a2ff;
  }

  :deep(.el-tabs__content) {
    display: none;
  }
}
</style>
