<template>
  <transition name="station-fade">
    <div ref="panelRef" class="results-panel" :style="panelStyle">
      <div class="results-panel__panel">
        <div class="results-panel__header" @mousedown="startDrag">
          <div class="results-panel__title">用户管理</div>
          <button class="results-panel__close" type="button" title="关闭" @click="handleClose" @mousedown.stop>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="results-panel__toolbar">
          <label class="results-panel__field">
            <span>用户名称</span>
            <el-input v-model="queryParams.search" placeholder="请输入用户名称" clearable />
          </label>
          <div class="results-panel__actions">
            <button v-show="is_staff" class="results-panel__btn results-panel__btn--outline" type="button" @click="showAddDialog = true">
              新增用户
            </button>
            <button v-show="is_staff" class="results-panel__btn results-panel__btn--danger" type="button" @click="handleBatchDelete">
              批量删除
            </button>
            <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="handleReset">重置</button>
            <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleSearch">查询</button>
          </div>
        </div>

        <div class="results-panel__section-head">
          <h3 class="results-panel__card-title">用户列表</h3>
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
            <el-table-column prop="id" label="用户ID" type="index" width="90" align="center" />
            <el-table-column prop="username" label="用户名称" align="center" min-width="120" show-overflow-tooltip />
            <el-table-column prop="description" label="用户描述" align="center" min-width="160" show-overflow-tooltip />
            <el-table-column prop="is_active" label="用户状态" align="center" width="120" v-if="is_staff">
              <template #default="scope">
                <el-switch
                  @change="handleStatusChange(scope.row)"
                  v-model="scope.row.is_active"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="160">
              <template #default="scope">
                <div class="results-panel__row-actions">
                  <button class="results-panel__link" type="button" @click="handleView(scope.row)">查看</button>
                  <button class="results-panel__link" type="button" @click="handleEdit(scope.row)">编辑</button>
                  <button v-show="is_staff" class="results-panel__link results-panel__link--danger" type="button" @click="handleDelete(scope.row)">
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

        <div v-if="showAddDialog" class="results-panel__sub">
          <div class="results-panel__sub-card">
            <div class="results-panel__sub-head">
              <div class="results-panel__sub-title">新增用户</div>
              <button class="results-panel__close" type="button" @click="showAddDialog = false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                </svg>
              </button>
            </div>
            <el-form :rules="rules" ref="formRef" :model="addForm" label-position="top">
              <el-form-item label="用户名称" prop="username">
                <el-input v-model="addForm.username" placeholder="请输入" />
              </el-form-item>
              <el-form-item label="用户密码" prop="password">
                <el-input v-model="addForm.password" placeholder="请输入" show-password />
              </el-form-item>
              <el-form-item label="用户描述" prop="description">
                <el-input v-model="addForm.description" placeholder="请输入" />
              </el-form-item>
            </el-form>
            <div class="results-panel__sub-actions">
              <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="showAddDialog = false">取消</button>
              <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleConfirmAdd(formRef)">确认</button>
            </div>
          </div>
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
                <el-input v-model="editForm.password" placeholder="请输入" :disabled="dialogStatus === '查看'" show-password />
              </el-form-item>
              <el-form-item label="用户描述">
                <el-input v-model="editForm.description" placeholder="请输入" :disabled="dialogStatus === '查看'" />
              </el-form-item>
              <el-form-item label="用户状态">
                <el-switch
                  :disabled="dialogStatus === '查看'"
                  v-model="editForm.is_active"
                />
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

import { nextTick, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listUser, addUser, delUser, updateUser, batchDelUser } from "@/request/system_user";
import { useGothamPanel } from "./useGothamPanel";

const { panelRef, panelStyle, startDrag, handleClose } = useGothamPanel(960);

const queryParams = ref({
  page: 1,
  search: "",
});

let tableData: any = reactive([]);
const total = ref(0);
const loading = ref(false);
const ids = ref<number[]>([]);
const multiple = ref(true);
const is_staff = ref(false);

const showAddDialog = ref(false);
const addForm = ref({
  username: "",
  password: "",
  description: "",
});
const formRef = ref(null);
const rules = ref({
  username: [{ required: true, message: "请输入用户名称", trigger: "blur" }],
  password: [{ required: true, message: "请输入用户密码", trigger: "blur" }],
  description: [{ required: false, message: "请输入用户描述", trigger: "blur" }],
});

const resetForm = () => {
  addForm.value = {
    username: "",
    password: "",
    description: "",
  };
};

const handleConfirmAdd = async (formEl: any) => {
  if (!formEl) return;
  await formEl.validate(async (valid) => {
    if (valid) {
      await addUser(addForm.value);
      ElMessage.success("添加成功");
      showAddDialog.value = false;
      resetForm();
      getList();
      return;
    }
    ElMessage.error("请填写完整信息");
  });
};

const handleStatusChange = async (row: any) => {
  try {
    editForm.value = {
      id: row.id,
      username: row.username,
      password: row.password,
      description: row.description,
      is_active: row.is_active,
    };
    await updateUser(editForm.value);
    ElMessage.success("编辑成功");
    showEditDialog.value = false;
    getList();
  } catch (error) {}
};

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

const handleView = (row: any) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    password: row.password,
    description: row.description,
    is_active: row.is_active,
  };
  showEditDialog.value = true;
  dialogTitle.value = "查看用户";
  dialogStatus.value = "查看";
};

const handleEdit = (row: any) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    password: row.password,
    description: row.description,
    is_active: row.is_active,
  };
  showEditDialog.value = true;
  dialogTitle.value = "编辑用户";
  dialogStatus.value = "编辑";
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

const handleBatchDelete = () => {
  if (ids.value.length === 0) {
    ElMessage.warning("请选择要删除的数据");
    return;
  }
  ElMessageBox.confirm("确认删除选中数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    customClass: "gotham-message-box",
  })
    .then(() => {
      batchDelUser(ids.value)
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

onMounted(async () => {
  await nextTick(() => {
    is_staff.value = JSON.parse(localStorage.getItem("is_staff"));
  });
  getList();
});
</script>

<style lang="scss" scoped>
@import "@/styles/gotham-panel.scss";
</style>
