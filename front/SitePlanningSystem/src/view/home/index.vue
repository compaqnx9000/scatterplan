<template>
  <div class="content_wrap">
    <!-- 固定在右侧的颜色条 -->
    <div
      class="fixed-color-bar"
      ref="fixedColorBar"
      v-show="activeBtnIndex === 1 || activeBtnIndex === 2 || showColorBarConfigurationDialog"
      :class="{ 'is-open': showColorBarConfigurationDialog }"
      title="点击配置传输损耗"
      @click="openLossConfigFromLegend"
    >
      <div class="color-bar-title">dB</div>
      <div class="color-bar-body">
        <div class="color-bar-gradient" :style="gradientStyle"></div>
        <div class="color-bar-scale">
          <div v-for="(scale, index) in scales" :key="index" class="scale-item">
            <div class="scale-line"></div>
            <div class="scale-text">{{ scale }}</div>
          </div>
        </div>
      </div>
      <button class="color-bar-gear" type="button" title="传输损耗配置" @click.stop="openLossConfigFromLegend">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M10.2 3.6h3.6l.5 2.2 2-.9 2.5 2.5-.9 2 2.2.5v3.6l-2.2.5.9 2-2.5 2.5-2-.9-.5 2.2h-3.6l-.5-2.2-2 .9-2.5-2.5.9-2L3.6 13.8v-3.6l2.2-.5-.9-2 2.5-2.5 2 .9.5-2.2Z"
            fill="none"
            stroke="currentColor"
            stroke-width="1.6"
            stroke-linejoin="round"
          />
          <circle cx="12" cy="12" r="2.2" fill="none" stroke="currentColor" stroke-width="1.6" />
        </svg>
      </button>
    </div>
    <!-- <ScreenshotTool></ScreenshotTool> -->
    <div v-if="showProfileProgressBar" class="screen-progress">
      <div class="progress-bar-wrapper">
        <div class="progress-label">链路计算</div>
        <el-progress :stroke-width="12" :percentage="profileProgressValue" :show-text="true" />
        <div class="progress-stop-btn" @click.stop="handleStopProgress">停止</div>
      </div>
    </div>
    <div v-if="showProgressBar" class="screen-progress">
      <div class="progress-bar-wrapper">
        <div class="progress-label">计算进度</div>
        <el-progress :stroke-width="12" :percentage="progressValue" :show-text="true" />
        <div class="progress-stop-btn" @click.stop="handleStopProgress">停止</div>
      </div>
    </div>

    <!-- <button @click="butAddTxtName('发射站点')">截图</button> -->
    <div ref="export_map_png" style="position: fixed;right: 200vw;">
      <img style="
              width: 1920px;
              height: 1080px;
            " :src="mapImg" alt="" />
      <img style="
              width: 140px;
              height: 340px;
              position: absolute;
                right: 20px;
  top: 50%;
  transform: translateY(-50%);
            " :src="color_line_png" alt="">
    </div>
    <!-- 新建工程 -->
    <NewProjectDialog
      :visible="showNewProjectDialog"
      @update:visible="(val) => (showNewProjectDialog = val)"
      @confirm="handleNewProjectConfirm"
    />

    <!-- 发射点配置 -->

    <LaunchSiteDialog :visible="visible" @update:isSelectStartPointOver="(val) => {
      isSelectStartPointOver = val;
    }" :drawLaunchSiteForm="drawLaunchSiteForm" @update:visible="(val) => {
      visible = val;
    }" />

    <!-- 单链路计算配置 -->
    <SLPComputeDialog :showSLPComputedDialog="showSLPComputedDialog" :SLPComputeForm="SLPComputeForm"
      @update:visible="(val) => (showSLPComputedDialog = val)" />

    <!-- 散射通信区覆盖区域配置 -->
    <CommunicationAreaDialog :showCommunicationAreaDialog="showCommunicationAreaDialog"
      :CommunicationArea="CommunicationArea" :CommunicationAreaProhibited="CommunicationAreaProhibited"
      :launchSite="{ lng: drawLaunchSiteForm.lng, lat: drawLaunchSiteForm.lat }"
      @update:visible="(val) => (showCommunicationAreaDialog = val)" />

    <!-- 剖面提取 -->
    <ProfileDialog
      :visible="showProfileDialog"
      :imageUrl="ProfileForm.image_url"
      :insights="ProfileForm"
      :form="linkageCalculationForm"
      :rxLng="SLPComputeForm.lng"
      :rxLat="SLPComputeForm.lat"
      :loading="loadingProfileDialog"
      @update:visible="handleProfileVisible"
      @export="handleExport"
      @changeCommRate="handleChangeCommRate"
    />

    <!-- 聚类分析及站点推荐列表查询参数 -->
    <ClusterAnalysisSearchDialog :showClusterAnalysisSearchDialog="showClusterAnalysisSearchDialog"
      :clusterAnalysisForm="clusterAnalysisForm" :clusterAnalysisFormRelay="clusterAnalysisFormRelay"
      :communicationAreaProhibitedForm="communicationAreaProhibitedForm"
      :id="CommunicationArea.activeName === 'Rectangle' ? rectangleArea_tif_id : circleArea_tif_id"
      :tif_path="CommunicationArea.activeName === 'Rectangle' ? rectangleArea_tif_url : circleArea_tif_url"
      @update:visible="(val) => (showClusterAnalysisSearchDialog = val)" />

    <!-- 聚类分析及站点推荐 / 中继站点列表 -->
    <transition name="station-fade">
      <div
        v-if="showClusterAnalysisDialog || showRelayClusterAnalysisDialog"
        ref="clusterResultPanelRef"
        class="results-panel"
        :style="clusterResultPanelStyle"
      >
        <div class="results-panel__panel">
          <div class="results-panel__edge"></div>
          <div class="results-panel__header" @mousedown="startClusterResultDrag">
            <div class="results-panel__heading">
              <div class="results-panel__badge">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M5 7h4v4H5zm5 0h4v4h-4zm5 0h4v4h-4zM7.5 14.5 5 19h14l-3.5-4.5-2.5 3z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div>
                <h2 class="results-panel__title">
                  {{ showRelayClusterAnalysisDialog ? "中继站点列表" : "聚类分析及站点推荐" }}
                </h2>
                <p class="results-panel__subtitle">
                  计算耗时：{{ showRelayClusterAnalysisDialog ? getRelayTableDataTime : getTableDataTime }}
                </p>
              </div>
            </div>
            <div class="results-panel__header-actions">
              <button
                v-show="showClusterAnalysisDialog && relayTableData.length"
                class="results-panel__btn results-panel__btn--ghost"
                type="button"
                @click="showClusterAnalysisDialog = false; showRelayClusterAnalysisDialog = true"
                @mousedown.stop
              >
                返回
              </button>
              <button
                class="results-panel__icon-btn"
                type="button"
                title="关闭"
                @click="closeClusterResultPanel"
                @mousedown.stop
              >
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
          </div>

          <div class="results-panel__body">
            <div class="results-panel__table">
              <el-table
                v-if="showClusterAnalysisDialog"
                height="320"
                :data="tableData"
                style="width: 100%"
                header-row-class-name="results-table-header"
                :row-style="{ height: '40px' }"
                :row-class-name="tableRowClassName"
              >
                <el-table-column label="序号" type="index" width="70" align="center" />
                <el-table-column label="站点编号" align="center" min-width="110">
                  <template #default="scope">
                    <el-input v-model="scope.row.number" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="站点名称" align="center" min-width="120">
                  <template #default="scope">
                    <el-input v-model="scope.row.name" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="接收点经度" align="center" min-width="120">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.longitude) }}
                  </template>
                </el-table-column>
                <el-table-column label="接收点纬度" align="center" min-width="120">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.latitude) }}
                  </template>
                </el-table-column>
                <el-table-column label="坡度（°）" align="center" min-width="90">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.slope) }}
                  </template>
                </el-table-column>
                <el-table-column label="道路距离（m）" align="center" min-width="110">
                  <template #default="scope">
                    {{ Number(scope.row.to_road_distance).toFixed(0) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" align="center" width="150" fixed="right">
                  <template #default="scope">
                    <div class="results-panel__row-actions">
                      <button class="results-panel__link" type="button" @click="handleApplySite(scope.row)">保存</button>
                      <button class="results-panel__link" type="button" @click="handleLinkageCalculation(scope.row)">链路计算</button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <el-table
                v-else
                height="320"
                :data="relayTableData"
                style="width: 100%"
                header-row-class-name="results-table-header"
                :row-style="{ height: '40px' }"
                :row-class-name="tableRowClassName"
              >
                <el-table-column label="序号" type="index" width="70" align="center" />
                <el-table-column label="站点编号" align="center" min-width="110">
                  <template #default="scope">
                    <el-input v-model="scope.row.number" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="站点名称" align="center" min-width="120">
                  <template #default="scope">
                    <el-input v-model="scope.row.name" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="接收点经度" align="center" min-width="120">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.longitude) }}
                  </template>
                </el-table-column>
                <el-table-column label="接收点纬度" align="center" min-width="120">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.latitude) }}
                  </template>
                </el-table-column>
                <el-table-column label="坡度（°）" align="center" min-width="90">
                  <template #default="scope">
                    {{ formatDecimal6(scope.row.slope) }}
                  </template>
                </el-table-column>
                <el-table-column label="道路距离（m）" align="center" min-width="110">
                  <template #default="scope">
                    {{ Number(scope.row.to_road_distance).toFixed(0) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" align="center" width="110" fixed="right">
                  <template #default="scope">
                    <div class="results-panel__row-actions">
                      <button class="results-panel__link" type="button" @click="handleRelaySiteCalculation(scope.row, scope.$index)">
                        站点计算
                      </button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <div class="results-panel__footer">
            <el-dropdown v-if="showClusterAnalysisDialog" trigger="click" :teleported="false" placement="top-end">
              <button class="results-panel__btn results-panel__btn--ghost" type="button">导出</button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleExportExcel">导出 Excel</el-dropdown-item>
                  <el-dropdown-item @click="handleExportImage">导出图片</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <button class="results-panel__btn results-panel__btn--primary" type="button" @click="closeClusterResultPanel">
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

    <!-- 传输损耗配置 -->
    <TransmissionLossConfigDialog
      :visible="showColorBarConfigurationDialog"
      :colorBarList="colorBarList"
      :radio="radio1"
      :selectIndex="selectIndex"
      :panelColor="panel_color"
      :thresholdStart="threshold_start"
      :thresholdEnd="threshold_end"
      :scales="scales"
      :btnLoading="btnloading"
      :canScreenshot="!!(circleArea_tif_url || rectangleArea_tif_url)"
      :canToggleLossMap="!!(rectangleArea_image_url || circleArea_image_url)"
      :lossMapVisible="lossMapVisible"
      @update:visible="(val) => (showColorBarConfigurationDialog = val)"
      @update:radio="(val) => (radio1 = val)"
      @update:selectIndex="(val) => (selectIndex = val)"
      @update:panelColor="(val) => (panel_color = val)"
      @update:thresholdStart="(val) => (threshold_start = val)"
      @update:thresholdEnd="(val) => (threshold_end = val)"
      @confirm="handleColorBarConfiguration"
      @screenshot="butAddTxtName('发射站点')"
      @toggleLossMap="handleToggleLossMap"
    />

    <!-- 单链路计算导出 -->
    <div ref="canvasBox" class="export-sheet">
      <h3 class="export-sheet__title">单链路输入</h3>
      <div class="export-sheet__grid">
        <div class="export-sheet__field"><span class="export-sheet__label">通信速率</span><span class="export-sheet__value">{{ linkageCalculationForm.comm_rate }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">调整系数</span><span class="export-sheet__value">{{ linkageCalculationForm.diversity_order }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射天线增益（dB）</span><span class="export-sheet__value">{{ linkageCalculationForm.tx_gain }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收天线增益（dB）</span><span class="export-sheet__value">{{ linkageCalculationForm.rx_gain }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">信号频率（MHz）</span><span class="export-sheet__value">{{ linkageCalculationForm.freq }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射功率（W）</span><span class="export-sheet__value">{{ linkageCalculationForm.trans_power }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射经度（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.lng }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射纬度（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.lat }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收经度（°）</span><span class="export-sheet__value">{{ SLPComputeForm.lng }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收纬度（°）</span><span class="export-sheet__value">{{ SLPComputeForm.lat }}</span></div>
      </div>
      <h3 class="export-sheet__title">单链路输出</h3>
      <div class="export-sheet__grid">
        <div class="export-sheet__field"><span class="export-sheet__label">通信距离（km）</span><span class="export-sheet__value">{{ linkageCalculationForm.distance }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">散射角（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.theta_scatter }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">区域类型</span><span class="export-sheet__value">{{ linkageCalculationForm.area }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">链路传播可靠度（%）</span><span class="export-sheet__value">{{ linkageCalculationForm.reliability }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射天线仰角（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.tx_theta }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射点障碍物距离（km）</span><span class="export-sheet__value">{{ linkageCalculationForm.tx_barrier_distance }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">路径损耗中值（dB）</span><span class="export-sheet__value">{{ linkageCalculationForm.median_loss }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收天线仰角（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.rx_theta }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收点障碍物距离（km）</span><span class="export-sheet__value">{{ linkageCalculationForm.rx_barrier_distance }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收功率（dBm）</span><span class="export-sheet__value">{{ linkageCalculationForm.recv_power }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射天线方位角（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.tx_azimuth }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">发射点障碍物高差（m）</span><span class="export-sheet__value">{{ linkageCalculationForm.tx_barrier_height }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">信号衰落余值（dB）</span><span class="export-sheet__value">{{ linkageCalculationForm.residual_value }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收天线方位角（°）</span><span class="export-sheet__value">{{ linkageCalculationForm.rx_azimuth }}</span></div>
        <div class="export-sheet__field"><span class="export-sheet__label">接收点障碍物高差（m）</span><span class="export-sheet__value">{{ linkageCalculationForm.rx_barrier_height }}</span></div>
      </div>
      <h3 class="export-sheet__title">剖面图</h3>
      <div class="export-sheet__image">
        <img v-if="linkageCalculationForm.image_url" :src="linkageCalculationForm.image_url + '?t=' + time" alt="剖面图" />
      </div>
    </div>

    <!-- 传输损耗预测导出 ，增加字间距 -->
    <div class="table_wrap" :style="{
      letterSpacing: '0.15rem',
      position: 'fixed',
      right: '200vw',
      width: '100%',
      padding: '30px',
    }" ref="tableWrapRef">
      <div class="table_content">
        <!-- 表格 -->
        <el-table :data="tableData" style="margin-top: 16px" border header-row-class-name="tableHeaderClassName"
          :row-style="{ height: '50px' }" :row-class-name="tableRowClassName">
          <el-table-column label="序号" type="index" width="100" align="center" />
          <el-table-column label="站点编号" align="center">
            <template #default="scope">
              <!-- 应用站点 -->
              <el-input v-model="scope.row.number" size="small" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="站点名称" align="center">
            <template #default="scope">
              <el-input v-model="scope.row.name" size="small" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column prop="lng" label="接收点经度" align="center">
            <template #default="scope">
              <span>{{ scope.row.longitude }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lat" label="接收点纬度" align="center">
            <template #default="scope">
              <span>{{ scope.row.latitude }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lat" label="坡度（°）" align="center">
            <template #default="scope">
              <span>{{ scope.row.slope }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="distance" label="道路距离（m）" align="center">
            <template #default="scope">
              <span>{{ scope.row.to_road_distance.toFixed(0) }}</span>
            </template>
          </el-table-column>
          <!-- 操作 -->
          <!-- 应用站点 -->
          <!-- <el-table-column class-name="small-padding fixed-width" label="操作" width="100" align="center">
            <template #default="scope">
              <div class="table_btn_wrap">
                <span class="table_btn_item view_btn" @click="handleApplySite(scope.row)">应用站点</span>
              </div>
            </template>
          </el-table-column> -->
        </el-table>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
//@ts-nocheck
import { getCurrentInstance, ref, watch, computed, nextTick, onMounted, onBeforeUnmount } from "vue";
import LaunchSiteDialog from "./component/LaunchSiteDialog.vue";
import NewProjectDialog from "./component/NewProjectDialog.vue";
import SLPComputeDialog from "./component/SLPComputedDialog.vue";
import ProfileDialog from "./component/ProfileDialog.vue";
import CommunicationAreaDialog from "./component/CommunicationAreaDialog.vue";
import ClusterAnalysisSearchDialog from "./component/ClusterAnalysisSearchDialog.vue";
import TransmissionLossConfigDialog from "./component/TransmissionLossConfigDialog.vue";
import $store from "@/store/index";

import * as mars3d from "mars3d";
// 导入 Cesium 核心库

// 导入echarts
import * as echarts from "echarts";
import { getMapInstance } from "@/assets/util/index";
import Main from "./service/main";
import { MAP_LABEL_FONT } from "./service/mapLabelStyle";

import { color } from "echarts";
import { getSingleLinkageImage, getClusterAnalysisList, useSite, exportExcel, setColorGenerateImage, getRecommendSiteList, saveRecommendSiteList, calculateReliability } from "@/request/home";
import { createProject, getProject } from "@/request/sitePlanting";
import { ElMessage, ElMessageBox } from "element-plus";
import { saveAs } from "file-saver";
import html2canvas from "html2canvas";

import ScreenshotTool from "@/components/ScreenshotTool/index.vue";
import { useRoute, useRouter } from 'vue-router';
import { formatDecimal6 } from "@/view/systemData/useGothamPanel";
import { parseLongitude, parseLatitude, formatLongitude, formatLatitude } from "@/view/home/service/rules";



import { image } from "html2canvas/dist/types/css/types/image";


const SingleLink = null

const activeIndex = ref(0);
// 发射点
const visible = ref(false);
const visible2 = ref(true);

const drawLaunchSiteForm = reactive({
  name: "",
  lng: "11.2345°\u00A0E",
  lat: "45.8321°\u00A0N",
  height: 10,
  tx_gain: "38",
  rx_gain: "38",
  freq: "4700",
  trans_power: "400",
  point_name: '',
  diversity_order: "8",
  comm_rate: "2.4kbps",
  climate_num: ''
});



// 单链路计算配置
const showSLPComputedDialog = ref(false);
const SLPComputeForm = reactive({
  lng: "",
  lat: "",
  point_name: '',
  height: 10,
});

// 散射通信区覆盖区域配置
const showCommunicationAreaDialog = ref(false);
const CommunicationArea = reactive({
  activeName: "Rectangle",
  initialPointLng: "",
  initialPointLat: "",
  destinationPointLng: "",
  destinationPointLat: "",
  centerPointLng: "",
  centerPointLat: "",
  radius: "",
});


// 散射通信区覆盖区域配置-禁止区域
const CommunicationAreaProhibited = reactive({
  activeProhibitedName: 'Rectangle',
  initialPointLng: '',
  initialPointLat: '',
  destinationPointLng: '',
  destinationPointLat: '',
  centerPointLng: '',
  centerPointLat: '',
  radius: '',
});



const time = ref(new Date().getTime());
let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;
let MapContainer: mars3d.Map;



const isSelectStartPointOver = ref(false);
const projectOpen = ref(false);
const currentProjectId = ref("");
const showNewProjectDialog = ref(false);
const railFullUnlock = ref(false);
const menuList = reactive([
  {
    name: "单链路计算适配",
    clickName: "showSLPComputedDialog",
    showChildren: false,
    children: [
      {
        name: "剖面提取",
        clickName: "profile",
      },
    ],
  },
  {
    name: "区域覆盖计算适配",
    clickName: "showCommunicationAreaDialog",
    showChildren: false,

    children: [
      {
        name: "传输损耗预测",
        clickName: "transmissionLossPrediction",
      },
    ],
  },
  {
    name: "聚类分析及站点推荐",
    clickName: "showClusterDialog",
    showChildren: false,

    children: [],
  },
]);
const activeBtnIndex = ref(0);
const graphicLayer = new mars3d.layer.GraphicLayer();
const showMenu = ref(false);
// 进度条响应式变量
const progressValue = ref(0);
const showProgressBar = ref(false);
const profileProgressValue = ref(0);
const showProfileProgressBar = ref(false);

// 剖面提取
const loadingProfileDialog = ref(false);
const showLinkageCalculationDialog = ref(false);
const emptyProfileReturn = () => ({
  cluster: false,
  relay: false,
  slp: false,
  launch: false,
  coverage: false,
  search: false,
});
const profileReturnTo = ref(emptyProfileReturn());

const snapshotProfileReturn = () => {
  profileReturnTo.value = {
    cluster: showClusterAnalysisDialog.value,
    relay: showRelayClusterAnalysisDialog.value,
    slp: showSLPComputedDialog.value,
    launch: visible.value,
    coverage: showCommunicationAreaDialog.value,
    search: showClusterAnalysisSearchDialog.value,
  };
};

const hasProfileReturn = () => Object.values(profileReturnTo.value).some(Boolean);

const clearProfileReturn = () => {
  profileReturnTo.value = emptyProfileReturn();
};

const restoreProfileReturn = () => {
  const s = profileReturnTo.value;
  if (s.cluster) showClusterAnalysisDialog.value = true;
  if (s.relay) showRelayClusterAnalysisDialog.value = true;
  if (s.slp) showSLPComputedDialog.value = true;
  if (s.launch) visible.value = true;
  if (s.coverage) showCommunicationAreaDialog.value = true;
  if (s.search) showClusterAnalysisSearchDialog.value = true;
  clearProfileReturn();
};

const handleProfileVisible = (val: boolean) => {
  showProfileDialog.value = val;
  if (!val) restoreProfileReturn();
};

const hasLinkResult = () =>
  hasFilled(linkageCalculationForm.distance) ||
  hasFilled(ProfileForm.image_url) ||
  hasFilled(linkageCalculationForm.image_url);
const showComputedLoading = ref(false);
const progressStopped = ref(false);
let profileWatchdogTimer: ReturnType<typeof setTimeout> | null = null;
let coverageWatchdogTimer: ReturnType<typeof setTimeout> | null = null;

const clearProfileWatchdog = () => {
  if (profileWatchdogTimer) {
    clearTimeout(profileWatchdogTimer);
    profileWatchdogTimer = null;
  }
};

const clearCoverageWatchdog = () => {
  if (coverageWatchdogTimer) {
    clearTimeout(coverageWatchdogTimer);
    coverageWatchdogTimer = null;
  }
};

/** 开始新任务：允许接收进度，并忽略旧 task 的残留消息 */
const armNewTask = (kind: "profile" | "coverage") => {
  progressStopped.value = false;
  $store.commit("setTaskId", "");
  if (kind === "profile") {
    clearProfileWatchdog();
    showComputedLoading.value = true;
    showProfileProgressBar.value = true;
    profileProgressValue.value = 2;
    profileWatchdogTimer = setTimeout(() => {
      if (!showProfileProgressBar.value || profileProgressValue.value > 2) return;
      hideProfileProgress();
      ElMessage.error("链路计算无响应，请刷新页面后重试");
    }, 20000);
  } else {
    clearCoverageWatchdog();
    showProgressBar.value = true;
    progressValue.value = 2;
    coverageWatchdogTimer = setTimeout(() => {
      if (!showProgressBar.value || progressValue.value > 2) return;
      showProgressBar.value = false;
      progressValue.value = 0;
      ElMessage.error("覆盖计算长时间无响应，请确认 Celery 服务是否在运行后重试");
    }, 120000);
  }
};

// 进度条停止
const handleStopProgress = () => {
  progressStopped.value = true;
  clearProfileWatchdog();
  clearCoverageWatchdog();
  showProgressBar.value = false;
  progressValue.value = 0;
  showProfileProgressBar.value = false;
  profileProgressValue.value = 0;
  showComputedLoading.value = false;
  $bus.emit("sendMessage", {
    'task_id': $store.state.taskId,
    'type': "stop_task",
  });
}
$bus.on("stopProgress", (payload?: { task_id?: string }) => {
  const incomingId = payload?.task_id;
  if (incomingId && $store.state.taskId && String(incomingId) !== String($store.state.taskId)) {
    return;
  }
  progressStopped.value = true;
  clearProfileWatchdog();
  clearCoverageWatchdog();
  showProgressBar.value = false;
  progressValue.value = 0;
  showProfileProgressBar.value = false;
  profileProgressValue.value = 0;
  showComputedLoading.value = false;
  if (activeBtnIndex.value === 1) {
    showDialog("showCommunicationAreaDialog", 1);
  }
});
$bus.on("taskStarted", (taskId) => {
  progressStopped.value = false;
  if (taskId) $store.commit("setTaskId", taskId);
});
// 链路计算
const handleConfirmLinkageCalculation = () => {

  ElMessageBox.confirm(
    '是否继续区域覆盖计算?',
    '提示',
    {
      confirmButtonText: '是',
      cancelButtonText: '否',
      type: 'warning',
      customClass: 'gotham-message-box',
      appendTo: document.body,
    }
  )
    .then(() => {
      showLinkageCalculationDialog.value = false;
      showDialog("showCommunicationAreaDialog", 1);
      $bus.emit("workflowActive", "coverage");
    })
    .catch(() => {
      showLinkageCalculationDialog.value = false;
    })
  // showLinkageCalculationDialog.value = false;
  // // 跳转站点规划


  // router.push({
  //   path: '/sitePlanning/sitePlanning',
  // })
  // handleExport();
  // showProfileDialog.value = true;
};
// 导出
const canvasBox = ref(null);

const handleExport = async () => {
  const el = canvasBox.value as HTMLElement | null;
  if (!el) return;
  await nextTick();
  const canvas = await html2canvas(el, {
    useCORS: true,
    backgroundColor: "#1a222c",
    scale: 2,
    logging: false,
    width: 1080,
    windowWidth: 1080,
  });
  const link = document.createElement("a");
  link.download = "图表.png";
  link.href = canvas.toDataURL("image/png");
  document.body.appendChild(link);
  link.click();
  link.remove();
};


const rectangleArea_tif_url = ref('');
const circleArea_tif_url = ref('');

const rectangleArea_image_url = ref('');
const circleArea_image_url = ref('');
const rectangleArea_tif_id = ref('');
const circleArea_tif_id = ref('');



// 聚类分析及站点推荐列表查询参数
const showClusterAnalysisSearchDialog = ref(false);
const clusterAnalysisForm = ref({
  loss_threshold: '150',
  limit_road_distance: '500',
  eps_cells: '500',
  min_samples: '10',
  p: '',
  // 矩形或圆形
  area_type: 'smallRectangle',
  // 矩形或圆形参数
  initialPointLng: '',
  initialPointLat: '',
  destinationPointLng: '',
  destinationPointLat: '',
  centerPointLng: '',
  centerPointLat: '',
  radius: '',
})
const clusterAnalysisFormRelay = ref({
  // 矩形或圆形
  area_type: 'relayRectangle',
  // 矩形或圆形参数
  initialPointLng: '',
  initialPointLat: '',
  destinationPointLng: '',
  destinationPointLat: '',
  centerPointLng: '',
  centerPointLat: '',
  radius: '',
})
const communicationAreaProhibitedForm = ref({
  activeProhibitedName: 'Rectangle',
  initialPointLng: '',
  initialPointLat: '',
  destinationPointLng: '',
  destinationPointLat: '',
  centerPointLng: '',
  centerPointLat: '',
  radius: '',
})


// 聚类分析及站点推荐列表查询
const btnloading = ref(false);

// 设置聚类分析及站点推荐列表

const setTableData = (data: any) => {
  console.log(data, "setTableData");
  if (!data.stations || data.stations.length === 0) {
    ElMessageBox.alert(
      data.stations_type === "relay stations" ? "中继站点为空" : "推荐站点为空",
      "提示",
      {
        confirmButtonText: "确定",
        type: "warning",
        customClass: "gotham-message-box",
        appendTo: document.body,
        closeOnClickModal: false,
        closeOnPressEscape: false,
        showClose: false,
      }
    );
    return;
  }
  if (data.stations_type === 'relay stations') {
    // 设置中继站点数据
    relayTableData.value = data.stations
    $bus.emit('addRelayClusterPoint', relayTableData.value)
    showRelayClusterAnalysisDialog.value = true;
    showClusterAnalysisDialog.value = false;

    getRelayTableDataTime.value = data.calculation_duration

  } else if (data.stations_type === 'recv stations') {
    // 设置推荐站点数据
    tableData.value = data.stations
    showClusterAnalysisDialog.value = true;
    showRelayClusterAnalysisDialog.value = false;

    getTableDataTime.value = data.calculation_duration
    $bus.emit('addClusterPoint', tableData.value)

  }


  // 遍历数据在地图上加点矢量

  showClusterAnalysisSearchDialog.value = false;
}

$bus.on('rectangleAreaClustering', setTableData)

const onOpenLaunchSiteConfig = () => {
  if (!projectOpen.value) {
    showNewProjectDialog.value = true;
    return;
  }
  showDialog("visible");
};
const onOpenSLPComputedDialog = () => {
  showDialog("showSLPComputedDialog", 0);
  $bus.emit("workflowActive", "slp");
};
const onOpenProfileExtract = () => {
  $bus.emit("workflowActive", "profile");
  if (hasLinkResult()) {
    showProfileDialog.value = true;
    return;
  }
  clickChildMenu("profile", 0);
};
const onOpenCoverageDialog = () => {
  showDialog("showCommunicationAreaDialog", 1);
  $bus.emit("workflowActive", "coverage");
};
const onRunTransmissionLossPrediction = () => {
  activeBtnIndex.value = 1;
  $bus.emit("workflowActive", "prediction");
  clickChildMenu("transmissionLossPrediction", 0);
};
const onOpenClusterDialog = () => {
  showDialog("showClusterDialog", 2);
  $bus.emit("workflowActive", "cluster");
};

const confirmResetSession = (action: "new" | "close") => {
  const isNew = action === "new";
  return ElMessageBox.confirm(
    isNew
      ? "将关闭当前工程并清空地图上的接收点、剖面、覆盖区和推荐站点，然后新建工程。已保存到服务器的记录不受影响。"
      : "将关闭当前工程并清空当前地图会话，回到登录后的初始状态。已保存到服务器的记录不受影响。",
    isNew ? "新建工程" : "关闭工程",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
      customClass: "gotham-message-box",
      appendTo: document.body,
    }
  );
};

const onRequestNewProject = async () => {
  if (projectOpen.value) {
    try {
      await confirmResetSession("new");
    } catch {
      return;
    }
    resetAppToInitial();
  }
  showNewProjectDialog.value = true;
};

const onRequestCloseProject = async () => {
  if (!projectOpen.value) return;
  try {
    await confirmResetSession("close");
  } catch {
    return;
  }
  resetAppToInitial();
};

const handleNewProjectConfirm = async (name: string) => {
  try {
    const res: any = await createProject({ name });
    currentProjectId.value = res.id;
    drawLaunchSiteForm.name = name;
    railFullUnlock.value = false;
    $bus.emit("workflowRailFull", false);
    projectOpen.value = true;
    showNewProjectDialog.value = false;
    emitWorkflowPointState();
  } catch (error: any) {
    const data = error?.response?.data;
    const msg = data?.name?.[0] || data?.msg || "创建工程失败";
    ElMessage.error(typeof msg === "string" ? msg : "创建工程失败");
  }
};

const bindHomeBus = () => {
  $bus.all?.delete?.("openLaunchSiteConfig");
  $bus.all?.delete?.("openSLPComputedDialog");
  $bus.all?.delete?.("openProfileExtract");
  $bus.all?.delete?.("openCoverageDialog");
  $bus.all?.delete?.("runTransmissionLossPrediction");
  $bus.all?.delete?.("openClusterDialog");
  $bus.all?.delete?.("requestNewProject");
  $bus.all?.delete?.("requestCloseProject");
  $bus.on("openLaunchSiteConfig", onOpenLaunchSiteConfig);
  $bus.on("openSLPComputedDialog", onOpenSLPComputedDialog);
  $bus.on("openProfileExtract", onOpenProfileExtract);
  $bus.on("openCoverageDialog", onOpenCoverageDialog);
  $bus.on("runTransmissionLossPrediction", onRunTransmissionLossPrediction);
  $bus.on("openClusterDialog", onOpenClusterDialog);
  $bus.on("requestNewProject", onRequestNewProject);
  $bus.on("requestCloseProject", onRequestCloseProject);
};

bindHomeBus();

const resetAppToInitial = () => {
  if ((route.path === "/" || route.name === "home") && route.query.project) {
    router.replace({ path: "/" });
  }
  visible.value = false;
  showSLPComputedDialog.value = false;
  showCommunicationAreaDialog.value = false;
  showLinkageCalculationDialog.value = false;
  showClusterAnalysisDialog.value = false;
  showRelayClusterAnalysisDialog.value = false;
  showColorBarConfigurationDialog.value = false;
  showProfileDialog.value = false;
  showClusterAnalysisSearchDialog.value = false;
  showNewProjectDialog.value = false;
  isSelectStartPointOver.value = false;
  projectOpen.value = false;
  railFullUnlock.value = false;
  currentProjectId.value = "";
  activeBtnIndex.value = 0;
  lossMapVisible.value = true;
  progressStopped.value = true;
  clearProfileWatchdog();
  clearCoverageWatchdog();
  showProgressBar.value = false;
  progressValue.value = 0;
  showComputedLoading.value = false;
  showProfileProgressBar.value = false;
  profileProgressValue.value = 0;
  profileReturnTo.value = emptyProfileReturn();
  handleRelayIndex.value = 0;
  relayPoint.value = [];
  SLPCompute_id.value = "";
  circleArea_tif_image_url.value = "";

  if ($store.state.taskId) {
    $bus.emit("sendMessage", {
      task_id: $store.state.taskId,
      type: "stop_task",
    });
    $store.commit("setTaskId", "");
  }

  Object.assign(drawLaunchSiteForm, {
    name: "",
    lng: "11.2345°\u00A0E",
    lat: "45.8321°\u00A0N",
    height: 10,
    tx_gain: "38",
    rx_gain: "38",
    freq: "4700",
    trans_power: "400",
    point_name: "",
    diversity_order: "8",
    comm_rate: "2.4kbps",
    climate_num: "",
  });
  Object.assign(SLPComputeForm, {
    lng: "",
    lat: "",
    point_name: "",
    height: 10,
  });
  Object.assign(CommunicationArea, {
    activeName: "Rectangle",
    initialPointLng: "",
    initialPointLat: "",
    destinationPointLng: "",
    destinationPointLat: "",
    centerPointLng: "",
    centerPointLat: "",
    radius: "",
  });
  Object.assign(CommunicationAreaProhibited, {
    activeProhibitedName: "Rectangle",
    initialPointLng: "",
    initialPointLat: "",
    destinationPointLng: "",
    destinationPointLat: "",
    centerPointLng: "",
    centerPointLat: "",
    radius: "",
  });
  Object.assign(clusterAnalysisForm.value, {
    loss_threshold: "150",
    limit_road_distance: "500",
    eps_cells: "500",
    min_samples: "10",
    p: "",
    area_type: "smallRectangle",
    initialPointLng: "",
    initialPointLat: "",
    destinationPointLng: "",
    destinationPointLat: "",
    centerPointLng: "",
    centerPointLat: "",
    radius: "",
  });
  Object.assign(clusterAnalysisFormRelay.value, {
    area_type: "relayRectangle",
    initialPointLng: "",
    initialPointLat: "",
    destinationPointLng: "",
    destinationPointLat: "",
    centerPointLng: "",
    centerPointLat: "",
    radius: "",
  });
  Object.assign(communicationAreaProhibitedForm.value, {
    activeProhibitedName: "Rectangle",
    initialPointLng: "",
    initialPointLat: "",
    destinationPointLng: "",
    destinationPointLat: "",
    centerPointLng: "",
    centerPointLat: "",
    radius: "",
  });
  Object.assign(ProfileForm, {
    image_url: "",
    samples: [],
    tx_height: 0,
    rx_height: 0,
    min_height: 0,
    max_height: 0,
    distance: 0,
    scatterer_height: 0,
    scatterer_distance: 0,
    scatterer_lon: 0,
    scatterer_lat: 0,
    tx_lng: 0,
    tx_lat: 0,
    tx_barrier_distance: 0,
    tx_barrier_elev: 0,
    tx_barrier_height: 0,
    rx_barrier_distance: 0,
    rx_barrier_elev: 0,
    rx_barrier_height: 0,
    median_loss: 0,
    residual_value: 0,
    reliability: 0,
    recv_power: 0,
  });
  Object.assign(linkageCalculationForm, {
    distance: "",
    median_loss: "",
    tx_theta: "",
    rx_theta: "",
    theta_scatter: "",
    area: "",
    image_url: "",
    elapsed: "",
  });
  rectangleArea_tif_url.value = "";
  circleArea_tif_url.value = "";
  rectangleArea_image_url.value = "";
  circleArea_image_url.value = "";
  rectangleArea_tif_id.value = "";
  circleArea_tif_id.value = "";
  tableData.value = [];
  relayTableData.value = [];
  graphicLayer.clear();
  $bus.emit("cancelDrawPoint");
  $bus.emit("mapPickMode", false);
  $bus.emit("clearAll");
  $bus.emit("resetMapView");
  $bus.emit("workflowStationReady", false);
  $bus.emit("workflowLinkReady", false);
  $bus.emit("workflowProfileReady", false);
  $bus.emit("workflowLinkAnalysisReady", false);
  $bus.emit("workflowRailFull", false);
  $bus.emit("workflowActive", "");
  $bus.emit("workflowProjectOpen", false);
  $bus.emit("workflowProjectName", "");
};

$bus.on("Logout", resetAppToInitial);

watch(
  () => projectOpen.value,
  (open) => {
    $bus.emit("workflowProjectOpen", !!open);
    $bus.emit("workflowProjectName", open ? (drawLaunchSiteForm.name || "") : "");
    if (!open) {
      railFullUnlock.value = false;
      $bus.emit("workflowRailFull", false);
    }
  },
  { immediate: true }
);

watch(
  () => currentProjectId.value,
  (id) => {
    $bus.emit("workflowProjectId", id || "");
  },
  { immediate: true }
);

watch(
  () => drawLaunchSiteForm.name,
  (name) => {
    if (projectOpen.value) $bus.emit("workflowProjectName", name || "");
  }
);

watch(
  () => showComputedLoading.value,
  (loading) => {
    $bus.emit('workflowProfileLoading', !!loading);
  }
);

const showDialog = (name: any, index: number) => {
  if (name !== "visible") {    
      activeBtnIndex.value = index;
  }
  switch (name) {
    case "visible":
      visible.value = true;
      showSLPComputedDialog.value = false;
      showCommunicationAreaDialog.value = false;
      showLinkageCalculationDialog.value = false;
      showClusterAnalysisDialog.value = false;
      showColorBarConfigurationDialog.value = false;
      showProfileDialog.value = false;
      showClusterAnalysisSearchDialog.value = false

      break;
    case "showSLPComputedDialog":
      visible.value = false;
      showSLPComputedDialog.value = true;
      showCommunicationAreaDialog.value = false;
      showLinkageCalculationDialog.value = false;
      showClusterAnalysisDialog.value = false;
      showColorBarConfigurationDialog.value = false;
      showProfileDialog.value = false;
      showClusterAnalysisSearchDialog.value = false

      break;
    case "showCommunicationAreaDialog":
      visible.value = false;
      showSLPComputedDialog.value = false;
      showCommunicationAreaDialog.value = true;
      showLinkageCalculationDialog.value = false;
      showClusterAnalysisDialog.value = false;
      showColorBarConfigurationDialog.value = false;
      showProfileDialog.value = false;
      showClusterAnalysisSearchDialog.value = false
      break;

    // visible.value = false;
    // showSLPComputedDialog.value = false;
    // showCommunicationAreaDialog.value = false;
    // showLinkageCalculationDialog.value = false;
    // showClusterAnalysisDialog.value = false;
    // showColorBarConfigurationDialog.value = false;
    case "showClusterDialog":
      if (CommunicationArea.activeName === "Rectangle") {
        // ElMessage.error("请选择圆形区域");
        if (
          CommunicationArea.initialPointLng &&
          CommunicationArea.initialPointLat &&
          CommunicationArea.destinationPointLng &&
          CommunicationArea.destinationPointLat
        ) {
          // showClusterAnalysisDialog.value = true;
          if (!rectangleArea_tif_url.value) {
            ElMessage.error("请先完成传输损耗预测");
            return;
          }
        } else {
          ElMessage.error("请输入完整信息");
          return;
        }
      } else if (CommunicationArea.activeName === "round" || CommunicationArea.activeName === "Round") {
        if (
          CommunicationArea.centerPointLng &&
          CommunicationArea.centerPointLat &&
          CommunicationArea.radius
        ) {
          if (!circleArea_tif_image_url.value) {
            ElMessage.error("请先完成传输损耗预测");
            return;
          }

          // showClusterAnalysisDialog.value = true;
        } else {
          ElMessage.error("请输入完整信息");
          return;
        }
      }

      visible.value = false;
      showSLPComputedDialog.value = false;
      showCommunicationAreaDialog.value = false;
      showLinkageCalculationDialog.value = false;
      showColorBarConfigurationDialog.value = false;
      showClusterAnalysisSearchDialog.value = true;
      showClusterAnalysisDialog.value = false
      break;
    default:
      break;
  }
};

const showProfileDialog = ref(false);
// 控制子菜单按钮点击
const ProfileForm = reactive({
  image_url: "",
  samples: [] as Array<[number, number]>,
  tx_height: 0,
  rx_height: 0,
  min_height: 0,
  max_height: 0,
  distance: 0,
  scatterer_height: 0,
  scatterer_distance: 0,
  scatterer_lon: 0,
  scatterer_lat: 0,
  tx_lng: 0,
  tx_lat: 0,
  tx_barrier_distance: 0,
  tx_barrier_elev: 0,
  tx_barrier_height: 0,
  rx_barrier_distance: 0,
  rx_barrier_elev: 0,
  rx_barrier_height: 0,
  median_loss: 0,
  residual_value: 0,
  reliability: 0,
  recv_power: 0,
});
let mapImg = ref('')
let color_line_png = ref('')
let export_map_png = ref(null)
const butAddTxtName = (name) => {
  // 动态的获取index
  const item = {
    name,
    center: MapContainer.getCameraView()
  }

  MapContainer
    .expImage({
      download: false,
      width: 1920,
      height: 1080
    })
    .then((result) => {
      item.img = result.image
      console.log('item', item);
      mapImg.value = item.img

      // 使用html2canvas 对mapImg 进行截图
      html2canvas(fixedColorBar.value).then(canvas => {
        // 转换为base64编码
        const base64 = canvas.toDataURL('image/png');
        console.log('base64', base64);

        color_line_png.value = base64;
      });
      setTimeout(() => {
        html2canvas(export_map_png.value).then(canvas => {
          // 转换为base64编码
          const base64 = canvas.toDataURL('image/png');
          // 下载
          const a = document.createElement('a');
          a.href = base64;
          a.download = 'map.png';
          a.click();
        });
      }, 1000);
      // const eventTarget = new mars3d.BaseClass()

    })
}


const fixedColorBar = ref(null)

const threshold_start = ref(100);
const threshold_end = ref(300);
const hasFilled = (value: unknown) => {
  if (value === 0 || value === "0") return true;
  if (value === null || value === undefined) return false;
  return String(value).trim() !== "";
};

const emitWorkflowPointState = () => {
  const linkReady =
    hasFilled(SLPComputeForm.lng) && hasFilled(SLPComputeForm.lat);
  const stationReady = !!isSelectStartPointOver.value;
  $bus.emit("workflowStationReady", stationReady);
  $bus.emit("workflowLinkReady", linkReady);
  $bus.emit("workflowProfileReady", stationReady && linkReady);
};

watch(
  () => [isSelectStartPointOver.value, SLPComputeForm.lng, SLPComputeForm.lat],
  () => {
    emitWorkflowPointState();
  },
  { immediate: true }
);

$bus.on("workflowRailStateRequest", () => {
  $bus.emit("workflowProjectOpen", !!projectOpen.value);
  $bus.emit("workflowRailFull", !!railFullUnlock.value);
  emitWorkflowPointState();
  $bus.emit(
    "workflowLinkAnalysisReady",
    !!(hasFilled(linkageCalculationForm.distance) || hasFilled(ProfileForm.image_url) || hasFilled(linkageCalculationForm.image_url))
  );
});

const hasRectangleArea = () =>
  hasFilled(CommunicationArea.initialPointLng) &&
  hasFilled(CommunicationArea.initialPointLat) &&
  hasFilled(CommunicationArea.destinationPointLng) &&
  hasFilled(CommunicationArea.destinationPointLat);

const hasRoundArea = () =>
  hasFilled(CommunicationArea.centerPointLng) &&
  hasFilled(CommunicationArea.centerPointLat) &&
  hasFilled(CommunicationArea.radius);

const projectFields = () => ({
  project_id: currentProjectId.value,
  project_name: drawLaunchSiteForm.name,
});

const startRectangleLossPrediction = (colors: string[]) => {
  let sendData: any = {
    id: rectangleArea_tif_id.value ? rectangleArea_tif_id.value : "",
    type: "rectangle area coverage",
    ...projectFields(),
    name: drawLaunchSiteForm.name,
    tx_gain: drawLaunchSiteForm.tx_gain,
    rx_gain: drawLaunchSiteForm.rx_gain,
    trans_power: drawLaunchSiteForm.trans_power,
    diversity_order: drawLaunchSiteForm.diversity_order,
    tx_lon: parseLongitude(drawLaunchSiteForm.lng),
    tx_lat: parseLatitude(drawLaunchSiteForm.lat),
    freq: drawLaunchSiteForm.freq,
    min_lon: parseLongitude(CommunicationArea.initialPointLng),
    min_lat: parseLatitude(CommunicationArea.initialPointLat),
    max_lon: parseLongitude(CommunicationArea.destinationPointLng),
    max_lat: parseLatitude(CommunicationArea.destinationPointLat),
    colors,
    min_val: threshold_start.value,
    max_val: threshold_end.value,
    comm_rate: drawLaunchSiteForm.comm_rate,
    tx_station_name: drawLaunchSiteForm.point_name,
    climate_num: drawLaunchSiteForm.climate_num,
  };
  if (CommunicationAreaProhibited.activeProhibitedName === "Rectangle" && CommunicationAreaProhibited.initialPointLng) {
    sendData = {
      ...sendData,
      prohibited_area_type: "rectangle",
      prohibited_min_lon: CommunicationAreaProhibited.initialPointLng,
      prohibited_min_lat: CommunicationAreaProhibited.initialPointLat,
      prohibited_max_lon: CommunicationAreaProhibited.destinationPointLng,
      prohibited_max_lat: CommunicationAreaProhibited.destinationPointLat,
    };
  } else if (
    (CommunicationAreaProhibited.activeProhibitedName === "Round" ||
      CommunicationAreaProhibited.activeProhibitedName === "round") &&
    CommunicationAreaProhibited.centerPointLng
  ) {
    sendData = {
      ...sendData,
      prohibited_area_type: "circle",
      prohibited_center_lon: CommunicationAreaProhibited.centerPointLng,
      prohibited_center_lat: CommunicationAreaProhibited.centerPointLat,
      prohibited_radius_m: CommunicationAreaProhibited.radius * 1000,
    };
  }
  armNewTask("coverage");
  $bus.emit("sendMessage", sendData);
};

const startRoundLossPrediction = (colors: string[]) => {
  armNewTask("coverage");
  $bus.emit("sendMessage", {
    type: "circle area coverage",
    id: circleArea_tif_id.value ? circleArea_tif_id.value : "",
    ...projectFields(),
    name: drawLaunchSiteForm.name,
    tx_gain: drawLaunchSiteForm.tx_gain,
    rx_gain: drawLaunchSiteForm.rx_gain,
    trans_power: drawLaunchSiteForm.trans_power,
    diversity_order: drawLaunchSiteForm.diversity_order,
    tx_lon: parseLongitude(drawLaunchSiteForm.lng),
    tx_lat: parseLatitude(drawLaunchSiteForm.lat),
    freq: drawLaunchSiteForm.freq,
    center_lon: parseLongitude(CommunicationArea.centerPointLng),
    center_lat: parseLatitude(CommunicationArea.centerPointLat),
    radius_m: CommunicationArea.radius * 1000,
    colors,
    min_val: threshold_start.value,
    max_val: threshold_end.value,
    comm_rate: drawLaunchSiteForm.comm_rate,
    tx_station_name: drawLaunchSiteForm.point_name,
  });
};


const clickChildMenu = async (name: any, index: number) => {
  activeIndex.value = index;
  switch (name) {
    case "profile":
      if (
        hasFilled(drawLaunchSiteForm.lng) &&
        hasFilled(drawLaunchSiteForm.lat) &&
        hasFilled(SLPComputeForm.lng) &&
        hasFilled(SLPComputeForm.lat)
      ) {
        armNewTask("profile");
        $bus.emit("wsReconnect");
        $bus.emit("sendMessage", {
          id: SLPCompute_id.value ? SLPCompute_id.value : '',
          ...projectFields(),
          name: drawLaunchSiteForm.name,
          link_name: "主链路",
          tx_lon: parseLongitude(drawLaunchSiteForm.lng),
          tx_lat: parseLatitude(drawLaunchSiteForm.lat),
          tx_height: drawLaunchSiteForm.height ? drawLaunchSiteForm.height : 0,
          rx_lon: parseLongitude(SLPComputeForm.lng),
          rx_lat: parseLatitude(SLPComputeForm.lat),
          rx_height: SLPComputeForm.height,
          tx_gain: drawLaunchSiteForm.tx_gain,
          rx_gain: drawLaunchSiteForm.rx_gain,
          freq: drawLaunchSiteForm.freq,
          trans_power: drawLaunchSiteForm.trans_power,
          diversity_order: drawLaunchSiteForm.diversity_order,
          rx_station_name: SLPComputeForm.point_name,
          tx_station_name: drawLaunchSiteForm.point_name,
          comm_rate: drawLaunchSiteForm.comm_rate,
          climate_num: drawLaunchSiteForm.climate_num
        });
      } else if (ProfileForm.image_url) {
        snapshotProfileReturn();
        showProfileDialog.value = true;
      } else {
        ElMessage.error("请先完成站点配置和单链路接收点");
      }

      break;

    case "transmissionLossPrediction": {
      const colors_2 = selectedColorBar.value.map((item) => item.color);
      const preferRound =
        CommunicationArea.activeName === "Round" || CommunicationArea.activeName === "round";
      if (preferRound && hasRoundArea()) {
        startRoundLossPrediction(colors_2);
      } else if (hasRectangleArea()) {
        startRectangleLossPrediction(colors_2);
      } else if (hasRoundArea()) {
        startRoundLossPrediction(colors_2);
      } else {
        ElMessage.error("请先在区域覆盖中绘制或填写计算区域");
      }
      return;
    }
    case "colorBarConfiguration":
      openLossConfigFromLegend();
      break;
    default:
      break;
  }
};

const linkageCalculationForm = reactive({
  distance: "",
  median_loss: "",
  tx_theta: "",
  rx_theta: "",
  theta_scatter: "",
  area: "",
  image_url: "",
  elapsed: "",
});



// 传输损耗预测
watch(() => activeBtnIndex.value, (newVal, oldVal) => {
  // const query = route.query;
  // if (query.type) { return }
  if ((oldVal === 0 && newVal !== 0)) {
    // 先获取所有图形的副本
    $bus.emit('HideAllSLPCompute')
    $bus.emit('showAllCommunicationArea', { activeName: CommunicationArea.activeName, area_type: clusterAnalysisForm.value.area_type })
  } else if (oldVal !== 0 && newVal === 0) {
    $bus.emit('HideAllCommunicationArea')
    $bus.emit('showAllSLPCompute')
  }
});

// 设置单链分析表单数据
const setSingleLinkFormData = (message: any) => {
  clearProfileWatchdog();
  showComputedLoading.value = false;
  showProfileProgressBar.value = false;
  profileProgressValue.value = 0;
  SLPCompute_id.value = message.id
  if (SLPComputeForm.lng && SLPComputeForm.lat) {
    $bus.emit('setSingleLink', {
      startPoint: [parseLongitude(drawLaunchSiteForm.lng), parseLatitude(drawLaunchSiteForm.lat), drawLaunchSiteForm.height],
      endPoint: [parseLongitude(SLPComputeForm.lng), parseLatitude(SLPComputeForm.lat), SLPComputeForm.height],
      ...message
    });
  }

  linkageCalculationForm.distance = message.distance; //距离
  linkageCalculationForm.median_loss = message.median_loss; //中值损失
  linkageCalculationForm.residual_value = message.residual_value; //信号衰落余值
  linkageCalculationForm.reliability = message.reliability; //可靠度
  linkageCalculationForm.tx_theta = message.tx_theta; //发射角度
  linkageCalculationForm.rx_theta = message.rx_theta; //接收角度
  linkageCalculationForm.tx_azimuth = message.tx_azimuth; //发射方位角
  linkageCalculationForm.rx_azimuth = message.rx_azimuth; //接收方位角
  linkageCalculationForm.theta_scatter = message.theta_scatter; //散射角
  linkageCalculationForm.recv_power = message.recv_power; //接收功率
  linkageCalculationForm.area = message.area; //面积
  linkageCalculationForm.image_url = message.image_url; //图片
  linkageCalculationForm.comm_rate = message.comm_rate; //通信速率（Mbps）：
  linkageCalculationForm.rx_barrier_distance = message.rx_barrier_distance; //接收站点距障碍点距离（M）：
  linkageCalculationForm.tx_barrier_distance = message.tx_barrier_distance; //发射站点距障碍点距离（M）：
  linkageCalculationForm.tx_barrier_height = message.tx_barrier_height; //发射站点距障碍点高度差（M）：
  linkageCalculationForm.rx_barrier_height = message.rx_barrier_height; //接收站点距障碍点高度差（M）：

  // 获取发射点配置数据进行回显

  linkageCalculationForm.diversity_order = drawLaunchSiteForm.diversity_order; //调整系数：
  linkageCalculationForm.tx_gain = drawLaunchSiteForm.tx_gain; //发射天线增益（dB）：
  linkageCalculationForm.rx_gain = drawLaunchSiteForm.rx_gain; //接受天线增益（dB）：
  linkageCalculationForm.freq = drawLaunchSiteForm.freq; //信号频率（MHz）：
  linkageCalculationForm.trans_power = drawLaunchSiteForm.trans_power; //发射功率（W）：
  linkageCalculationForm.lng = parseLongitude(drawLaunchSiteForm.lng); //发射站经度（°）：
  linkageCalculationForm.lat = parseLatitude(drawLaunchSiteForm.lat); //发射站纬度

  // linkageCalculationForm.elapsed = message.elapsed;//时间

  ProfileForm.image_url = message.image_url + '?t=' + new Date().getTime();
  ProfileForm.samples = Array.isArray(message.profile_samples) ? message.profile_samples : [];
  ProfileForm.tx_height = Number(message.tx_height) || 0;
  ProfileForm.rx_height = Number(message.rx_height) || 0;
  ProfileForm.min_height = Number(message.min_height) || 0;
  ProfileForm.max_height = Number(message.max_height) || 0;
  ProfileForm.distance = Number(message.distance) || 0;
  ProfileForm.scatterer_height = Number(message.scatterer_height) || 0;
  ProfileForm.scatterer_lon = Number(message.scatterer_lon) || 0;
  ProfileForm.scatterer_lat = Number(message.scatterer_lat) || 0;
  ProfileForm.tx_lng = parseLongitude(drawLaunchSiteForm.lng) || 0;
  ProfileForm.tx_lat = parseLatitude(drawLaunchSiteForm.lat) || 0;
  ProfileForm.scatterer_distance = Number(message.scatterer_distance) || 0;
  ProfileForm.tx_barrier_distance = Number(message.tx_barrier_distance) || 0;
  ProfileForm.tx_barrier_height = Number(message.tx_barrier_height) || 0;
  ProfileForm.tx_barrier_elev = Number(message.tx_barrier_elev) || 0;
  ProfileForm.rx_barrier_distance = Number(message.rx_barrier_distance) || 0;
  ProfileForm.rx_barrier_height = Number(message.rx_barrier_height) || 0;
  ProfileForm.rx_barrier_elev = Number(message.rx_barrier_elev) || 0;
  ProfileForm.median_loss = Number(message.median_loss) || 0;
  ProfileForm.residual_value = Number(message.residual_value) || 0;
  ProfileForm.reliability = Number(message.reliability) || 0;
  ProfileForm.recv_power = Number(message.recv_power) || 0;
  if (!hasProfileReturn()) snapshotProfileReturn();
  $bus.emit("workflowLinkAnalysisReady", true);
  showProfileDialog.value = true;

  visible.value = false;
  showSLPComputedDialog.value = false;
  showCommunicationAreaDialog.value = false;
  showLinkageCalculationDialog.value = false;
  showClusterAnalysisDialog.value = false;
  showColorBarConfigurationDialog.value = false;
  showClusterAnalysisSearchDialog.value = false

  // loadingProfileDialog.value = false;
}

$bus.on("singlelink", setSingleLinkFormData);

const isActiveTaskMessage = (taskId?: string) => {
  if (progressStopped.value) return false;
  const current = $store.state.taskId;
  // 新任务已启动、task_started 尚未到达时，先放行进度
  if (!current) return true;
  if (!taskId) return true;
  return String(taskId) === String(current);
};

const updateProfileProgressBar = (payload: any) => {
  const value = Number(payload?.progress ?? payload);
  if (!isActiveTaskMessage(payload?.task_id)) return;
  if (Number.isNaN(value)) return;
  clearProfileWatchdog();
  showProfileProgressBar.value = true;
  profileProgressValue.value = Number(value.toFixed(2));
  if (value >= 100) {
    showProfileProgressBar.value = false;
  }
};
$bus.on("singlelinkProgress", updateProfileProgressBar);

const hideProfileProgress = () => {
  clearProfileWatchdog();
  showComputedLoading.value = false;
  showProfileProgressBar.value = false;
  profileProgressValue.value = 0;
};
$bus.on("closeLoading", hideProfileProgress);

// 更新进度条
const updateProgressBar = (payload: any) => {
  const value = Number(payload?.progress ?? payload);
  if (!isActiveTaskMessage(payload?.task_id)) return;
  if (Number.isNaN(value)) return;
  clearCoverageWatchdog();
  showProgressBar.value = true;
  progressValue.value = Number(value.toFixed(2));
  if (value >= 100) {
    showProgressBar.value = false;
  }
}
$bus.on("coverageProgress", updateProgressBar)

const circleArea_tif_image_url = ref('');
// 更新圆形区域图片
const updateCircleAreaImg = (message: any) => {
  if (!isActiveTaskMessage(message.task_id)) return;
  console.log("circleArea", message.png_image_url);
  circleArea_tif_image_url.value = message.tif_image_url;
  circleArea_tif_url.value = message.tif_image_url;
  message.png_image_url = message.png_image_url + '?t=' + new Date().getTime();
  circleArea_image_url.value = message.png_image_url;
  circleArea_tif_id.value = message.id;
  $bus.emit('setCircleAreaImg', {
    ...message,
    centerPoint: [parseLongitude(CommunicationArea.centerPointLng), parseLatitude(CommunicationArea.centerPointLat)],
    radius: CommunicationArea.radius
  })
  showProgressBar.value = false
  lossMapVisible.value = true
}
$bus.on("circleArea", updateCircleAreaImg)


// 更新矩形区域图片
const updateRectangleAreaImg = (message: any) => {
  if (!isActiveTaskMessage(message.task_id)) return;
  console.log("rectangleArea", message);
  rectangleArea_tif_url.value = message.tif_image_url;
  rectangleArea_image_url.value = message.png_image_url + '?t=' + new Date().getTime();

  rectangleArea_tif_id.value = message.id;
  $bus.emit('setRectangleAreaImg', {
    ...message,
    initialPoint: [parseLongitude(CommunicationArea.initialPointLng), parseLatitude(CommunicationArea.initialPointLat)],
    destinationPoint: [parseLongitude(CommunicationArea.destinationPointLng), parseLatitude(CommunicationArea.destinationPointLat)],
  })
  showProgressBar.value = false
  lossMapVisible.value = true
}
$bus.on("rectangleArea", updateRectangleAreaImg)

// 切换损耗图显示/隐藏
const lossMapVisible = ref(true);
const toggleRectangleImg = () => {
  handleToggleLossMap(!lossMapVisible.value);
};
const handleToggleLossMap = (visible: boolean) => {
  lossMapVisible.value = !!visible;
  $bus.emit("toggleRectangleImg", lossMapVisible.value);
};

// 聚类分析及站点推荐
const showClusterAnalysisDialog = ref(false);
const showRelayClusterAnalysisDialog = ref(false);
const tableData = ref([

]);
const relayTableData = ref([

]);

const getTableDataTime = ref(null)
const getRelayTableDataTime = ref(null)

const clusterResultPanelRef = ref<HTMLElement | null>(null);
const clusterResultPanelPos = ref({ x: 24, y: 72 });
const clusterResultDragging = ref(false);
const clusterResultDragOffset = ref({ x: 0, y: 0 });
const CLUSTER_RESULT_PANEL_WIDTH = 1180;

const clusterResultPanelStyle = computed(() => ({
  left: `${clusterResultPanelPos.value.x}px`,
  top: `${clusterResultPanelPos.value.y}px`,
  width: `${Math.min(CLUSTER_RESULT_PANEL_WIDTH, window.innerWidth - 48)}px`,
}));

const getClusterResultDefaultPos = (size?: { width: number; height: number }) => {
  const width = size?.width ?? Math.min(CLUSTER_RESULT_PANEL_WIDTH, window.innerWidth - 48);
  const height = size?.height ?? 560;
  return {
    x: Math.max(24, Math.round((window.innerWidth - width) / 2)),
    y: Math.max(72, Math.round((window.innerHeight - height) / 2)),
  };
};

const centerClusterResultPanel = async () => {
  clusterResultPanelPos.value = getClusterResultDefaultPos();
  await nextTick();
  const el = clusterResultPanelRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  clusterResultPanelPos.value = getClusterResultDefaultPos({ width: rect.width, height: rect.height });
};

const startClusterResultDrag = (e: MouseEvent) => {
  if (e.button !== 0) return;
  clusterResultDragging.value = true;
  clusterResultDragOffset.value = {
    x: e.clientX - clusterResultPanelPos.value.x,
    y: e.clientY - clusterResultPanelPos.value.y,
  };
  window.addEventListener("mousemove", onClusterResultDrag);
  window.addEventListener("mouseup", stopClusterResultDrag);
};

const onClusterResultDrag = (e: MouseEvent) => {
  if (!clusterResultDragging.value) return;
  const width = Math.min(CLUSTER_RESULT_PANEL_WIDTH, window.innerWidth - 48);
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(0, window.innerHeight - 80);
  clusterResultPanelPos.value = {
    x: Math.min(maxX, Math.max(0, e.clientX - clusterResultDragOffset.value.x)),
    y: Math.min(maxY, Math.max(0, e.clientY - clusterResultDragOffset.value.y)),
  };
};

const stopClusterResultDrag = () => {
  clusterResultDragging.value = false;
  window.removeEventListener("mousemove", onClusterResultDrag);
  window.removeEventListener("mouseup", stopClusterResultDrag);
};

const closeClusterResultPanel = () => {
  showClusterAnalysisDialog.value = false;
  showRelayClusterAnalysisDialog.value = false;
};

const onClusterResultEsc = (e: KeyboardEvent) => {
  if (e.key !== "Escape") return;
  if (!showClusterAnalysisDialog.value && !showRelayClusterAnalysisDialog.value) return;
  closeClusterResultPanel();
};

watch(
  () => showClusterAnalysisDialog.value || showRelayClusterAnalysisDialog.value,
  (open) => {
    if (open) centerClusterResultPanel();
  }
);

const handleInput = (type, scope) => {
  alert('事件触发了！')
  console.log('当前行数据:', type, scope.row);
  // 这里可以直接通过 row.site_name 获取最新值（因为v-model已经双向绑定）
};


// 监听tableData变化
watch(() => tableData.value, (newVal, oldVal) => {
  $bus.emit('setClusterPoint', newVal);
}, { deep: true }); // 必须开启深度监听

// 表格行类名
const tableRowClassName = ({ rowIndex }: { rowIndex: number }) => {
  if (rowIndex % 2 === 0) {
    return "even-row";
  } else {
    return "odd-row";
  }
};

const tableWrapRef = ref(null);
const handleExportExcel = async () => {
  try {
    const data = await exportExcel({
      id: CommunicationArea.activeName === "Rectangle" ? rectangleArea_tif_id.value : circleArea_tif_id.value,
      cluster_stats: tableData.value,
    });
    // 错误时后端返回 JSON，responseType=blob 下需先识别
    if (data instanceof Blob && data.type && data.type.includes("application/json")) {
      const text = await data.text();
      const err = JSON.parse(text);
      ElMessage.error(err.error || err.message || "导出失败");
      return;
    }
    const blob = data instanceof Blob ? data : new Blob([data]);
    const stamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
    saveAs(blob, `stations_${stamp}.xlsx`);
  } catch (error) {
    ElMessage.error("导出失败");
  }
};
const handleExportImage = () => {
  console.log("tableWrapRef", tableWrapRef.value);
  html2canvas(tableWrapRef.value, {
    useCORS: true, // 允许加载跨域图片（需服务器配合CORS）
  }).then(function (canvas) {
    var img = canvas
      .toDataURL("image/png")
      .replace("image/png", "image/octet-stream");
    var creatIMg = document.createElement("a");
    creatIMg.download = "聚类分析及站点推荐.png";
    creatIMg.href = img;
    document.body.appendChild(creatIMg);
    creatIMg.click();
    creatIMg.remove();
  });
};


// 通信速率改变时，更新接收站点距障碍点高度差（M）：
const handleChangeCommRate = async (val) => {
  // alert(val)
  // linkageCalculationForm.rx_barrier_height = val === '2.4kbps' ? 0 : 10;
  try {
    const res = await calculateReliability({
      id: SLPCompute_id.value,
      comm_rate: linkageCalculationForm.comm_rate,
    })
    linkageCalculationForm.reliability = res.reliability;
    linkageCalculationForm.residual_value = res.residual_value;
    linkageCalculationForm.recv_power = res.recv_power;
    ProfileForm.reliability = Number(res.reliability) || 0;
    ProfileForm.residual_value = Number(res.residual_value) || 0;
    ProfileForm.recv_power = Number(res.recv_power) || 0;

    ElMessage.success("计算成功");
  } catch (error) {
    ElMessage.error("计算失败");
  }
}

// 色条配置
const showColorBarConfigurationDialog = ref(false);

const openLossConfigFromLegend = () => {
  if (showColorBarConfigurationDialog.value) {
    showColorBarConfigurationDialog.value = false;
    return;
  }
  visible.value = false;
  showSLPComputedDialog.value = false;
  showCommunicationAreaDialog.value = false;
  showLinkageCalculationDialog.value = false;
  showClusterAnalysisDialog.value = false;
  showClusterAnalysisSearchDialog.value = false;
  showColorBarConfigurationDialog.value = true;
};
const radio1 = ref(0);
const selectIndex = ref("1-1");

const makePalette = (row: number, colors: string[]) => ({
  colors: colors.map((color, i) => ({ index: `${row}-${i + 1}`, color })),
});

const colorBarList = reactive([
  makePalette(1, ["#01A7F0", "#4B7902", "#70B603", "#95F204", "#F59A23", "#FFFF80", "#D9001B"]),
  makePalette(2, ["#4b0076", "#0000ff", "#00ffff", "#00ff00", "#ffff00", "#ff7f00", "#ff0000"]),
  makePalette(3, ["#0000ff", "#00ffff", "#00ff00", "#ffff00", "#ff7f00", "#ff0000", "#800000"]),
  makePalette(4, ["#3b4cc0", "#688aef", "#9abbff", "#dddcdc", "#f7a385", "#dd3c4a", "#b40426"]),
  makePalette(5, ["#0000aa", "#0066ff", "#00ccff", "#66ff66", "#ffff00", "#ff6600", "#cc0000"]),
  makePalette(6, ["#000004", "#280b53", "#65156e", "#9f2a63", "#d44842", "#f57d15", "#fcffa4"]),
  makePalette(7, ["#000004", "#2c115f", "#721f81", "#b73779", "#f1605d", "#feae76", "#fcfdbf"]),
  makePalette(8, ["#0d0887", "#5c01a6", "#9c179e", "#cc4778", "#ed7953", "#fdb32f", "#f0f921"]),
  makePalette(9, ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151", "#bddf26", "#fde725"]),
  makePalette(10, ["#30123b", "#4676ed", "#1ae4b6", "#a2fc3c", "#f8ba39", "#e4460a", "#7a0403"]),
  makePalette(11, ["#0066cc", "#00cccc", "#66cc66", "#cccc33", "#cc9933", "#996633", "#ffffff"]),
  makePalette(12, ["#0b1a4a", "#123c7a", "#1e6e8f", "#3aa37a", "#c2b86a", "#c48a4a", "#f2efe6"]),
  makePalette(13, ["#081d58", "#1d4e89", "#2b8cbe", "#7fcdbb", "#c7e9b4", "#edf8b1", "#ffffd9"]),
  makePalette(14, ["#8c510a", "#d8b365", "#f6e8c3", "#f5f5f5", "#c7eae5", "#5ab4ac", "#01665e"]),
  makePalette(15, ["#a50026", "#d73027", "#f46d43", "#fee08b", "#a6d96a", "#1a9850", "#006837"]),
  makePalette(16, ["#d73027", "#fc8d59", "#fee08b", "#ffffbf", "#d9ef8b", "#91cf60", "#1a9850"]),
  makePalette(17, ["#543005", "#bf812d", "#f6e8c3", "#f5f5f5", "#c7eae5", "#35978f", "#003c30"]),
  makePalette(18, ["#7b3294", "#c2a5cf", "#e7d4e8", "#f7f7f7", "#d9f0d3", "#7fbf7b", "#008837"]),
  makePalette(19, ["#2166ac", "#67a9cf", "#d1e5f0", "#f7f7f7", "#fddbc7", "#ef8a62", "#b2182b"]),
  makePalette(20, ["#0000ff", "#4d4dff", "#9999ff", "#ffffff", "#ff9999", "#ff4d4d", "#ff0000"]),
  makePalette(21, ["#00aa00", "#55cc55", "#aaeeaa", "#ffffff", "#eeaacc", "#cc5599", "#aa0066"]),
  makePalette(22, ["#0066ff", "#66aaff", "#cce6ff", "#ffffff", "#ffcce6", "#ff66aa", "#ff0066"]),
  makePalette(23, ["#00aa00", "#55cc55", "#aaeeaa", "#ffffff", "#ffaaaa", "#ff5555", "#cc0000"]),
  makePalette(24, ["#4b0082", "#7b2cbf", "#c77dff", "#e0aaff", "#ff6b6b", "#e03131", "#9b111e"]),
  makePalette(25, ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c"]),
  makePalette(26, ["#f7fcf0", "#e0f3db", "#ccebc5", "#a8ddb5", "#7bccc4", "#43a2ca", "#0868ac"]),
  makePalette(27, ["#fff7ec", "#fee8c8", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"]),
  makePalette(28, ["#f7fcfd", "#e0ecf4", "#bfd3e6", "#9ebcda", "#8c96c6", "#8856a7", "#810f7c"]),
  makePalette(29, ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8"]),
  makePalette(30, ["#00204d", "#2c3a6f", "#4d536e", "#6e6d6a", "#958f6e", "#c4b96a", "#ffe945"]),
  makePalette(31, ["#000000", "#2a2a2a", "#555555", "#808080", "#aaaaaa", "#d5d5d5", "#ffffff"]),
  makePalette(32, ["#ffffff", "#d5d5d5", "#aaaaaa", "#808080", "#555555", "#2a2a2a", "#000000"]),
]);

const panel_color = ref("rgba(255, 69, 0, 0.68)");


// 颜色条相关响应式变量 threshold_start-threshold_end 等分6段 取整
const color_line = computed(() => {
  const setpArr = [
    threshold_start.value,
    Math.round(Number(threshold_start.value) + (threshold_end.value - threshold_start.value) / 6),
    Math.round(Number(threshold_start.value) + (threshold_end.value - threshold_start.value) * 2 / 6),
    Math.round(Number(threshold_start.value) + (threshold_end.value - threshold_start.value) * 3 / 6),
    Math.round(Number(threshold_start.value) + (threshold_end.value - threshold_start.value) * 4 / 6),
    Math.round(Number(threshold_start.value) + (threshold_end.value - threshold_start.value) * 5 / 6),
    threshold_end.value,
  ]
  console.log('setpArr', setpArr);

  return setpArr
})

console.log('color_line', color_line.value);

const scales = color_line; // 数字刻度线

// 监听 radio1 的变化，修改 selectedColorBar 的值
watch(
  () => radio1.value,
  (newValue) => {
    selectedColorBar.value = [...colorBarList[newValue].colors];
  }
);

watch(
  () => panel_color.value,
  (newvalue) => {
    if (!selectIndex.value) {
      return;
    }
    // 修复：通过.value访问ref对象的值
    colorBarList[Number(selectIndex.value.split("-")[0]) - 1].colors[
      Number(selectIndex.value.split("-")[1]) - 1
    ].color = newvalue;

    // 如果修改的是当前选中的颜色条，同步更新selectedColorBar
    if (radio1.value === Number(selectIndex.value.split("-")[0]) - 1) {
      selectedColorBar.value = [...colorBarList[radio1.value].colors];
    }
  }
);
const predefineColors = [
  "#ff4500",
  "#ff8c00",
  "#ffd700",
  "#90ee90",
  "#00ced1",
  "#1e90ff",
  "#c71585",
  "rgba(255, 69, 0, 0.68)",
  "rgb(255, 120, 0)",
  "hsv(51, 100, 98)",
  "hsva(120, 40, 94, 0.5)",
  "hsl(181, 100%, 37%)",
  "hsla(209, 100%, 56%, 0.73)",
  "#c7158577",
];


const stripUrlQuery = (url = "") => String(url || "").split("?")[0];

const isCircleCoverage = () =>
  CommunicationArea.activeName === "Round" || CommunicationArea.activeName === "round";

const getLossOverlayRef = () => {
  const circle = {
    isCircle: true,
    id: circleArea_tif_id.value,
    pngPath: circleArea_image_url.value,
    tifPath: circleArea_tif_url.value || circleArea_tif_image_url.value,
  };
  const rectangle = {
    isCircle: false,
    id: rectangleArea_tif_id.value,
    pngPath: rectangleArea_image_url.value,
    tifPath: rectangleArea_tif_url.value,
  };
  const preferred = isCircleCoverage() ? circle : rectangle;
  const fallback = isCircleCoverage() ? rectangle : circle;
  if (preferred.id && preferred.pngPath && preferred.tifPath) return preferred;
  if (fallback.id && fallback.pngPath && fallback.tifPath) return fallback;
  return preferred;
};

const recolorLossOverlay = async (colors: string[], minVal: number, maxVal: number) => {
  const overlay = getLossOverlayRef();
  const pngPath = stripUrlQuery(overlay.pngPath);
  const tifPath = stripUrlQuery(overlay.tifPath);
  if (!overlay.id || !pngPath || !tifPath || !colors?.length) {
    return false;
  }

  await setColorGenerateImage({
    id: overlay.id,
    png_path: pngPath,
    tif_path: tifPath,
    colors,
    min_val: minVal,
    max_val: maxVal,
  });

  const displayUrl = `${pngPath}?t=${Date.now()}`;
  if (overlay.isCircle) {
    circleArea_image_url.value = displayUrl;
  } else {
    rectangleArea_image_url.value = displayUrl;
  }

  $bus.emit("setAreaPng", {
    png_image_url: displayUrl,
    tif_image_url: displayUrl,
    type: overlay.isCircle ? "round" : "Rectangle",
    initialPoint: [parseLongitude(CommunicationArea.initialPointLng), parseLatitude(CommunicationArea.initialPointLat)],
    destinationPoint: [parseLongitude(CommunicationArea.destinationPointLng), parseLatitude(CommunicationArea.destinationPointLat)],
    centerPoint: [parseLongitude(CommunicationArea.centerPointLng), parseLatitude(CommunicationArea.centerPointLat)],
    radius: CommunicationArea.radius,
  });
  lossMapVisible.value = true;
  return true;
};

// 颜色配置：点选只改对话框预览，确认后才更新图例并重着色地图
const applyColorBarToMap = async (closeDialog = true) => {
  const palette = colorBarList[radio1.value]?.colors;
  const colors = palette?.length
    ? palette.map((item) => item.color)
    : selectedColorBar.value.map((item) => item.color);
  const minVal = Number(threshold_start.value);
  const maxVal = Number(threshold_end.value);

  if (palette?.length) {
    selectedColorBar.value = [...palette];
  }

  localStorage.setItem("threshold_start", JSON.stringify(minVal));
  localStorage.setItem("threshold_end", JSON.stringify(maxVal));
  localStorage.setItem("radio1", JSON.stringify(radio1.value));

  btnloading.value = true;
  try {
    const ok = await recolorLossOverlay(colors, minVal, maxVal);
    if (!ok) {
      ElMessage.warning("请先完成传输损耗预测");
    }
  } catch (error) {
    console.log(error);
    ElMessage.error("损耗图着色失败，请稍后重试");
    btnloading.value = false;
    return;
  }
  btnloading.value = false;
  if (closeDialog) showColorBarConfigurationDialog.value = false;
};

const handleColorBarConfiguration = async (payload?: {
  radio?: number;
  thresholdStart?: number | string;
  thresholdEnd?: number | string;
}) => {
  if (payload && payload.radio != null) {
    radio1.value = Number(payload.radio);
  }
  if (payload && payload.thresholdStart != null) {
    threshold_start.value = Number(payload.thresholdStart);
  }
  if (payload && payload.thresholdEnd != null) {
    threshold_end.value = Number(payload.thresholdEnd);
  }
  await applyColorBarToMap(true);
};



// 获取路由对象
const route = useRoute();

const router = useRouter();
// 销毁
onBeforeUnmount(() => {
  clearProfileWatchdog();
  clearCoverageWatchdog();
  stopClusterResultDrag();
  window.removeEventListener("keydown", onClusterResultEsc);
  graphicLayer.clear();
  $bus.emit('clearAll');
  // 清理事件监听器，防止重复监听
  $bus.off('rectangleAreaClustering', setTableData)
  $bus.off('singlelink', setSingleLinkFormData)
  $bus.off('circleArea', updateCircleAreaImg)
  $bus.off('rectangleArea', updateRectangleAreaImg)
  $bus.off('coverageProgress', updateProgressBar)
  $bus.off('singlelinkProgress', updateProfileProgressBar)
  $bus.off('closeLoading', hideProfileProgress)
  $bus.off('clearRelayArea', clearRelayAreaAndPoint)
  $bus.off('Logout', resetAppToInitial)
  $bus.off('openLaunchSiteConfig', onOpenLaunchSiteConfig)
  $bus.off('openSLPComputedDialog', onOpenSLPComputedDialog)
  $bus.off('openProfileExtract', onOpenProfileExtract)
  $bus.off('openCoverageDialog', onOpenCoverageDialog)
  $bus.off('runTransmissionLossPrediction', onRunTransmissionLossPrediction)
  $bus.off('openClusterDialog', onOpenClusterDialog)
  $bus.off('requestNewProject', onRequestNewProject)
  $bus.off('requestCloseProject', onRequestCloseProject)
  $bus.off('openProjectById', onOpenProjectById)
  $bus.off('resetProjectSession', resetAppToInitial)
  if(showProgressBar.value){
    ElMessage.warning("覆盖计算转入后台");
  }
});
// 计算渐变样式
const gradientStyle = computed(() => {
  if (!selectedColorBar.value || !selectedColorBar.value.length) {
    return {};
  }
  const colors = selectedColorBar.value;
  console.log('colors', colors);

  const colorStops = colors.map((color, index) => {
    // 计算每个颜色的位置百分比
    const position = (index / (colors.length - 1)) * 100;
    return `${color.color} ${position}%`;
  }).join(', ');

  return {
    background: `linear-gradient(to bottom, ${colorStops})`
  };
});

const selectedColorBar = ref([...colorBarList[0].colors])

// 添加 graphicLayer.startDraw 相同的点位
const addBillboard = (position: number[], name: string, label: string) => {
  const billboard = new mars3d.graphic.BillboardEntity({
    name: name,
    position: position,
    style: {
      image: name === 'LaunchSite' ? "/images/start_point.png" : "/images/end_point.png",
      horizontalOrigin: mars3d.Cesium.HorizontalOrigin.CENTER,
      verticalOrigin: mars3d.Cesium.VerticalOrigin.BOTTOM,
      scale: 0.3,
      // 贴地
      clampToGround: true,
      label: {
        // 不需要文字时，去掉label配置即可
        text: label,
        ...MAP_LABEL_FONT,
        color: "#ffffff",
        outline: true,
        outlineColor: "#000000",
        pixelOffsetY: 20,
      },
    },
    attr: { remark: "示例4" }
  })
  graphicLayer.addGraphic(billboard);
}

const addLine = (positionStart: number[], positionEnd: number[], positionCenter: number[]) => {
  console.log(positionStart, positionEnd, positionCenter);

  const graphics = [...graphicLayer.getGraphics()];

  graphics.forEach(graphicItem => {
    if (graphicItem && graphicItem.name === "linkageCalculation") {
      graphicLayer.removeGraphic(graphicItem);
    }
  });
  const graphic = new mars3d.graphic.PolylineEntity({
    name: "linkageCalculation",
    positions: [positionStart, positionEnd],
    style: {
      width: 2,
      materialType: mars3d.MaterialType.PolylineDash,
      materialOptions: {
        color: "#FFA21A", // 中心线颜色
      },
    },
    attr: { remark: "示例18" },
  });

  // 添加空中的矢量点
  const graphicPoint = new mars3d.graphic.PointEntity({
    name: "linkageCalculation",
    position: positionCenter,
    style: {
      pixelSize: 10,
      color: "#FF391A", // 中心线颜色
      label: {
        text: "散射体",
        ...MAP_LABEL_FONT,
        color: "#ffffff",
        outline: true,
        outlineColor: "#000000",
        pixelOffsetY: -10,
      },
    },

    attr: { remark: "散射体" },
  });
  // // 设置PolylineEntity是


  const graphicline1 = new mars3d.graphic.PolylineEntity({
    name: "linkageCalculation",
    positions: [positionStart, positionCenter],
    style: {
      width: 2,
      materialType: mars3d.MaterialType.Polyline,
      materialOptions: {
        color: "#FF391A", // 中心线颜色
      },
    },
    attr: { remark: "示例18" },
  });
  const graphicline2 = new mars3d.graphic.PolylineEntity({
    name: "linkageCalculation",
    positions: [positionEnd, positionCenter],
    style: {
      width: 2,
      materialType: mars3d.MaterialType.Polyline,
      materialOptions: {
        color: "#FF391A", // 中心线颜色
      },
    },
    attr: { remark: "示例18" },
  });
  graphicLayer.addGraphic(graphicline1);
  graphicLayer.addGraphic(graphicline2);
  graphicLayer.addGraphic(graphicPoint);
  graphicLayer.addGraphic(graphic);
}
const SLPCompute_id = ref('')
const initstartEndPoint = (query: any) => {
  // 设置单链路数据id
  SLPCompute_id.value = query.id

  // 发射点配置
  console.log('发射点配置', query);
  drawLaunchSiteForm.name = query.name
  drawLaunchSiteForm.diversity_order = query.diversity_order
  drawLaunchSiteForm.tx_gain = query.tx_gain
  drawLaunchSiteForm.rx_gain = query.rx_gain
  drawLaunchSiteForm.freq = query.freq
  drawLaunchSiteForm.trans_power = query.trans_power
  drawLaunchSiteForm.text = query.text
  drawLaunchSiteForm.lng = query.tx_lon
  drawLaunchSiteForm.lat = query.tx_lat
  drawLaunchSiteForm.height = query.tx_height
  drawLaunchSiteForm.point_name = query.tx_station_name
  drawLaunchSiteForm.comm_rate = query.comm_rate
  // 接收点配置
  SLPComputeForm.lng = formatLongitude(query.rx_lon)
  SLPComputeForm.lat = formatLatitude(query.rx_lat)
  SLPComputeForm.height = query.rx_height
  SLPComputeForm.point_name = query.rx_station_name

  // 
  ProfileForm.image_url = query.image_path + '?t=' + new Date().getTime()
  console.log('ProfileForm.image_url', ProfileForm.image_url);
  linkageCalculationForm.area = query.area
  linkageCalculationForm.diversity_order = query.diversity_order
  linkageCalculationForm.tx_gain = query.tx_gain
  linkageCalculationForm.rx_gain = query.rx_gain
  linkageCalculationForm.freq = query.freq
  linkageCalculationForm.trans_power = query.trans_power
  linkageCalculationForm.lng = query.lng
  linkageCalculationForm.lat = query.lat
  linkageCalculationForm.distance = query.distance
  linkageCalculationForm.median_loss = query.median_loss
  linkageCalculationForm.reliability = query.reliability
  linkageCalculationForm.tx_theta = query.tx_theta
  linkageCalculationForm.rx_theta = query.rx_theta
  linkageCalculationForm.recv_power = query.recv_power
  linkageCalculationForm.tx_azimuth = query.tx_azimuth
  linkageCalculationForm.rx_azimuth = query.rx_azimuth
  linkageCalculationForm.theta_scatter = query.theta_scatter
  linkageCalculationForm.image_url = query.image_path
  linkageCalculationForm.lng = query.tx_lon
  linkageCalculationForm.lat = query.tx_lat
  linkageCalculationForm.distance = query.distance_km
  linkageCalculationForm.residual_value = query.residual_value
  linkageCalculationForm.reliability = query.reliability
  linkageCalculationForm.recv_power = query.recv_power
  linkageCalculationForm.tx_azimuth = query.tx_azimuth
  linkageCalculationForm.rx_azimuth = query.rx_azimuth
  linkageCalculationForm.comm_rate = query.comm_rate
  linkageCalculationForm.rx_barrier_distance = query.rx_barrier_distance
  linkageCalculationForm.tx_barrier_distance = query.tx_barrier_distance
  linkageCalculationForm.tx_barrier_height = query.tx_barrier_height
  linkageCalculationForm.rx_barrier_height = query.rx_barrier_height

  rectangleArea_tif_url.value = query.tif_path;
  rectangleArea_image_url.value = query.image_path;

  circleArea_tif_url.value = query.tif_path;
  circleArea_image_url.value = query.image_path;

  // 散射通信区覆盖区域配置
  CommunicationArea.activeName = query.coverage_type === 'rectangle' ? 'Rectangle' : 'Round';
  CommunicationArea.initialPointLng = query.rectangle_min_longitude != null && query.rectangle_min_longitude !== ''
    ? formatLongitude(query.rectangle_min_longitude) : ''
  CommunicationArea.initialPointLat = query.rectangle_min_latitude != null && query.rectangle_min_latitude !== ''
    ? formatLatitude(query.rectangle_min_latitude) : ''
  CommunicationArea.destinationPointLng = query.rectangle_max_longitude != null && query.rectangle_max_longitude !== ''
    ? formatLongitude(query.rectangle_max_longitude) : ''
  CommunicationArea.destinationPointLat = query.rectangle_max_latitude != null && query.rectangle_max_latitude !== ''
    ? formatLatitude(query.rectangle_max_latitude) : ''
  CommunicationArea.centerPointLng = query.circle_center_longitude != null && query.circle_center_longitude !== ''
    ? formatLongitude(query.circle_center_longitude) : ''
  CommunicationArea.centerPointLat = query.circle_center_latitude != null && query.circle_center_latitude !== ''
    ? formatLatitude(query.circle_center_latitude) : ''
  CommunicationArea.radius = query.circle_radius ? query.circle_radius / 1000 : ''


  // 聚类分析及站点推荐列表查询表单回显

  clusterAnalysisForm.value.loss_threshold = query.loss_threshold ? query.loss_threshold : clusterAnalysisForm.value.loss_threshold
  clusterAnalysisForm.value.limit_road_distance = query.limit_road_distance ? query.limit_road_distance : clusterAnalysisForm.value.limit_road_distance
  clusterAnalysisForm.value.eps_cells = query.eps_cells ? query.eps_cells : clusterAnalysisForm.value.eps_cells
  clusterAnalysisForm.value.min_samples = query.min_samples ? query.min_samples : clusterAnalysisForm.value.min_samples
  clusterAnalysisForm.value.p = query.p ? query.p : clusterAnalysisForm.value.p

  clusterAnalysisForm.value.area_type = query.subrange_type === 'rectangle' ? 'smallRectangle' : 'smallRound'

  if (query.subrange_type === 'rectangle') {
    clusterAnalysisForm.value.initialPointLng = query.subrange_rectangle_min_longitude
    clusterAnalysisForm.value.initialPointLat = query.subrange_rectangle_min_latitude
    clusterAnalysisForm.value.destinationPointLng = query.subrange_rectangle_max_longitude
    clusterAnalysisForm.value.destinationPointLat = query.subrange_rectangle_max_latitude
  } else {
    clusterAnalysisForm.value.centerPointLng = query.subrange_circle_center_longitude
    clusterAnalysisForm.value.centerPointLat = query.subrange_circle_center_latitude
    clusterAnalysisForm.value.radius = query.subrange_circle_radius ? query.subrange_circle_radius / 1000 : ''
  }

  // 禁止区域配置
  console.log('prohibited_area_type', query.prohibited_area_type);
  if (query.prohibited_area_type === 'rectangle') {
    CommunicationAreaProhibited.activeProhibitedName = 'Rectangle';
    CommunicationAreaProhibited.initialPointLng = query.prohibited_max_longitude
    CommunicationAreaProhibited.initialPointLat = query.prohibited_max_latitude
    CommunicationAreaProhibited.destinationPointLng = query.prohibited_min_longitude
    CommunicationAreaProhibited.destinationPointLat = query.prohibited_min_latitude
  } else {
    CommunicationAreaProhibited.activeProhibitedName = 'Round';
    CommunicationAreaProhibited.centerPointLng = query.prohibited_center_longitude
    CommunicationAreaProhibited.centerPointLat = query.prohibited_center_latitude
    CommunicationAreaProhibited.radius = query.prohibited_radius ? query.prohibited_radius / 1000 : ''
  }
  console.log('CommunicationAreaProhibited', CommunicationAreaProhibited);

  $bus.emit(
    "workflowLinkAnalysisReady",
    !!(hasFilled(query.image_path) || hasFilled(query.distance) || hasFilled(query.distance_km) || hasFilled(linkageCalculationForm.distance))
  );
}
let SingleLinkMain = null


const handleApplySite = async (row: any, showMessage: boolean = true) => {
  // const res = await useSite({
  //   id: CommunicationArea.activeName === "Rectangle" ? rectangleArea_tif_id.value : circleArea_tif_id.value,
  //   number: row.num_points,
  //   center_longitude: row.center[0],
  //   center_latitude: row.center[1],
  //   road_name: row.nearest_road.name,
  //   road_slope: row.nearest_road.slope,
  //   distance: row.nearest_road.distance_m,
  // })
  try {
    const res = await saveRecommendSiteList({
      id: row.id,
      name: row.name,
      number: row.number,
    })
    if (showMessage) {
      ElMessage.success('保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败');
  }
}

// 链路计算
const handleLinkageCalculation = async (row: any) => {
  snapshotProfileReturn();
  await handleApplySite(row, false)
  // 如果没有中继站点且中继列表为空，使用发射点

  let startPoint = []
  if (relayPoint.value.length) {
    startPoint = relayPoint.value
  } else if (relayTableData.value.length) {
    startPoint = [relayTableData.value[handleRelayIndex.value].longitude, relayTableData.value[handleRelayIndex.value].latitude]
  } else {
    startPoint = [parseLongitude(drawLaunchSiteForm.lng), parseLatitude(drawLaunchSiteForm.lat)]
  }
  $bus.emit("sendMessage", {
    ...projectFields(),
    name: drawLaunchSiteForm.name,
    link_name: row.name || "推荐站点",
    tx_lon: startPoint[0],
    tx_lat: startPoint[1],
    tx_height: drawLaunchSiteForm.height ? drawLaunchSiteForm.height : 0,
    rx_lon: row.longitude,
    rx_lat: row.latitude,
    rx_height: 0,
    tx_gain: drawLaunchSiteForm.tx_gain,
    rx_gain: drawLaunchSiteForm.rx_gain,
    freq: drawLaunchSiteForm.freq,
    trans_power: drawLaunchSiteForm.trans_power,
    climate_num: drawLaunchSiteForm.climate_num,
    diversity_order: drawLaunchSiteForm.diversity_order,
    rx_station_name: row.name,
    tx_station_name: drawLaunchSiteForm.point_name,
    comm_rate: drawLaunchSiteForm.comm_rate,
  });
}

// 清理中继区域和点数据
const clearRelayAreaAndPoint = () => {
  relayPoint.value = []
  relayTableData.value = []
  handleRelayIndex.value = 0
}
$bus.on('clearRelayArea', clearRelayAreaAndPoint);


const handleRelayIndex = ref(0)
// 站点计算
const handleRelaySiteCalculation = async (row: any, index: number) => {
  handleRelayIndex.value = index
  let data = {
    type: clusterAnalysisForm.value.area_type === 'smallRectangle' ? 'rectangle area clustering' : 'circle area clustering',
    id: CommunicationArea.activeName === 'Rectangle' ? rectangleArea_tif_id.value : circleArea_tif_id.value,
    tif_path: CommunicationArea.activeName === 'Rectangle' ? rectangleArea_tif_url.value : circleArea_tif_url.value,
    loss_threshold: clusterAnalysisForm.value.loss_threshold,
    limit_road_distance: clusterAnalysisForm.value.limit_road_distance,
    eps_cells: clusterAnalysisForm.value.eps_cells,
    min_samples: clusterAnalysisForm.value.min_samples,
    p: clusterAnalysisForm.value.p,

    relay_lon: row.longitude,
    relay_lat: row.latitude,

  }
  if (clusterAnalysisForm.value.area_type === 'smallRectangle') {
    data = {
      ...data,
      min_lon: clusterAnalysisForm.value.initialPointLng,
      min_lat: clusterAnalysisForm.value.initialPointLat,
      max_lon: clusterAnalysisForm.value.destinationPointLng,
      max_lat: clusterAnalysisForm.value.destinationPointLat,
    }

  } else if (clusterAnalysisForm.value.area_type === 'smallRound') {
    data = {
      ...data,
      center_lon: clusterAnalysisForm.value.centerPointLng,
      center_lat: clusterAnalysisForm.value.centerPointLat,
      radius_m: clusterAnalysisForm.value.radius,
    }
  }
  console.log('data', data);

  $bus.emit("sendMessage", data);

}



// 区域覆盖回显
const addPrimitive = (query: any) => {
  // 区域覆盖
  if (query.type === 'rectangle') {
    // addPrimitive(query)
    addBillboard(query.position, 'LaunchSite', '站点1');
    rectangleArea_tif_url.value = query.rectangle.tif_image_url;
    rectangleArea_image_url.value = query.rectangle.png_image_url;
    // rectangleArea_tif_id.value = query.id;
    graphicLayer.eachGraphic((graphicItem) => {
      if (graphicItem && graphicItem.name === "Rectangle") {
        graphicLayer.removeGraphic(graphicItem);
      }
      if (graphicItem && graphicItem.name === "rectangle") {
        graphicLayer.removeGraphic(graphicItem);
      }
    });
    console.log('query.rectangle', query.rectangle);

    const graphic = new mars3d.graphic.RectanglePrimitive({
      name: "Rectangle",
      positions: [
        [
          query.rectangle.minLongitude,
          query.rectangle.minLatitude,
          33.69,
        ],
        [
          query.rectangle.maxLongitude,
          query.rectangle.maxLatitude,
          26.44,
        ],
      ],
      style: {
        height: 100,
        opacity: 0.6,
        image: query.rectangle.png_image_url,
        clampToGround: true,
      },
      attr: { remark: "示例3" },
    });
    // 回显路网数据
    const geoJsonLayer1 = new mars3d.layer.GeoJsonLayer({
      // url: "https://data.mars3d.cn/file/geojson/wuhan-line1.json",
      data: query.rectangle.geojson,//路网geojson数据
      symbol: {
        type: "polylineC",
        styleOptions: {
          width: 50, // 线宽
          materialType: "PolylineGlow",
          materialOptions: {
            color: "#FF4500",
            opacity: 0.9,
            glowPower: 0.06 // 发光强度
          }
        }
      },
      // popup: "all",
      show: true
    })
    graphicLayer.addGraphic(graphic);
  }
}
const pickPrimaryLink = (links = []) => {
  if (!links.length) return null;
  return links.find((item) => item.name === "主链路") || links[0];
};

const fixedNum = (value, digits = 2) => {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(digits) : value;
};

const mapLinkToQuery = (project, link) => ({
  id: link.id,
  name: project.name,
  tx_lon: link.tx_lon,
  tx_lat: link.tx_lat,
  tx_height: link.tx_terrain_height,
  rx_height: link.rx_terrain_height,
  rx_lon: link.rx_lon,
  rx_lat: link.rx_lat,
  tx_gain: link.tx_gain,
  rx_gain: link.rx_gain,
  freq: link.freq,
  trans_power: link.trans_power,
  diversity_order: link.diversity_order,
  median_loss: fixedNum(link.median_loss),
  tx_theta: fixedNum(link.tx_theta),
  rx_theta: fixedNum(link.rx_theta),
  theta_scatter: fixedNum(link.theta_scatter),
  area: link.area,
  max_height: link.max_height,
  scatterer_lon: link.scatterer_lon,
  scatterer_lat: link.scatterer_lat,
  scatterer_height: link.scatterer_height,
  image_path: link.image_path,
  distance_km: link.distance_km,
  residual_value: fixedNum(link.residual_value),
  reliability: link.reliability,
  recv_power: fixedNum(link.recv_power),
  tx_azimuth: fixedNum(link.tx_azimuth),
  rx_azimuth: fixedNum(link.rx_azimuth),
  comm_rate: link.comm_rate,
  tx_barrier_distance: fixedNum(link.tx_barrier_distance),
  rx_barrier_distance: fixedNum(link.rx_barrier_distance),
  tx_barrier_height: link.tx_barrier_height,
  rx_barrier_height: link.rx_barrier_height,
  tx_station_name: link.tx_station_name,
  rx_station_name: link.rx_station_name,
});

const mapCoverageToQuery = (coverage) => ({
  id: coverage.id,
  name: coverage.name,
  tx_gain: coverage.tx_gain,
  rx_gain: coverage.rx_gain,
  trans_power: coverage.trans_power,
  diversity_order: coverage.diversity_order,
  tx_lon: coverage.tx_longitude,
  tx_lat: coverage.tx_latitude,
  tx_height: 10,
  freq: coverage.frequency,
  coverage_type: coverage.coverage_type,
  rectangle_min_longitude: coverage.rectangle_min_longitude,
  rectangle_max_longitude: coverage.rectangle_max_longitude,
  rectangle_min_latitude: coverage.rectangle_min_latitude,
  rectangle_max_latitude: coverage.rectangle_max_latitude,
  circle_center_longitude: coverage.circle_center_longitude,
  circle_center_latitude: coverage.circle_center_latitude,
  circle_radius: coverage.circle_radius,
  tif_path: coverage.tif_path,
  image_path: coverage.image_path,
  loss_threshold: coverage.loss_threshold,
  eps_cells: coverage.eps_cells,
  min_samples: coverage.min_samples,
  p: coverage.p,
  created_at: coverage.created_at,
  image_colors: coverage.image_colors,
  image_max: coverage.image_max,
  image_min: coverage.image_min,
  comm_rate: coverage.comm_rate,
  tx_station_name: coverage.tx_station_name,
  subrange_circle_center_latitude: coverage.subrange_circle_center_latitude,
  subrange_circle_center_longitude: coverage.subrange_circle_center_longitude,
  subrange_circle_radius: coverage.subrange_circle_radius,
  subrange_rectangle_max_latitude: coverage.subrange_rectangle_max_latitude,
  subrange_rectangle_max_longitude: coverage.subrange_rectangle_max_longitude,
  subrange_rectangle_min_latitude: coverage.subrange_rectangle_min_latitude,
  subrange_rectangle_min_longitude: coverage.subrange_rectangle_min_longitude,
  subrange_type: coverage.subrange_type,
  prohibited_area_type: coverage.prohibited_area_type,
  prohibited_min_longitude: coverage.prohibited_min_longitude,
  prohibited_min_latitude: coverage.prohibited_min_latitude,
  prohibited_max_longitude: coverage.prohibited_max_longitude,
  prohibited_max_latitude: coverage.prohibited_max_latitude,
  prohibited_center_longitude: coverage.prohibited_center_longitude,
  prohibited_center_latitude: coverage.prohibited_center_latitude,
  prohibited_radius: coverage.prohibited_radius,
  relay_longitude: coverage.relay_longitude,
  relay_latitude: coverage.relay_latitude,
  limit_road_distance: coverage.limit_road_distance,
});

const restoreCoverageOnMap = (query, stations = []) => {
  rectangleArea_tif_id.value = query.id;
  circleArea_tif_id.value = query.id;
  activeBtnIndex.value = 1;

  if (query.image_colors) {
    const image_colors = String(query.image_colors).split(" ");
    colorBarList[radio1.value].colors.forEach((item, index) => {
      if (image_colors[index]) item.color = image_colors[index];
    });
  }
  if (query.image_max) {
    threshold_end.value = Number(query.image_max);
  }
  if (query.image_min) {
    threshold_start.value = Number(query.image_min);
  }
  if (query.coverage_type === "rectangle") {
    $bus.emit("addRectangleAreaImg", {
      initialPoint: [query.rectangle_min_longitude, query.rectangle_min_latitude],
      destinationPoint: [query.rectangle_max_longitude, query.rectangle_max_latitude],
      png_image_url: query.image_path + "?time=" + new Date().getTime(),
    });
  } else if (query.coverage_type === "circle") {
    $bus.emit("addCircleAreaImg", {
      center: [Number(query.circle_center_longitude), Number(query.circle_center_latitude)],
      radius: Number(query.circle_radius),
      png_image_url: query.image_path + "?time=" + new Date().getTime(),
    });
  }

  if (query.subrange_type === "rectangle") {
    $bus.emit("addSmallRectangleAreaImg", {
      initialPoint: [query.subrange_rectangle_min_longitude, query.subrange_rectangle_min_latitude],
      destinationPoint: [query.subrange_rectangle_max_longitude, query.subrange_rectangle_max_latitude],
    });
  } else if (query.subrange_type === "circle") {
    $bus.emit("addSmallCircleAreaImg", {
      center: [query.subrange_circle_center_longitude, query.subrange_circle_center_latitude],
      radius: query.subrange_circle_radius,
    });
  }

  if (query.prohibited_area_type === "rectangle") {
    $bus.emit("addProhibitedCommunicationAreaImg", {
      type: "Rectangle",
      initialPoint: [query.prohibited_min_longitude, query.prohibited_min_latitude],
      destinationPoint: [query.prohibited_max_longitude, query.prohibited_max_latitude],
    });
  } else if (query.prohibited_area_type === "circle") {
    $bus.emit("addProhibitedCommunicationAreaImg", {
      type: "Round",
      center: [query.prohibited_center_longitude, query.prohibited_center_latitude],
      radius: query.prohibited_radius,
    });
  }

  if (query.relay_longitude && query.relay_latitude) {
    relayPoint.value = [query.relay_longitude, query.relay_latitude];
    $bus.emit("addRelayStationImg", {
      center: [query.relay_longitude, query.relay_latitude],
    });
  }

  const rows = (stations || []).map((item, index) => ({
    ...item,
    name: item.name || "推荐站点" + (index + 1),
    number: item.number,
    latitude: item.latitude || item.center_latitude,
    longitude: item.longitude || item.center_longitude,
    slope: item.slope || item.to_road_slope,
  }));
  tableData.value = rows;
  if (rows.length) {
    $bus.emit("addClusterPoint", rows);
  }
};

const restoreProjectFromId = async (projectId) => {
  try {
    const project: any = await getProject(projectId);
    currentProjectId.value = project.id;
    railFullUnlock.value = true;
    $bus.emit("workflowRailFull", true);
    projectOpen.value = true;
    isSelectStartPointOver.value = true;

    const link = pickPrimaryLink(project.single_links || []);
    const coverage = project.coverage;
    const stations = project.stations || [];
    const query: any = { name: project.name };

    if (link) {
      Object.assign(query, mapLinkToQuery(project, link));
    }
    if (coverage) {
      const coverageQuery = mapCoverageToQuery(coverage);
      Object.assign(query, coverageQuery, {
        name: project.name,
        image_path: link?.image_path || coverage.image_path,
        tif_path: coverage.tif_path,
      });
      if (link) {
        query.tx_lon = link.tx_lon;
        query.tx_lat = link.tx_lat;
        query.tx_height = link.tx_terrain_height;
        query.tx_gain = link.tx_gain;
        query.rx_gain = link.rx_gain;
        query.freq = link.freq;
        query.trans_power = link.trans_power;
        query.diversity_order = link.diversity_order;
        query.comm_rate = link.comm_rate;
        query.tx_station_name = link.tx_station_name;
      }
    }

    initstartEndPoint(query);
    if (link?.image_path) {
      ProfileForm.image_url = link.image_path + "?t=" + new Date().getTime();
    }
    if (coverage) {
      rectangleArea_tif_url.value = coverage.tif_path;
      rectangleArea_image_url.value = coverage.image_path;
      circleArea_tif_url.value = coverage.tif_path;
      circleArea_image_url.value = coverage.image_path;
    }

    if (query.tx_lon && query.tx_lat) {
      $bus.emit("setLaunchSite", {
        type: "LaunchSite",
        lng: query.tx_lon,
        lat: query.tx_lat,
        height: query.tx_height,
      });
    }
    if (link) {
      $bus.emit("setSLPCompute", {
        type: "SLPCompute",
        lng: link.rx_lon,
        lat: link.rx_lat,
        height: link.rx_terrain_height,
      });
      $bus.emit("setSingleLink", {
        startPoint: [link.tx_lon, link.tx_lat, link.tx_terrain_height],
        endPoint: [link.rx_lon, link.rx_lat, link.rx_terrain_height],
        scatterer_lon: link.scatterer_lon,
        scatterer_lat: link.scatterer_lat,
        scatterer_height: link.scatterer_height,
      });
    }
    if (coverage) {
      restoreCoverageOnMap(mapCoverageToQuery(coverage), stations);
      getTableDataTime.value = coverage.cluster_duration;
    }

    const firstStation = stations[0];
    const flyLon = Number(
      firstStation?.center_longitude ?? firstStation?.longitude ?? (link ? link.rx_lon : query.tx_lon)
    );
    const flyLat = Number(
      firstStation?.center_latitude ?? firstStation?.latitude ?? (link ? link.rx_lat : query.tx_lat)
    );
    if (MapContainer && Number.isFinite(flyLon) && Number.isFinite(flyLat)) {
      MapContainer.camera.flyTo({
        destination: mars3d.Cesium.Cartesian3.fromDegrees(flyLon, flyLat, 80000),
        duration: 1.2,
      });
    }
    emitWorkflowPointState();
    $bus.emit(
      "workflowLinkAnalysisReady",
      !!(hasFilled(linkageCalculationForm.distance) || hasFilled(ProfileForm.image_url) || hasFilled(linkageCalculationForm.image_url))
    );
  } catch (error) {
    railFullUnlock.value = false;
    $bus.emit("workflowRailFull", false);
    ElMessage.error("打开工程失败");
  }
};

const onOpenProjectById = async (projectId) => {
  if (!projectId) return;
  if (String(currentProjectId.value) === String(projectId) && projectOpen.value) {
    return;
  }
  if (projectOpen.value) {
    resetAppToInitial();
  }
  await restoreProjectFromId(projectId);
  if (route.path === "/" || route.name === "home") {
    router.replace({ path: "/", query: { project: String(projectId) } });
  }
};

$bus.all?.delete?.("openProjectById");
$bus.all?.delete?.("resetProjectSession");
$bus.on("openProjectById", onOpenProjectById);
$bus.on("resetProjectSession", resetAppToInitial);

const relayPoint = ref([])
onMounted(async () => {
  window.addEventListener("keydown", onClusterResultEsc);
  await nextTick(async () => {
    MapContainer = getMapInstance();
    const main = new Main(MapContainer);
    MapContainer && MapContainer.addLayer(graphicLayer);

    // 初始化选中的颜色条为第一个颜色条
    // 获取 locastorage 中的颜色配置数据，如果有则对数据进行回显
    const local_threshold_start = localStorage.getItem("threshold_start");
    const local_threshold_end = localStorage.getItem("threshold_end");

    if (JSON.parse(local_threshold_start)) {
      threshold_start.value = JSON.parse(local_threshold_start);
    }
    if (JSON.parse(local_threshold_end)) {
      threshold_end.value = JSON.parse(local_threshold_end);
    }

    radio1.value = 0;
    selectedColorBar.value = [...colorBarList[0].colors];
    localStorage.setItem("radio1", JSON.stringify(0));

    // 接收页面的 query 值，如果有值，则对当前页面数据进行回显
    const query = route.query;

    if (query.project) {
      await restoreProjectFromId(query.project);
    } else if (query.type) {
      // 如果 type === 'singleLink' 则进行单链规划回显
      railFullUnlock.value = true;
      $bus.emit("workflowRailFull", true);
      projectOpen.value = true
      isSelectStartPointOver.value = true
      if (query.type === 'singleLink') {
        // 单链规划回显
        $bus.emit('setLaunchSite', {
          type: 'LaunchSite',
          lng: query.tx_lon,
          lat: query.tx_lat,
          height: query.tx_height,
        })
        $bus.emit('setSLPCompute', {
          type: 'SLPCompute',
          lng: query.rx_lon,
          lat: query.rx_lat,
          height: query.rx_height,
        })

        $bus.emit('setSingleLink', {
          startPoint: [query.tx_lon, query.tx_lat, query.tx_height],
          endPoint: [query.rx_lon, query.rx_lat, query.rx_height],
          scatterer_lon: query.scatterer_lon,
          scatterer_lat: query.scatterer_lat,
          scatterer_height: query.scatterer_height,
        })

        // 对发射点和接受点数据进行回显
        initstartEndPoint(query)
      }
      // 如果 type === 'areaCoverage' 则进行区域覆盖回显
      if (query.type === 'areaCoverage') {
        $bus.emit('setLaunchSite', {
          type: 'LaunchSite',
          lng: query.tx_lon,
          lat: query.tx_lat,
          height: query.tx_height,
        })
        initstartEndPoint(query)
        rectangleArea_tif_id.value = query.id;
        circleArea_tif_id.value = query.id;
        activeBtnIndex.value = 1


        const image_colors = query.image_colors.split(' ');

        // 对色条和阈值进行回显
        if (query.image_colors) {
          colorBarList[radio1.value].colors.forEach((item, index) => {
            item.color = image_colors[index];
          })
        }
        if (query.image_max) {
          threshold_end.value = JSON.parse(query.image_max);
        }
        if (query.image_min) {
          threshold_start.value = JSON.parse(query.image_min);
        }
        if (query.coverage_type === 'rectangle') {
          // 区域覆盖
          $bus.emit('addRectangleAreaImg', {
            initialPoint: [query.rectangle_min_longitude, query.rectangle_min_latitude],
            destinationPoint: [query.rectangle_max_longitude, query.rectangle_max_latitude],
            png_image_url: query.image_path + '?time=' + new Date().getTime(),
          })

        } else if (query.coverage_type === 'circle') {
          // 区域覆盖
          $bus.emit('addCircleAreaImg', {
            center: [Number(query.circle_center_longitude), Number(query.circle_center_latitude)],
            radius: Number(query.circle_radius),
            png_image_url: query.image_path + '?time=' + new Date().getTime(),
          })

        }

        if (query.subrange_type === 'rectangle') {
          // 二次区域绘制数据
          $bus.emit('addSmallRectangleAreaImg', {
            initialPoint: [query.subrange_rectangle_min_longitude, query.subrange_rectangle_min_latitude],
            destinationPoint: [query.subrange_rectangle_max_longitude, query.subrange_rectangle_max_latitude],
          })
        } else if (query.subrange_type === 'circle') {
          // 二次区域绘制数据
          $bus.emit('addSmallCircleAreaImg', {
            center: [query.subrange_circle_center_longitude, query.subrange_circle_center_latitude],
            radius: query.subrange_circle_radius,
          })
        }

        // 禁止区域绘制数据
        if (query.prohibited_area_type === 'rectangle') {
          // 禁止区域绘制数据
          $bus.emit('addProhibitedCommunicationAreaImg', {
            type: 'Rectangle',
            initialPoint: [query.prohibited_min_longitude, query.prohibited_min_latitude],
            destinationPoint: [query.prohibited_max_longitude, query.prohibited_max_latitude],
          })
        } else if (query.prohibited_area_type === 'circle') {
          // 禁止区域绘制数据
          $bus.emit('addProhibitedCommunicationAreaImg', {
            type: 'Round',
            center: [query.prohibited_center_longitude, query.prohibited_center_latitude],
            radius: query.prohibited_radius,
          })
        }
        // 中继站点添加
        if (query.relay_longitude && query.relay_latitude) {
          relayPoint.value = [query.relay_longitude, query.relay_latitude]
          $bus.emit('addRelayStationImg', {
            center: [query.relay_longitude, query.relay_latitude],
          })
        }

        // 获取站点推荐数据并回显
        getRecommendSiteList({
          area_coverage_id: query.id,
        }).then(res => {
          res.stations.forEach((item, index) => {
            item.name = item.name || '推荐站点' + (index + 1)
            item.number = item.number
            item.latitude = item.latitude || item.center_latitude
            item.longitude = item.longitude || item.center_longitude
            item.slope = item.slope || item.to_road_slope
          })
          tableData.value = res.stations
          getTableDataTime.value = res.calculation_duration
          showClusterAnalysisDialog.value = true
          $bus.emit('addClusterPoint', tableData.value)
        })

        // 对区域覆盖数据进行回显
      }
      // 站点规划结果-查看详情点击跳转到首页之后定位到rx_lon经纬度点
      MapContainer.camera.flyTo({
        destination: mars3d.Cesium.Cartesian3.fromDegrees(query.type === 'singleLink' ? query.rx_lon : query.tx_lon, query.type === 'singleLink' ? query.rx_lat : query.tx_lat, 1500000),
        duration: 0
      })
    }

  });
});
</script>

<style lang="scss" scoped>
@use './index.scss';
@use "@/styles/gotham-panel.scss" as *;

.results-panel :deep(.el-dropdown-menu) {
  background: rgba(12, 21, 16, 0.96);
  border: 1px solid rgba(64, 73, 69, 0.4);
}

.results-panel :deep(.el-dropdown-menu__item) {
  color: #dae5dc;
  font-family: Inter, "Noto Sans SC", sans-serif;
}

.results-panel :deep(.el-dropdown-menu__item:hover) {
  background: rgba(157, 223, 46, 0.12);
  color: #9ddf2e;
}
</style>
