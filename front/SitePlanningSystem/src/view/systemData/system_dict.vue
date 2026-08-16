<template>
  <transition name="station-fade">
    <div ref="panelRef" class="results-panel" :style="panelStyle">
      <div class="results-panel__panel">
        <div class="results-panel__header" @mousedown="startDrag">
          <div class="results-panel__title">数据字典配置</div>
          <button class="results-panel__close" type="button" title="关闭" @click="handleClose" @mousedown.stop>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="results-panel__section-head">
          <h3 class="results-panel__card-title">字典列表</h3>
        </div>

        <div class="results-panel__table">
          <el-table
            v-loading="loading"
            :data="tableData"
            @selection-change="handleSelectionChange"
            style="width: 100%"
            :row-style="{ height: '40px' }"
            :row-class-name="tableRowClassName"
          >
            <el-table-column type="selection" width="40" align="center" />
            <el-table-column prop="num" label="序号" type="index" width="80" align="center" />
            <el-table-column prop="siteCode" label="字典名称" align="center" min-width="140" show-overflow-tooltip />
            <el-table-column prop="siteName" label="数据标签" align="center" min-width="140" show-overflow-tooltip />
            <el-table-column prop="siteLongitude" label="字典类型" align="center" min-width="120">
              <template #default="scope">
                {{ formatDecimal6(scope.row.siteLongitude) || scope.row.siteLongitude }}
              </template>
            </el-table-column>
            <el-table-column prop="siteLatitude" label="创建时间" align="center" min-width="140">
              <template #default="scope">
                {{ formatDecimal6(scope.row.siteLatitude) || scope.row.siteLatitude }}
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="150">
              <template #default="scope">
                <div class="results-panel__row-actions">
                  <button class="results-panel__link" type="button" @click="handleEdit(scope.row)">查看详情</button>
                  <button class="results-panel__link results-panel__link--danger" type="button" @click="handleDelete(scope.row)">删除</button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="results-panel__footer results-panel__footer--split">
          <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="triggerImport">导入</button>
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

        <input
          ref="importInputRef"
          type="file"
          accept=".json,.csv,.xlsx,.xls"
          class="results-panel__file-input"
          @change="handleImportFile"
        />

        <div v-if="showEditDialog" class="results-panel__sub">
          <div class="results-panel__sub-card">
            <div class="results-panel__sub-head">
              <div class="results-panel__sub-title">{{ dialogTitle }}</div>
              <button class="results-panel__close" type="button" @click="showEditDialog = false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                </svg>
              </button>
            </div>
            <el-form :model="editForm" label-position="top">
              <el-form-item label="用户名称">
                <el-input v-model="editForm.username" placeholder="请输入" :disabled="dialogStatus === '查看'" />
              </el-form-item>
              <el-form-item label="用户密码">
                <el-input v-model="editForm.password" placeholder="请输入" :disabled="dialogStatus === '查看'" />
              </el-form-item>
              <el-form-item label="用户描述">
                <el-input v-model="editForm.description" placeholder="请输入" :disabled="dialogStatus === '查看'" />
              </el-form-item>
            </el-form>
            <div class="results-panel__sub-actions">
              <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="showEditDialog = false">取消</button>
              <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleConfirmEdit">确认</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck

import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { formatDecimal6, useGothamPanel } from "./useGothamPanel";

const { panelRef, panelStyle, startDrag, handleClose } = useGothamPanel(1100);

let tableData: any = reactive([]);
const loading = ref(false);
const ids = ref<number[]>([]);
const multiple = ref(true);
const importInputRef = ref<HTMLInputElement | null>(null);

const getList = async () => {
  loading.value = true;
  try {
    // 字典表尚未落地，勿再调用用户接口
    tableData = [];
  } catch (error) {
  } finally {
    loading.value = false;
  }
};

const handleSelectionChange = (selection: any[]) => {
  ids.value = selection.map((item: any) => item.id);
  multiple.value = !selection.length;
};

const showEditDialog = ref(false);
const editForm = ref({
  id: "",
  username: "",
  password: "",
  description: "",
  is_active: true,
});
const dialogTitle = ref("");
const dialogStatus = ref("");

const handleEdit = (row: any) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    password: row.password,
    description: row.description,
    is_active: row.is_active,
  };
  showEditDialog.value = true;
  dialogTitle.value = "查看详情";
  dialogStatus.value = "查看";
};

const handleConfirmEdit = async () => {
  showEditDialog.value = false;
};

const handleDelete = (row?: any) => {
  ElMessage.warning("数据字典尚未接入，删除不会生效（也不会再删除用户）");
};

const triggerImport = () => {
  importInputRef.value?.click();
};

const handleImportFile = (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  // 字典导入接口尚未落地，先保留选文件入口
  ElMessage.info(`已选择文件：${file.name}（导入功能待接入）`);
};

const tableRowClassName = ({ rowIndex }: { rowIndex: number }) => {
  return rowIndex % 2 === 0 ? "even-row" : "odd-row";
};

onMounted(() => {
  getList();
});
</script>

<style lang="scss" scoped>
@import "@/styles/gotham-panel.scss";

.results-panel__file-input {
  display: none;
}
</style>
