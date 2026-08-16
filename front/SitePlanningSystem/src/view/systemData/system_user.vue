<template>
  <transition name="station-fade">
    <div ref="panelRef" class="results-panel" :style="panelStyle">
      <div class="results-panel__panel">
        <div class="results-panel__edge"></div>
        <div class="results-panel__header" @mousedown="startDrag">
          <div class="results-panel__heading">
            <div class="results-panel__badge">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 7.2a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2Zm0 2.2c-3.2 0-5.8 1.7-5.8 3.8v1.6h11.6v-1.6c0-2.1-2.6-3.8-5.8-3.8Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="results-panel__title">用户管理</h2>
              <p class="results-panel__subtitle">Manage accounts and access status.</p>
            </div>
          </div>
          <button class="results-panel__icon-btn" type="button" title="关闭" @click="handleClose" @mousedown.stop>
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

        <div class="results-panel__section-head">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M5 7h14M5 12h14M5 17h10"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
          </svg>
          <h3 class="results-panel__card-title">用户列表</h3>
        </div>

        <div class="results-panel__table">
          <el-table
            v-loading="loading"
            :data="tableData"
            style="width: 100%"
            :row-style="{ height: '40px' }"
            :row-class-name="tableRowClassName"
          >
            <el-table-column prop="id" label="用户ID" type="index" width="90" align="center" />
            <el-table-column prop="username" label="用户名称" align="center" min-width="120">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.username || ''"
                  placement="top"
                  effect="dark"
                  :disabled="!row.username"
                  :show-after="120"
                  :offset="8"
                  append-to="body"
                  popper-class="gotham-table-tooltip"
                >
                  <span class="results-panel__ellip">{{ row.username }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="用户描述" align="center" min-width="160">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.description || ''"
                  placement="top"
                  effect="dark"
                  :disabled="!row.description"
                  :show-after="120"
                  :offset="8"
                  append-to="body"
                  popper-class="gotham-table-tooltip"
                >
                  <span class="results-panel__ellip">{{ row.description }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column v-if="is_staff" prop="is_active" label="用户状态" align="center" width="120">
              <template #default="scope">
                <el-switch v-model="scope.row.is_active" @change="handleStatusChange(scope.row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="160">
              <template #default="scope">
                <div class="results-panel__row-actions">
                  <button class="results-panel__link" type="button" @click="handleView(scope.row)">查看</button>
                  <button class="results-panel__link" type="button" @click="handleEdit(scope.row)">编辑</button>
                  <button
                    v-show="is_staff"
                    class="results-panel__link results-panel__link--danger"
                    type="button"
                    @click="handleDelete(scope.row)"
                  >
                    删除
                  </button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="results-panel__footer" :class="{ 'results-panel__footer--split': is_staff }">
          <button
            v-show="is_staff"
            class="results-panel__btn results-panel__btn--ghost"
            type="button"
            @click="showAddDialog = true"
          >
            新增用户
          </button>
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

        <!-- 新增用户 -->
        <div v-if="showAddDialog" class="results-panel__sub">
          <div class="results-panel__sub-card">
            <div class="results-panel__edge"></div>
            <div class="results-panel__sub-head">
              <div class="results-panel__heading">
                <div class="results-panel__badge">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 7.2a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2Zm0 2.2c-3.2 0-5.8 1.7-5.8 3.8v1.6h11.6v-1.6c0-2.1-2.6-3.8-5.8-3.8Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M18.5 10.5v5M16 13h5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                <div>
                  <h3 class="results-panel__sub-title">新增用户</h3>
                  <p class="results-panel__subtitle">Create a new account.</p>
                </div>
              </div>
              <button class="results-panel__icon-btn" type="button" title="关闭" @click="showAddDialog = false">
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
            <div class="results-panel__sub-body">
              <div class="results-panel__section-head results-panel__section-head--in-sub">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M5 7h14M5 12h14M5 17h10"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <h3>Account</h3>
              </div>
              <el-form
                :rules="rules"
                ref="formRef"
                :model="addForm"
                label-position="top"
                class="results-panel__form"
                require-asterisk-position="right"
                :show-message="false"
              >
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
            </div>
            <div class="results-panel__sub-actions">
              <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="showAddDialog = false">
                取消
              </button>
              <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleConfirmAdd(formRef)">
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

        <!-- 查看 / 编辑用户 -->
        <div v-if="showEditDialog" class="results-panel__sub">
          <div class="results-panel__sub-card">
            <div class="results-panel__edge"></div>
            <div class="results-panel__sub-head">
              <div class="results-panel__heading">
                <div class="results-panel__badge">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 7.2a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2Zm0 2.2c-3.2 0-5.8 1.7-5.8 3.8v1.6h11.6v-1.6c0-2.1-2.6-3.8-5.8-3.8Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                <div>
                  <h3 class="results-panel__sub-title">{{ dialogTitle }}</h3>
                  <p class="results-panel__subtitle">
                    {{ dialogStatus === "查看" ? "View account details." : "Edit account details." }}
                  </p>
                </div>
              </div>
              <button class="results-panel__icon-btn" type="button" title="关闭" @click="showEditDialog = false">
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
            <div class="results-panel__sub-body">
              <div class="results-panel__section-head results-panel__section-head--in-sub">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M5 7h14M5 12h14M5 17h10"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <h3>Account</h3>
              </div>
              <el-form :model="editForm" label-position="top" class="results-panel__form">
                <el-form-item label="用户名称">
                  <el-input v-model="editForm.username" placeholder="请输入" :disabled="dialogStatus === '查看'" />
                </el-form-item>
                <el-form-item label="用户密码">
                  <el-input
                    v-model="editForm.password"
                    placeholder="请输入"
                    :disabled="dialogStatus === '查看'"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="用户描述">
                  <el-input v-model="editForm.description" placeholder="请输入" :disabled="dialogStatus === '查看'" />
                </el-form-item>
                <el-form-item label="用户状态">
                  <el-switch :disabled="dialogStatus === '查看'" v-model="editForm.is_active" />
                </el-form-item>
              </el-form>
            </div>
            <div class="results-panel__sub-actions">
              <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="showEditDialog = false">
                取消
              </button>
              <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleConfirmEdit">
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
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
//@ts-nocheck

import { nextTick, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listUser, addUser, delUser, updateUser } from "@/request/system_user";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";
import { useGothamPanel } from "./useGothamPanel";

const { panelRef, panelStyle, startDrag, handleClose } = useGothamPanel(960);

const tableData = ref<any[]>([]);
const loading = ref(false);
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
    shakeInvalidFormFields(formEl);
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
    const res: any = await listUser({ page: 1, page_size: 1000 });
    tableData.value = res.results || res || [];
  } catch (error) {
  } finally {
    loading.value = false;
  }
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

const handleDelete = (row: any) => {
  ElMessageBox.confirm("确认删除该用户?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    customClass: "gotham-message-box",
  })
    .then(() => {
      delUser(row.id)
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
