import { createRouter, createWebHistory } from "vue-router";

const routerHistory = createWebHistory();
import Layout from "@/view/layout/index.vue";
// createWebHistory history 路由
// createMemoryHistory 带缓存 history 路由
const router = createRouter({
  history: routerHistory,
  routes: [
    {
      path: "/",
      component: Layout,
      meta: {
        title: "首页",
      },
      children: [
        {
          path: "",
          name: "home",
          component: () => import("@/view/home/index.vue"),
          meta: { title: "首页" },
        },
      ],
    },
    {
      path: "/login",
      redirect: "/",
    },
    {
      path: "/home",
      redirect: "/",
    },
    {
      path: "/home/home",
      redirect: (to) => ({ path: "/", query: to.query, hash: to.hash }),
    },
    {
      path: "/sitePlanning",
      component: Layout,
      redirect: "/sitePlanning/sitePlanning",
      meta: {
        title: "站点规划结果",
      },
      children: [
        {
          path: "sitePlanning",
          name: "sitePlanning",
          component: () => import("@/view/sitePlanning/index.vue"),
          meta: { title: "站点规划结果" },
        },
        
      ],
    },
    {
      path: "/systemData",
      component: Layout,
      redirect: "/systemData/systemuser",
      meta: {
        title: "系统数据",
      },
      children: [
        {
          path: "systemmap",
          name: "systemmap",
          component: () => import("@/view/systemData/system_map.vue"),
          meta: { title: "地图接口服务" },
        },
        {
          path: "systemuser",
          name: "systemuser",
          component: () => import("@/view/systemData/system_user.vue"),
          meta: { title: "用户管理" },
        },
        
        {
          path: "systemdict",
          name: "systemdict",
          component: () => import("@/view/systemData/system_dict.vue"),
          meta: { title: "数据字典配置" },
        },
      ],
    },
    {
      path: "/tiffloader",
      component: Layout,
      redirect: "/tiffloader/TiffLoader",
      meta: {
        title: "加载tiff",
      },
      children: [
        {
          path: "TiffLoader",
          name: "TiffLoader",
          component: () => import("@/view/tiffloader/TiffLoader.vue"),
          meta: { title: "加载tiff" },
        },
        
      ],
    },

  ],
});

export default router;
