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
                  d="M4 7.5h16v9H4zM8 10.5h8M8 13.5h5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
              </svg>
            </div>
            <div>
              <h2 class="results-panel__title">地图接口服务</h2>
              <p class="results-panel__subtitle">Configure local or remote tile layers.</p>
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
          <h3 class="results-panel__card-title">地图接口列表</h3>
        </div>

        <div class="results-panel__table">
          <el-table
            v-loading="loading"
            :data="tableData"
            style="width: 100%"
            :row-style="{ height: '40px' }"
            :row-class-name="tableRowClassName"
          >
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="name" label="接口名称" align="center" min-width="120">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.name || ''"
                  placement="top"
                  effect="dark"
                  :disabled="!row.name"
                  :show-after="120"
                  :offset="8"
                  append-to="body"
                  popper-class="gotham-table-tooltip"
                >
                  <span class="results-panel__ellip">{{ row.name }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="service_type" label="类型" align="center" width="90">
              <template #default="scope">
                {{ (scope.row.service_type || "").toUpperCase() }}
              </template>
            </el-table-column>
            <el-table-column prop="url" label="服务地址" align="center" min-width="200">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.url || ''"
                  placement="top"
                  effect="dark"
                  :disabled="!row.url"
                  :show-after="120"
                  :offset="8"
                  append-to="body"
                  popper-class="gotham-table-tooltip"
                >
                  <span class="results-panel__ellip">{{ row.url }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="layers" label="图层" align="center" min-width="120">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.layers || ''"
                  placement="top"
                  effect="dark"
                  :disabled="!row.layers"
                  :show-after="120"
                  :offset="8"
                  append-to="body"
                  popper-class="gotham-table-tooltip"
                >
                  <span class="results-panel__ellip">{{ row.layers }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" align="center" min-width="120">
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
            <el-table-column prop="enabled" label="启用" align="center" width="90">
              <template #default="scope">
                <el-switch v-model="scope.row.enabled" @change="handleToggleEnabled(scope.row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="150">
              <template #default="scope">
                <div class="results-panel__row-actions">
                  <button class="results-panel__link" type="button" @click="openEdit(scope.row)">编辑</button>
                  <button class="results-panel__link results-panel__link--danger" type="button" @click="handleDelete(scope.row)">
                    删除
                  </button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="results-panel__footer results-panel__footer--split">
          <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="openCreate">新增接口</button>
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

        <div v-if="showFormDialog" class="results-panel__sub">
          <div class="results-panel__sub-card">
            <div class="results-panel__edge"></div>
            <div class="results-panel__sub-head">
              <div class="results-panel__heading">
                <div class="results-panel__badge">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M4 7.5h16v9H4zM8 10.5h8M8 13.5h5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                <div>
                  <h3 class="results-panel__sub-title">{{ formTitle }}</h3>
                  <p class="results-panel__subtitle">Local GeoServer or public tile URL.</p>
                </div>
              </div>
              <button class="results-panel__icon-btn" type="button" title="关闭" @click="showFormDialog = false">
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
                <h3>Endpoint</h3>
              </div>
              <el-form
                ref="formRef"
                :model="form"
                :rules="rules"
                label-position="top"
                class="results-panel__form"
                require-asterisk-position="right"
                :show-message="false"
              >
                <el-form-item label="接口名称" prop="name">
                  <el-input v-model="form.name" placeholder="如：本地路网" />
                </el-form-item>
                <el-form-item label="服务类型" prop="service_type">
                  <el-select
                    v-model="form.service_type"
                    placeholder="请选择"
                    style="width: 100%"
                    popper-class="station-config-select-dropdown"
                    :teleported="true"
                  >
                    <el-option label="WMS" value="wms" />
                    <el-option label="WMTS" value="wmts" />
                    <el-option label="XYZ" value="xyz" />
                  </el-select>
                </el-form-item>
                <el-form-item label="服务地址" prop="url">
                  <el-input
                    v-model="form.url"
                    :placeholder="
                      form.service_type === 'xyz'
                        ? 'http://127.0.0.1:8080/tiles/{z}/{x}/{y}.png'
                        : 'http://127.0.0.1:8080/geoserver/zk/wms'
                    "
                  />
                </el-form-item>
                <el-form-item v-if="form.service_type !== 'xyz'" label="图层名" prop="layers">
                  <el-input v-model="form.layers" placeholder="如：zk:china_roadnet2" />
                </el-form-item>
                <el-form-item v-if="form.service_type === 'wmts'" label="矩阵集">
                  <el-input v-model="form.tile_matrix_set_id" placeholder="EPSG:4326" />
                </el-form-item>
                <el-form-item label="接口描述">
                  <el-input
                    v-model="form.description"
                    type="textarea"
                    :rows="3"
                    resize="vertical"
                    placeholder="可选说明"
                  />
                </el-form-item>
                <div class="results-panel__switch-row">
                  <el-form-item label="启用">
                    <el-switch v-model="form.enabled" />
                  </el-form-item>
                  <el-form-item label="默认显示">
                    <el-switch v-model="form.show_default" />
                  </el-form-item>
                </div>
              </el-form>
            </div>
            <div class="results-panel__sub-actions">
              <button class="results-panel__btn results-panel__btn--ghost" type="button" @click="showFormDialog = false">
                取消
              </button>
              <button class="results-panel__btn results-panel__btn--primary" type="button" @click="handleSubmit">
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

import { getCurrentInstance, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  listMapServices,
  createMapService,
  updateMapService,
  deleteMapService,
} from "@/request/mapService";
import { shakeInvalidFormFields } from "@/view/home/service/formShake";
import { useGothamPanel } from "./useGothamPanel";

const { panelRef, panelStyle, startDrag, handleClose } = useGothamPanel(1100);
const $bus = getCurrentInstance()?.appContext.config.globalProperties.$bus;

const tableData = ref([]);
const loading = ref(false);
const showFormDialog = ref(false);
const formTitle = ref("新增接口");
const editingId = ref(null);
const formRef = ref(null);

const emptyForm = () => ({
  name: "",
  service_type: "wms",
  url: "",
  layers: "",
  format: "image/png",
  tile_matrix_set_id: "EPSG:4326",
  description: "",
  enabled: true,
  show_default: false,
  sort_order: 0,
});

const form = ref(emptyForm());

const rules = {
  name: [{ required: true, message: "请输入接口名称", trigger: "blur" }],
  service_type: [{ required: true, message: "请选择服务类型", trigger: "change" }],
  url: [{ required: true, message: "请输入服务地址", trigger: "blur" }],
  layers: [
    {
      validator: (_rule, value, callback) => {
        if (form.value.service_type !== "xyz" && !String(value || "").trim()) {
          callback(new Error("请输入图层名"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

const notifyMapReload = () => {
  $bus?.emit("reloadMapServices");
};

const getList = async () => {
  loading.value = true;
  try {
    const res = await listMapServices();
    tableData.value = Array.isArray(res) ? res : res?.results || [];
  } catch (e) {
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  editingId.value = null;
  formTitle.value = "新增接口";
  form.value = emptyForm();
  showFormDialog.value = true;
};

const openEdit = (row) => {
  editingId.value = row.id;
  formTitle.value = "编辑接口";
  form.value = {
    name: row.name || "",
    service_type: row.service_type || "wms",
    url: row.url || "",
    layers: row.layers || "",
    format: row.format || "image/png",
    tile_matrix_set_id: row.tile_matrix_set_id || "EPSG:4326",
    description: row.description || "",
    enabled: !!row.enabled,
    show_default: !!row.show_default,
    sort_order: row.sort_order ?? 0,
  };
  showFormDialog.value = true;
};

const handleSubmit = async () => {
  const el = formRef.value;
  if (!el) return;
  try {
    await el.validate();
  } catch {
    shakeInvalidFormFields(el);
    return;
  }
  try {
    if (editingId.value) {
      await updateMapService({ ...form.value, id: editingId.value });
      ElMessage.success("更新成功");
    } else {
      await createMapService(form.value);
      ElMessage.success("添加成功");
    }
    showFormDialog.value = false;
    await getList();
    notifyMapReload();
  } catch (e) {}
};

const handleToggleEnabled = async (row) => {
  try {
    await updateMapService({ ...row, enabled: row.enabled });
    notifyMapReload();
  } catch (e) {
    row.enabled = !row.enabled;
  }
};

const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除接口「${row.name}」?`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    customClass: "gotham-message-box",
  })
    .then(async () => {
      await deleteMapService(row.id);
      ElMessage.success("删除成功");
      await getList();
      notifyMapReload();
    })
    .catch(() => {});
};

const tableRowClassName = ({ rowIndex }) => (rowIndex % 2 === 0 ? "even-row" : "odd-row");

onMounted(() => {
  getList();
});
</script>

<style lang="scss" scoped>
@import "@/styles/gotham-panel.scss";

.results-panel__switch-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

:deep(.el-select .el-select__wrapper) {
  background: #07100b !important;
  border: 1px solid rgba(64, 73, 69, 0.5) !important;
  box-shadow: none !important;
  min-height: 40px;
}

:deep(.el-select .el-select__wrapper.is-focused),
:deep(.el-select .el-select__wrapper.is-hovering) {
  border-color: #9ddf2e !important;
  box-shadow: none !important;
}

:deep(.el-select .el-select__selected-item),
:deep(.el-select .el-select__placeholder),
:deep(.el-select .el-select__caret) {
  color: #dae5dc !important;
}

:deep(.el-select .el-select__placeholder) {
  color: rgba(192, 200, 195, 0.7) !important;
}
</style>
