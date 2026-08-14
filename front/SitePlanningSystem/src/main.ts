import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import mitt from "./assets/util/mitt";

import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import CommonDialog from "@/components/commonDialog/index.vue";
import vue3TreeOrg from 'vue3-tree-org';
import "vue3-tree-org/lib/vue3-tree-org.css";
// main.ts


//引入cesium基础库
import "mars3d-cesium/Build/Cesium/Widgets/widgets.css";

//导入mars3d主库
import "mars3d/mars3d.css";

//导入mars3d插件（按需使用，需要先npm install）
// import "mars3d-space";

// 全局样式必须在 Element Plus / Cesium 之后，才能覆盖下拉等挂到 body 的浮层
import "./index.scss";

const app = createApp(App);
app.use(ElementPlus, {
  locale: zhCn,
});
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}



// 给 html 标签添加 dark 类
app.use(router);
app.use(store);
app.use(vue3TreeOrg)
app.component("CommonDialog", CommonDialog);

// 将事件总线绑定到全局
app.config.globalProperties.$bus = mitt();

app.mount("#app");