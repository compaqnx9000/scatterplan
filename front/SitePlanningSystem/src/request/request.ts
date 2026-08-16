import axios from "axios";
import refreshToken from "@/request/refreshToken";

// @ts-ignore
import { saveAs } from "file-saver";

import $store from "@/store/index";
import router from "@/router";
import { ElLoading, ElMessage } from "element-plus";
import { blobValidate, tansParams } from "@/util";

// 创建 axios 实例
const service = axios.create({
  withCredentials: true,
  baseURL: import.meta.env.VITE_APP_BASE_prefix,
  headers: {
    "Content-Type": "application/json;charset=utf-8",
  },
  timeout: 300000,
});

let isRefreshing = false;
let requestsQueue: Array<{ resolve: Function; reject: Function }> = [];

// request 拦截器
service.interceptors.request.use(
  async (config: any) => {
    const isToken = (config.headers || {}).isToken === false;
    if ($store.getters.getToken && !isToken) {
      config.headers["Authorization"] = "Bearer " + $store.getters.getToken;
    }
    if (config.method === "get" && config.params) {
      let url = config.url + "?";
      for (const propName of Object.keys(config.params)) {
        const value = config.params[propName];
        var part = encodeURIComponent(propName) + "=";
        if (value !== null && typeof value !== "undefined") {
          if (typeof value === "object") {
            for (const key of Object.keys(value)) {
              let params = propName + "[" + key + "]";
              var subPart = encodeURIComponent(params) + "=";
              url += subPart + encodeURIComponent(value[key]) + "&";
            }
          } else {
            url += part + encodeURIComponent(value) + "&";
          }
        }
      }
      url = url.slice(0, -1);
      config.params = {};
      config.url = url;
    }
    return config;
  },
  (error) => {
    Promise.reject(error);
  }
);

let errorCode: any = {
  "401": "认证失败，无法访问系统资源",
  "403": "当前操作没有权限",
  "404": "访问资源不存在",
  default: "系统未知错误，请反馈给管理员",
};

function pickFirstText(value: any): string {
  if (typeof value === "string" && value.trim()) return value;
  if (Array.isArray(value) && value.length) return pickFirstText(value[0]);
  if (value && typeof value === "object") {
    return pickFirstText(value.string || value.msg || value.message || value.detail);
  }
  return "";
}

function pickServerMessage(data: any): string {
  if (!data) return "";
  if (typeof data === "string") return data.trim();
  const direct = pickFirstText(data.message || data.detail || data.msg || data.username);
  if (direct) return direct;
  if (typeof data === "object") {
    for (const value of Object.values(data)) {
      const text = pickFirstText(value);
      if (text) return text;
    }
  }
  return "";
}

// 响应拦截器
service.interceptors.response.use(
  (res) => {
    const code = res.status || 200;
    const msg = errorCode[code] || res.data.msg || errorCode.default;
    if (code === 401) {
      ElMessage.error("登录状态已过期，请重新登录");
      localStorage.removeItem("userToken");
      localStorage.removeItem("refreshToken");
      $store.commit("setToken", "");
      $store.commit("setRefreshToken", "");
      router.replace({ path: "/" });
    } else if (code === 500) {
      ElMessage.error(msg);
      return Promise.reject("error");
    } else if (code !== 200 && code !== 204 && code !== 201) {
      ElMessage.error(msg);
      return Promise.reject("error");
    } else {
      return res.data;
    }
  },

  async (error) => {
    console.log("请求失败:", error.response?.data);
    if (
      error.response?.status === 401 &&
      !error.config.url.includes("/login/") &&
      !error.config.url.includes("/jwt/refresh/")
    ) {
      const refreshTokenValue =
        localStorage.getItem("refreshToken") || $store.state.refreshToken;
      console.log("refreshTokenValue", refreshTokenValue);

      if (!refreshTokenValue) {
        ElMessage.error("登录状态已过期，请重新登录");
        localStorage.removeItem("userToken");
        localStorage.removeItem("refreshToken");
        $store.commit("setToken", "");
        $store.commit("setRefreshToken", "");
        router.replace({ path: "/" });
        return Promise.reject(error);
      }

      try {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            requestsQueue.push({ resolve, reject });
          })
            .then(() => {
              const config = error.config;
              config.headers["Authorization"] =
                "Bearer " +
                (localStorage.getItem("userToken") || $store.state.token);
              return service(config);
            })
            .catch((err) => {
              return Promise.reject(err);
            });
        }

        const newAccessToken = await refreshToken();
        const config = error.config;
        config.headers["Authorization"] = "Bearer " + newAccessToken;
        return service(config);
      } catch (refreshError) {
        ElMessage.error("登录状态已过期，请重新登录");
        localStorage.removeItem("userToken");
        localStorage.removeItem("refreshToken");
        $store.commit("setToken", "");
        $store.commit("setRefreshToken", "");
        router.replace({ path: "/" });
        return Promise.reject(refreshError);
      }
    }

    let { message } = error;
    const serverMsg = pickServerMessage(error.response?.data);
    if (serverMsg) {
      message = serverMsg;
    } else if (message == "Network Error") {
      message = "后端接口连接异常";
    } else if (message?.includes("timeout")) {
      message = "系统接口请求超时";
    } else if (message?.includes("Request failed with status code")) {
      message = "系统接口" + message.substr(message.length - 3) + "异常";
    }
    if (!error.config?.silentError) {
      ElMessage.error(message);
    }
    return Promise.reject(error);
  }
);

export default service;

let downloadLoadingInstance: { close: () => void };

export function download(url: string, params: any, filename: string) {
  downloadLoadingInstance = ElLoading.service({
    text: "正在下载数据，请稍候",
    spinner: "el-icon-loading",
    background: "rgba(0, 0, 0, 0.7)",
  });
  return service
    .post(url, params, {
      transformRequest: [
        (params) => {
          return tansParams(params);
        },
      ],
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      responseType: "blob",
    })
    .then(async (data: any) => {
      const isLogin = await blobValidate(data);
      if (isLogin) {
        const blob = new Blob([data]);
        saveAs(blob, filename);
      } else {
        const resText = await data.text();
        const rspObj = JSON.parse(resText);
        const errMsg = rspObj.msg;
        ElMessage.error(errMsg);
      }
      downloadLoadingInstance.close();
    })
    .catch(() => {
      ElMessage.error("下载文件出现错误，请联系管理员！");
      downloadLoadingInstance.close();
    });
}
