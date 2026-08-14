import $store from "@/store/index";
import service from "@/request/request";
import router from "@/router";

let isRefreshing = false;
let requestsQueue: Array<{ resolve: Function; reject: Function }> = [];

const refreshToken = async () => {
  try {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        requestsQueue.push({ resolve, reject });
      });
    }

    isRefreshing = true;

    const refreshTokenValue =
      localStorage.getItem("refreshToken") || $store.state.refreshToken;
    if (!refreshTokenValue) {
      router.push({ path: "/" });
      return;
    }

    const response: any = await service({
      url: "/jwt/refresh/",
      method: "post",
      headers: {
        isToken: false,
        Authorization: "Bearer " + refreshTokenValue,
      },
      data: {
        refresh: refreshTokenValue,
      },
    });

    const newAccessToken = response.access || response.token;
    const newRefreshToken = response.refresh;

    if (!newAccessToken) {
      throw new Error("Failed to get new access token");
    }

    if (newAccessToken) {
      localStorage.setItem("userToken", newAccessToken);
      $store.commit("setToken", newAccessToken);
    }
    if (newRefreshToken) {
      localStorage.setItem("refreshToken", newRefreshToken);
      $store.commit("setRefreshToken", newRefreshToken);
    }

    requestsQueue.forEach((item) => {
      item.resolve(newAccessToken);
    });
    requestsQueue = [];

    return newAccessToken;
  } catch (error) {
    requestsQueue.forEach((item) => {
      item.reject(error);
    });
    requestsQueue = [];

    localStorage.removeItem("userToken");
    localStorage.removeItem("refreshToken");
    $store.commit("setToken", "");
    $store.commit("setRefreshToken", "");
    router.replace({ path: "/" });

    throw error;
  } finally {
    isRefreshing = false;
  }
};

export default refreshToken;
