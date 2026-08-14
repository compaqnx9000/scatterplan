<template>
  <div v-if="visible" class="login-modal" @mousedown.stop @click.stop>
    <div class="login-modal__mask"></div>
    <div class="login-modal__panel" role="dialog" aria-modal="true" aria-label="登录">
      <div class="login-modal__header">
        <div class="login-modal__logo" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path
              d="M12 2.5v4.2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
            <path
              d="M8.2 4.2c2.1 1.4 5.5 1.4 7.6 0"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
            <path
              d="M6.2 6.4c3.2 2.1 8.4 2.1 11.6 0"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
            <path
              d="M10.2 8.8h3.6L15 21.2H9L10.2 8.8Z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
            <path
              d="M8.4 21.2h7.2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <div class="login-modal__titles">
          <div class="login-modal__brand">ScatterPlan</div>
          <div class="login-modal__product">散射通信规划系统</div>
          <div class="login-modal__title">登录</div>
        </div>
      </div>

      <form class="login-modal__form" @submit.prevent="checkLogin">
        <label class="login-modal__field">
          <span class="login-modal__label">USERNAME</span>
          <input
            v-model="loginData.userName"
            class="login-modal__input"
            type="text"
            autocomplete="username"
            placeholder=""
          />
        </label>

        <label class="login-modal__field">
          <span class="login-modal__label">PASSWORD</span>
          <input
            v-model="loginData.password"
            class="login-modal__input"
            type="password"
            autocomplete="current-password"
            placeholder=""
            @keyup.enter="checkLogin"
          />
        </label>

        <button class="login-modal__submit" type="submit" :disabled="pageData.loginLoading">
          {{ pageData.loginLoading ? "..." : "ENTER" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script lang="ts" setup>
//@ts-nocheck
import { reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import store from "@/store/index";
import { login } from "@/request/user";
import { ElMessage } from "element-plus";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["success"]);
const router = useRouter();

const pageData: any = reactive({
  remember: true,
  loginLoading: false,
});

const loginData: any = reactive({
  userName: "",
  password: "",
});

const loadRemembered = () => {
  const localLoginInfo: any = localStorage.getItem("loginData");
  if (localLoginInfo) {
    try {
      const parsed = JSON.parse(localLoginInfo);
      loginData.userName = parsed.userName || "";
      loginData.password = parsed.password || "";
    } catch (e) {}
  }
};

onMounted(loadRemembered);
watch(
  () => props.visible,
  (val) => {
    if (val) loadRemembered();
  }
);

async function checkLogin() {
  if (!loginData.userName) {
    ElMessage.error("请输入用户名");
    return;
  }
  if (!loginData.password) {
    ElMessage.error("请输入密码");
    return;
  }

  pageData.loginLoading = true;
  try {
    const loginResult: any = await login(loginData.userName, loginData.password);

    localStorage.setItem("userToken", loginResult.access);
    store.commit("setToken", loginResult.access);

    localStorage.setItem("is_staff", loginResult.is_staff);
    store.commit("setIs_staff", loginResult.is_staff);

    localStorage.setItem("refreshToken", loginResult.refresh);
    store.commit("setRefreshToken", loginResult.refresh);

    if (pageData.remember) {
      localStorage.setItem(
        "loginData",
        JSON.stringify({
          userName: loginData.userName,
          password: loginData.password,
        })
      );
    } else {
      localStorage.setItem("loginData", "");
    }

    if (router.currentRoute.value.path === "/login") {
      router.replace({ path: "/" });
    }

    emit("success");
  } catch (error) {
    // request layer already toasts
  } finally {
    pageData.loginLoading = false;
  }
}
</script>

<style lang="scss" scoped>
.login-modal {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: all;

  &__mask {
    position: absolute;
    inset: 0;
    background: rgba(4, 8, 14, 0.42);
    backdrop-filter: blur(2px);
  }

  &__panel {
    position: relative;
    width: min(420px, calc(100vw - 48px));
    padding: 28px 28px 26px;
    background: #1a1d22;
    border: 1px solid rgba(180, 190, 200, 0.28);
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.55);
    color: #fff;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
  }

  &__logo {
    width: 78px;
    height: 78px;
    border: 2px solid #f0c000;
    color: #f0c000;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    svg {
      width: 44px;
      height: 44px;
      display: block;
    }
  }

  &__titles {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__brand {
    font-size: 12px;
    letter-spacing: 0.18em;
    color: rgba(235, 240, 245, 0.9);
    font-weight: 600;
  }

  &__product {
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.04em;
    color: rgba(180, 190, 200, 0.78);
  }

  &__title {
    font-size: 34px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  &__field {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__label {
    font-size: 11px;
    letter-spacing: 0.14em;
    color: rgba(170, 178, 188, 0.95);
    font-weight: 600;
  }

  &__input {
    width: 100%;
    height: 44px;
    border: none;
    outline: none;
    background: #000000;
    color: #ffffff;
    padding: 0 14px;
    font-size: 14px;
    box-sizing: border-box;

    &:focus {
      box-shadow: inset 0 0 0 1px rgba(240, 192, 0, 0.45);
    }
  }

  &__submit {
    margin-top: 8px;
    width: 100%;
    height: 48px;
    border: none;
    background: #f0c000;
    color: #111111;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.12em;
    cursor: pointer;

    &:hover:not(:disabled) {
      filter: brightness(1.05);
    }

    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }
}
</style>
