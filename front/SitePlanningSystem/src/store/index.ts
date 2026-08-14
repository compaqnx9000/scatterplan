//@ts-nocheck
import { createStore } from 'vuex';
import { logout, getInfo } from "@/request/user";
import logo from "@/assets/logo.png";
// import { getRouters } from "@/request/system";
// import Layout from "@/layout/index.vue";
import router from "@/router/index";
import { ElLoading } from 'element-plus';
// import { Toast } from "@/assets/util/index"
// 引入所有views下.vue文件
const modules = import.meta.glob("../views/**/**.vue");
const store = createStore({
  state: {
    userInfo: {
      // avatar: "用户头像"
      // nickName: "用户名称"
      // phonenumber: "手机号码"
      // createTime: "创建时间"
      // sex: "0男1女"
    },
    token: "",
    roles: [], // 用户角色
    permissions: [], // 用户权限
    routes: [], // 用户路由信息
    allDict: {}, // 存储所有字典
    mapAddStatus:false,
    // 控制面板是否展示
    isPanelShow:true,
    // 控制3d模型
    isShowMoudle:false,
    refreshToken:'',
    is_staff:false,
    taskId:'', // 任务id
  },
  mutations: {
    setTaskId(state,taskId){
      state.taskId = taskId;
    },
    setMapAddStatus(state,mapStatus){
      state.mapAddStatus = mapStatus
    },
    setPermissions(state,permissions){
      state.permissions = permissions;
    },
    setRoles(state,roles){
      state.roles = roles;
    },
    setUserInfo(state,userInfo){
      state.userInfo = userInfo;
    },
    setToken(state,token){
      localStorage.setItem('userToken',token)
      state.token = token;
    },
    setIs_staff(state,is_staff){
      localStorage.setItem('is_staff',is_staff)
      state.is_staff = is_staff;
    },
    setRefreshToken(state,token){
      localStorage.setItem('refreshToken',token)
      state.refreshToken = token;
    },
    SET_ROUTES(state,routes){
      state.routes = routes;
    },
    SET_ALLDICT(state,allDict){
      state.allDict = allDict;
    },
    SET_PANELSHOW(state,flag){
      state.isPanelShow = flag;
    },
    SET_MOUDEL(state,flag){
      state.isShowMoudle = flag;
    },

  },
  actions: {
    GetUserInfo({ commit }){
      return new Promise((resolve, reject) => {
        getInfo().then((res: any) => {
          if(!res) return;
          const user:any = res.user;
          user.avatar = logo;
          if(res.roles && res.roles.length > 0){ // 验证返回的roles是否是一个非空数组
            commit('setRoles', res.roles); // 存储用户角色
            commit('setPermissions', res.permissions); // 存储用户权限
          } else {
            commit('setRoles', ['ROLE_DEFAULT']); // 存储用户角色
          }
          commit("setUserInfo", user);
          // commit('SET_AVATAR', avatar);
          resolve(res);
        }).catch(error => {
          reject(error);
        });
      });
    },
    // 退出系统
    async LogOut({ commit }){
      const loading = ElLoading.service({
        lock: true,
        text: 'Loading',
        customClass:"elLogadingStyle",
        background: 'rgba(0, 0, 0, 0.9)',
      });
      await logout();
      // 清除本地token
      localStorage.removeItem("userToken");
      // 清除token
      commit('setToken', '');
      // 清除角色
      commit('setRoles', []);
      // 清除权限
      commit('setPermissions', []);
      // 清除部门
      commit("SET_ROUTES", []);
      router.replace({path:"/"});
      loading.close();
    },
    // 生成路由
    // GenerateRoutes({ commit }){
    //   return new Promise(resolve => {
    //     // 向后端请求路由数据
    //     getRouters().then(res => {
    //       const rdata = JSON.parse(JSON.stringify(res.data));
    //       if(rdata.length){
    //         // const sidebarRoutes = filterAsyncRouter(sdata);
    //         const rewriteRoutes = filterAsyncRouter(JSON.parse(JSON.stringify(rdata)), false, true);
    //         // rewriteRoutes.push({ path: "/:catchAll(.*)", redirect: "/404", hidden: true });
    //         commit("SET_ROUTES", rewriteRoutes);
    //         resolve(rewriteRoutes);
    //       }else{
    //         Toast("该用户暂无系统使用权限",3000);
    //         store.dispatch("LogOut");
    //       }
    //     });
    //   });
    // },
  },
  getters: {
    getMapAddStatus(state){
      return state.mapAddStatus
    },
    getUserInfo(state){
      return state.userInfo;
    },
    getToken(state){
      let userToken = localStorage.getItem('userToken')
      return state.token?state.token:userToken;
    },
    getRoles(state){
      return state.roles;
    },
    getRoutes(state){
      return state.routes;
    },
    getBtnPermissions(state){
      return state.permissions;
    },
    getAllDict(state){
      return state.allDict;
    },
    getPermissions(state){
      return state.permissions;
    },
    getIsPanelShow(state){
      return state.isPanelShow;
    },
    getIsShowMoudle(state){
      return state.isShowMoudle;
    }
  }
});
export default store;
// 遍历后台传来的路由字符串，转换为组件对象
// function filterAsyncRouter(asyncRouterMap: Array<any>,lastRouter = false,type = false){
//   return asyncRouterMap.filter(route => {
//     if(type && route.children){
//       route.children = filterChildren(route.children);
//       // filterChildren(route.children);
//     }
//     if(route.component){
//       // Layout ParentView 组件特殊处理
//       if(route.component === "Layout"){
//         route.component = Layout;
//       }else if(route.component === "ParentView"){
//         route.component = Layout;
//       }else{
//         route.component = loadView(route.component);
//       }
//     }
//     if(route.children != null && route.children && route.children.length){
//       route.children = filterAsyncRouter(route.children, route, type);
//     }else{
//       delete route["children"];
//       delete route["redirect"];
//     }
//     return true;
//   });
// }
// function filterChildren(childrenMap:Array<any>,lastRouter:any = false){
//   let children:Array<any> = [];
//   childrenMap.forEach((el, index) => {
//     if(el.children && el.children.length){
//       if(el.component === "ParentView" && !lastRouter){
//         el.children.forEach((c: any) => {
//           c.path = el.path + "/" + c.path;
//           if(c.children && c.children.length){
//             children = children.concat(filterChildren(c.children, c))
//             return;
//           }
//           children.push(c);
//         });
//         return;
//       }
//     }
//     if(lastRouter){
//       el.path = lastRouter.path + "/" + el.path;
//     }
//     children = children.concat(el);
//   });
//   return children;
// }
// 动态加载页面组件 vite 独有
export let loadView = (view: string) => {
  let src = `../views/${view}.vue`;
  // console.log(modules[/* @vite-ignore */ src],src);
  // 路由懒加载
  return modules[/* @vite-ignore */ src];
};
