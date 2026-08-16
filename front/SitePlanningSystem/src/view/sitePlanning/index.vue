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
          <div class="results-panel__search">
            <div class="results-panel__seg">
              <button
                type="button"
                class="results-panel__seg-btn"
                :class="{ 'is-active': queryField === 'name' }"
                @click="queryField = 'name'"
              >
                工程名称
              </button>
              <button
                type="button"
                class="results-panel__seg-btn"
                :class="{ 'is-active': queryField === 'user' }"
                @click="queryField = 'user'"
              >
                用户名称
              </button>
            </div>
            <input
              v-model="keyword"
              class="results-panel__search-input"
              type="text"
              :placeholder="queryField === 'user' ? '请输入用户名称' : '请输入工程名称'"
              @keyup.enter="handleSearch"
            />
          </div>
          <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleSearch">查询</button>
        </div>

        <div class="results-panel__table">
          <el-table
            v-loading="loading"
            :data="tableData"
            :max-height="tableMaxHeight"
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
          <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleClose">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M5.4 12.4 10 17l8.6-9.2"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            确认
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck

import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listProjects, deleteProject } from "@/request/sitePlanting";
import { useRouter } from "vue-router";

const router = useRouter();
const queryField = ref<"name" | "user">("name");
const keyword = ref("");

const tableData = ref<any[]>([]);
const loading = ref(false);
const ids = ref<number[]>([]);
const multiple = ref(true);

const panelRef = ref<HTMLElement | null>(null);
const panelPos = ref({ x: 24, y: 72 });
const dragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const PANEL_WIDTH = 1280;
const tableMaxHeight = ref(Math.max(280, Math.min(480, window.innerHeight - 300)));

const updateTableMaxHeight = () => {
  tableMaxHeight.value = Math.max(280, Math.min(480, window.innerHeight - 300));
};

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
    const all: any[] = [];
    let page = 1;
    const text = keyword.value.trim();
    while (page <= 50) {
      const params: Record<string, any> = { page, page_size: 100 };
      if (text) {
        if (queryField.value === "user") params.user__username = text;
        else params.search = text;
      }
      const res: any = await listProjects(params);
      const batch = Array.isArray(res) ? res : res?.results || [];
      all.push(...batch);
      if (Array.isArray(res) || !res?.next || !batch.length) break;
      page += 1;
    }
    all.forEach((item: any) => {
      item.updated_at = isoToNormalTime(item.updated_at);
    });
    tableData.value = all;
  } catch (error) {
    tableData.value = [];
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
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
  updateTableMaxHeight();
  window.addEventListener("resize", updateTableMaxHeight);
  window.addEventListener("keydown", onEsc);
});

onBeforeUnmount(() => {
  stopDrag();
  window.removeEventListener("resize", updateTableMaxHeight);
  window.removeEventListener("keydown", onEsc);
});
</script>

<style lang="scss" scoped>
@import "@/styles/gotham-panel.scss";
</style>
