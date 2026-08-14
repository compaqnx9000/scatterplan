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
            <span>工程名称</span>
            <el-input v-model="queryParams.search" placeholder="请输入工程名称" clearable />
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
            <el-table-column type="selection" width="40" align="center" />
            <el-table-column label="序号" type="index" width="70" align="center" />
            <el-table-column prop="name" label="工程名称" align="center" min-width="140" show-overflow-tooltip />
            <el-table-column prop="username" label="用户名称" align="center" min-width="90" show-overflow-tooltip />
            <el-table-column prop="single_link_count" label="单链路" align="center" min-width="90">
              <template #default="scope">
                {{ scope.row.single_link_count ? `${scope.row.single_link_count}条` : "无" }}
              </template>
            </el-table-column>
            <el-table-column prop="has_coverage" label="区域覆盖" align="center" min-width="90">
              <template #default="scope">
                {{ scope.row.has_coverage ? "有" : "无" }}
              </template>
            </el-table-column>
            <el-table-column prop="station_count" label="推荐站点" align="center" min-width="90">
              <template #default="scope">
                {{ scope.row.station_count || 0 }}
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" align="center" min-width="168" />

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

import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listProjects, deleteProject } from "@/request/sitePlanting";
import { useRouter } from "vue-router";

const router = useRouter();
const queryParams = ref({
  page: 1,
  search: "",
  user__username: "",
});

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

const getList = async () => {
  loading.value = true;
  try {
    const res: any = await listProjects(queryParams.value);
    tableData = res.results || [];
    tableData.forEach((item: any) => {
      item.updated_at = isoToNormalTime(item.updated_at);
    });
    total.value = res.count || 0;
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
  router.push({
    path: "/",
    query: {
      project: row.id,
    },
  });
};

const handleDelete = (row?: any) => {
  const deleteIds = row ? [row.id] : ids.value;
  ElMessageBox.confirm("确认删除选中工程? 工程内的链路、覆盖和站点会一并删除。", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    customClass: "gotham-message-box",
  })
    .then(async () => {
      try {
        await Promise.all(deleteIds.map((id) => deleteProject(id)));
        ElMessage.success("删除成功");
        getList();
      } catch {
        ElMessage.error("删除失败");
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
</style>
