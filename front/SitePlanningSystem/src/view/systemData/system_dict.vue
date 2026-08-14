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

        <div class="results-panel__toolbar">
          <label class="results-panel__field">
            <span>字典名称</span>
            <el-input v-model="queryParams.search" placeholder="请输入字典名称" clearable />
          </label>
          <div class="results-panel__actions">
            <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="handleReset">重置</button>
            <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleSearch">查询</button>
          </div>
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
import { ElMessage, ElMessageBox } from "element-plus";
import { listUser, delUser, updateUser } from "@/request/system_user";
import { formatDecimal6, useGothamPanel } from "./useGothamPanel";

const { panelRef, panelStyle, startDrag, handleClose } = useGothamPanel(1100);

const queryParams = ref({
  page: 1,
  search: "",
});

let tableData: any = reactive([]);
const total = ref(0);
const loading = ref(false);
const ids = ref<number[]>([]);
const multiple = ref(true);

const getList = async () => {
  loading.value = true;
  try {
    const res: any = await listUser(queryParams.value);
    tableData = res.results || [];
    total.value = res.count || 0;
  } catch (error) {
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
  queryParams.value.page = 1;
  getList();
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
  if (dialogStatus.value === "查看") {
    showEditDialog.value = false;
    return;
  }
  try {
    await updateUser(editForm.value);
    ElMessage.success("编辑成功");
    showEditDialog.value = false;
    getList();
  } catch (error) {}
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
      delUser(deleteIds)
        .then(() => {
          ElMessage.success("删除成功");
          getList();
        })
        .catch(() => {});
    })
    .catch(() => {});
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
</style>
