<template>
  <div class="login-layout">
    <!-- <div class="login-layout__bg"></div> -->

    <div class="login-layout__form">
      <div class="login-layout__form__left">
        <div class="login-layout__form__left__title__wrap">
          <div class="login-layout__form__left__title1">Welcome！</div>
          <div class="login-layout__form__left__title2">
            散射通信规划系统
          </div>
        </div>
      </div>
      <div class="login-layout__form__right">
        <div class="login-layout__form__right__title">账号登录</div>
        <div class="login-layout__form__right__content">
          <el-form
            :model="loginData"
            :rules="rules"
            ref="loginFormRef"
            style="width: 100%"
          >
            <el-form-item label="" prop="userName">
              <el-input
                v-model="loginData.userName"
                style="
                  width: 100%;
                  border: 1px solid #d9d9d9;
                  border-radius: 4px;
                "
                size="large"
                placeholder="请输入账号"
                :prefix-icon="User"
                class="custom-input"
              />
            </el-form-item>
            <el-form-item label="" prop="password">
              <el-input
                v-model="loginData.password"
                type="password"
                style="
                  width: 100%;
                  border: 1px solid #d9d9d9;
                  border-radius: 4px;
                "
                size="large"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                class="custom-input"
              />
            </el-form-item>
          </el-form>
          <div class="login-layout__form__right__btn">
            <el-button
              type="primary"
              size="large"
              :loading="pageData.loginLoading"
              @click="checkLogin"
              style="width: 100%; margin-top: 70px"
              >登录</el-button
            >
          </div>
        </div>
      </div>
    </div>

    <!-- <div class="login-layout__bg"></div>
        <div class="login-layout__form">
            <div class="login-layout__form__layout">
                <h2>{{ pageData.systemName }}</h2>
                <div class="login-layout__form__item">
                    <i class="el-icon-delete"></i>
                    <div class="login-layout__form__item__name">账号：</div>
                    <div class="login-layout__form__item__write">
                        <input type="text" v-model="loginData.userName" maxlength="11" placeholder="请输入" />
                    </div>
                </div>
                <div class="login-layout__form__item">
                    <div class="login-layout__form__item__name">密码：</div>
                    <div class="login-layout__form__item__write">
                        <input type="password" maxlength="11" v-model="loginData.password" placeholder="请输入" />
                    </div>
                </div>
                <div class="login-layout__checkbox">
                    <el-checkbox v-model="pageData.remember">记住账号密码</el-checkbox>
                </div>
                <el-button type="primary" size="large" :loading="pageData.loginLoading"
                    @click="checkLogin">登录</el-button>
            </div>
        </div> -->
  </div>
</template>

<script lang="ts" setup>
import router from "@/router/index";
import store from "@/store/index";
import { login, captchaImage } from "@/request/user";
// import { getRouters } from "@/request/system";
import { ElButton, ElCheckbox, ElMessage } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
let pageData: any = reactive({
  imgSrc: "", //验证码图片
  systemName: import.meta.env.VITE_APP_TITLE,
  remember: true, //是否记住账号
  loginLoading: false,
});
let loginData: any = reactive({
  userName: "",
  password: "",
  code: "",
  uuid: "",
});
let rules: any = reactive({
  userName: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
});
onMounted(async () => {
  let localLoginInfo: any = localStorage.getItem("loginData");
  if (localLoginInfo) {
    loginData.userName = JSON.parse(localLoginInfo).userName;
    loginData.password = JSON.parse(localLoginInfo).password;
  }
  // getCodeImg();
});
async function getCodeImg() {
  try {
    let codeImg: any = await captchaImage();
    pageData.imgSrc = "data:image/gif;base64," + codeImg.img;
    loginData.uuid = codeImg.uuid;
  } catch (error) {
    console.log("请求失败结果", error);
  }
}
async function checkLogin() {
  if (!loginData.userName) {
    ElMessage.error("请输入用户名");
    return;
  }
  if (!loginData.password) {
    ElMessage.error("请输入密码");
    return;
  }
  // if (!loginData.code) {
  //     ElMessage.error("请输入验证码");
  //     return;
  // }
  let loginResult: any;
  pageData.loginLoading = true;
  try {
    loginResult = await login(
        loginData.userName,
        loginData.password
    );
    pageData.loginLoading = false;
    console.log('loginResult',loginResult);
    
   
    localStorage.setItem("userToken", loginResult.access);
    store.commit("setToken", loginResult.access);

    localStorage.setItem("is_staff", loginResult.is_staff);
    store.commit("setIs_staff", loginResult.is_staff);

     localStorage.setItem("refreshToken", loginResult.refresh);
    store.commit("setRefreshToken", loginResult.refresh);
    // 存储账号密码
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
    router.replace({ path: "/" });

    // await store.dispatch("GetUserInfo");
    // // console.log("===");
    // getRouters().then(response => {
    //     let roterList = response.data || [];
    //     let path = roterList[0].path;
    //     if (roterList[0].children && roterList[0].children.length) {
    //         if (path === '/') {
    //             path += roterList[0].children[0].path;
    //         } else {
    //             path += '/' + roterList[0].children[0].path;
    //         }
    //     }
    //     router.replace({ path: path });
    // });
  } catch (error) {
    pageData.loginLoading = false;
    // getCodeImg();
  }
}
</script>

<style lang="scss" scoped>
.login-layout {
  width: 100vw;
  height: 100vh;
  background: url("@/assets/images/login/login_bg.png") no-repeat center center;
  background-size: 100% 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 30px;
  box-sizing: border-box;
  position: relative;

  &__form {
    display: flex;
    // justify-content: space-between;
    align-items: center;
    border-radius: 8px;
    opacity: 1;
    height:calc((680/1080)*100vh);
    width: calc((1094/1920) * 100vw);
    background: #ffffff;
    z-index: 100;
    transform: translateY(-10px);

    &__left {
      width: 50%;
      height: 100%;
      background: url("@/assets/images/login/form_left_bg.png") no-repeat center
        center;
      background-size: 100% 100%;
      box-sizing: border-box;
      &__title__wrap {
        padding: calc(60 / 1080 * 100vh) calc(64 / 1920 * 100vw);
        background: url("@/assets/images/login/login_left_top_bg.png") no-repeat
          center center;

        background-size: 100% 100%;
        box-sizing: border-box;
      }
      &__title1 {
        font-size: calc(48 / 1920 * 100vw);
        font-weight: normal;
        line-height: calc(56 / 1080 * 100vh);
        color: #ffffff;
      }
      &__title2 {
        font-size: calc(24 / 1080 * 100vh);
        font-weight: normal;
        line-height: calc(24 / 1080 * 100vh);
        color: #ffffff;
        margin-top: calc(6 / 1080 * 100vh);
      }
    }
    &__right {
      padding: calc(150 / 1080 * 100vh) calc(88 / 1920 * 100vw);
      display: flex;
      flex-direction: column;
      //   justify-content: space-between;
      box-sizing: border-box;
      width: 50%;
      &__title {
        position: relative;
        width: auto;
        font-size: calc(40 / 1920 * 100vw);
        font-weight: 600;
        color: #000;
        flex: 0 0 auto; /* 禁用伸缩 */
        width: auto; /* 宽度由内容决定 */
        align-self: flex-start; /* 关键：在纵向Flex中让元素左对齐，宽度适应内容 */
        white-space: nowrap; /* 可选：防止文本换行（根据需求决定） */
      }
      &__title::before {
        content: "";
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: calc(30 / 1920 * 100vw);
        height: calc(4 / 1080 * 100vh);
        background: #1890ff;
      }
      &__content {
        margin-top: calc(70 / 1080 * 100vh);
      }
      &__btn {
      }
    }
  }
}
:deep(.el-form-item__label) {
  // color: #fff !important;
  color: #555555 !important;
  font-size: 16px !important;
  width: auto !important;
  // flex-grow: 1;
  white-space: nowrap;

  // color: #fff;
}

:deep(.custom-input .el-input__prefix .el-icon) {
  color: #1890ff !important;
}
</style>