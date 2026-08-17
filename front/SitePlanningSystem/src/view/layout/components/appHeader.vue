<template>
  <div class="app-header" :class="{ 'is-pick-locked': pickLocked }" ref="headerRef">
    <div class="app-header__bar">
      <button
        class="app-header__brand"
        type="button"
        title="首页"
        :disabled="pickLocked"
        @click="goHome"
      >
        <span class="app-header__brand-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path
              d="M12 2.5v4.2"
              fill="none"
              stroke="#bef264"
              stroke-width="1.8"
              stroke-linecap="round"
            />
            <path
              d="M8.2 4.2c2.1 1.4 5.5 1.4 7.6 0"
              fill="none"
              stroke="#bef264"
              stroke-width="1.6"
              stroke-linecap="round"
            />
            <path
              d="M6.2 6.4c3.2 2.1 8.4 2.1 11.6 0"
              fill="none"
              stroke="#bef264"
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
        </span>
        <span class="app-header__brand-text">
          <span class="app-header__brand-en">Scatter<span>Plan</span></span>
          <span class="app-header__brand-zh">散射通信规划系统</span>
        </span>
      </button>

      <div class="app-header__spacer">
        <PlaceSearch :disabled="pickLocked" />
      </div>

      <div class="app-header__right">
        <div v-if="projectOpen" class="app-header__project">
          <span class="app-header__project-label">当前工程</span>
          <span class="app-header__project-name" :title="projectName">{{ projectName }}</span>
        </div>
        <button
          class="app-header__user"
          type="button"
          :class="{ 'is-open': profileOpen }"
          :disabled="pickLocked"
          @click.stop="toggleProfile"
        >
          <img class="app-header__avatar" src="@/assets/images/layout/user_logo.png" alt="" />
          <div class="app-header__user-meta">
            <div class="app-header__user-name">{{ displayName }}</div>
            <div class="app-header__user-sub">账户</div>
          </div>
          <span class="app-header__chevron" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                d="M7 10l5 5 5-5"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
        </button>

        <transition name="el-zoom-in-top">
          <div v-show="profileOpen" class="app-header__menu" @click.stop>
            <div class="app-header__menu-card">
              <img class="app-header__menu-avatar" src="@/assets/images/layout/user_logo.png" alt="" />
              <div class="app-header__menu-name">{{ displayName }}</div>
              <div class="app-header__menu-email">{{ displayEmail }}</div>
            </div>

            <div class="app-header__menu-list">
              <button
                class="app-header__menu-item"
                type="button"
                :class="{ 'is-open': systemOpen }"
                @click="systemOpen = !systemOpen"
              >
                <span class="app-header__menu-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M4.8 7.2h14.4v9.6H4.8V7.2Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linejoin="round"
                    />
                    <path d="M8 4.8v2.4M16 4.8v2.4M8 16.8v2.4M16 16.8v2.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
                  </svg>
                </span>
                <span>系统数据</span>
                <span class="app-header__menu-arrow" :class="{ 'is-open': systemOpen }" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M9 7l5 5-5 5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>
              </button>

              <div v-show="systemOpen" class="app-header__submenu">
                <button
                  v-for="child in systemChildren"
                  :key="child.value"
                  class="app-header__submenu-item"
                  type="button"
                  :class="{ 'is-active': isSubMenuItemActive(child.value) }"
                  @click="subMenuClick(child)"
                >
                  <img v-if="child.icon === 'user'" src="@/assets/images/layout/system_user.png" alt="" />
                  <img v-if="child.icon === 'map'" src="@/assets/images/layout/system_map.png" alt="" />
                  <img v-if="child.icon === 'dict'" src="@/assets/images/layout/system_dict.png" alt="" />
                  <span>{{ child.label }}</span>
                </button>
              </div>
            </div>

            <div class="app-header__menu-divider"></div>

            <div class="app-header__menu-list">
              <button class="app-header__menu-item" type="button" @click="goSitePlanning">
                <span class="app-header__menu-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M5 6.5h14M5 12h14M5 17.5h9"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>
                <span>站点规划结果</span>
              </button>
            </div>

            <div class="app-header__menu-divider"></div>

            <div class="app-header__menu-list">
              <button class="app-header__menu-item app-header__menu-item--danger" type="button" @click="handleLogout">
                <span class="app-header__menu-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M10 5.5H6.8A1.8 1.8 0 0 0 5 7.3v9.4a1.8 1.8 0 0 0 1.8 1.8H10"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                    />
                    <path
                      d="M10.5 12H19M16.2 8.8 19.4 12l-3.2 3.2"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>
                <span>退出</span>
              </button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, onUnmounted, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import store from "@/store/index";
import PlaceSearch from "@/components/placeSearch/index.vue";
import { homeRouteForCurrentProject, rememberCurrentProjectId } from "@/view/home/service/projectSession";

let currentInstance = getCurrentInstance();
let $bus = currentInstance?.appContext.config.globalProperties.$bus;

const userInfo = localStorage.getItem("loginData")
  ? JSON.parse(localStorage.getItem("loginData") || "{}")
  : {};

const displayName = computed(() => userInfo.userName || userInfo.username || "admin");
const displayEmail = computed(
  () => userInfo.email || userInfo.userEmail || `${displayName.value}@local`
);

const profileOpen = ref(false);
const systemOpen = ref(false);
const pickLocked = ref(false);
const projectOpen = ref(false);
const projectName = ref("");
const subMenuActive: any = ref("");
const headerRef = ref<HTMLElement | null>(null);

const systemChildren = [
  {
    label: "用户管理",
    value: "/user",
    path: "/systemData/systemuser",
    icon: "user",
  },
  {
    label: "地图接口服务",
    value: "/map",
    path: "/systemData/systemmap",
    icon: "map",
  },
  {
    label: "数据字典配置",
    value: "/dict",
    path: "/systemData/systemdict",
    icon: "dict",
  },
];

const router = useRouter();
const route = useRoute();

function isSubMenuItemActive(value: string) {
  return subMenuActive.value === value || route.path.search(value) != -1;
}

function toggleProfile() {
  if (pickLocked.value) return;
  profileOpen.value = !profileOpen.value;
  if (!profileOpen.value) systemOpen.value = false;
}

function closeProfile() {
  profileOpen.value = false;
  systemOpen.value = false;
}

function goHome() {
  if (pickLocked.value) return;
  closeProfile();
  router.push(homeRouteForCurrentProject());
}

function goSitePlanning() {
  if (pickLocked.value) return;
  closeProfile();
  $bus?.emit("openSitePlanningResults");
}

function subMenuClick(val: any) {
  if (pickLocked.value) return;
  subMenuActive.value = val.value;
  closeProfile();
  router.push(val.path);
}

const handleLogout = () => {
  if (pickLocked.value) return;
  closeProfile();
  localStorage.removeItem("userToken");
  localStorage.removeItem("refreshToken");
  store.commit("setToken", "");
  store.commit("setRefreshToken", "");
  rememberCurrentProjectId("");
  router.replace("/");
  $bus.emit("Logout");
};

const onMapPickMode = (active: boolean) => {
  pickLocked.value = !!active;
  if (active) closeProfile();
};

const onProjectOpen = (open: boolean) => {
  projectOpen.value = !!open;
  if (!open) projectName.value = "";
};

const onProjectName = (name: string) => {
  projectName.value = name || "";
};

const onLogout = () => {
  projectOpen.value = false;
  projectName.value = "";
};

const onDocClick = (e: MouseEvent) => {
  if (!profileOpen.value) return;
  const el = headerRef.value;
  if (el && !el.contains(e.target as Node)) {
    closeProfile();
  }
};

onMounted(() => {
  document.addEventListener("click", onDocClick);
  $bus?.on("mapPickMode", onMapPickMode);
  $bus?.on("workflowProjectOpen", onProjectOpen);
  $bus?.on("workflowProjectName", onProjectName);
  $bus?.on("Logout", onLogout);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  $bus?.off("mapPickMode", onMapPickMode);
  $bus?.off("workflowProjectOpen", onProjectOpen);
  $bus?.off("workflowProjectName", onProjectName);
  $bus?.off("Logout", onLogout);
});
</script>

<style lang="scss" scoped>
.app-header {
  width: 100%;
  pointer-events: auto;
  flex-shrink: 0;
  padding: 14px 18px 0;
  box-sizing: border-box;
  background: transparent;

  &.is-pick-locked {
    pointer-events: none !important;
    opacity: 0.55;

    * {
      pointer-events: none !important;
      cursor: default !important;
    }
  }

  &__bar {
    width: 100%;
    min-height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 10px 18px;
    border-radius: 999px;
    background: rgba(24, 26, 24, 0.82);
    border: 1px solid rgba(180, 200, 220, 0.18);
    box-shadow:
      0 18px 48px rgba(0, 0, 0, 0.38),
      inset 0 1px 0 rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(22px) saturate(1.15);
    -webkit-backdrop-filter: blur(22px) saturate(1.15);
    box-sizing: border-box;
  }

  &__brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: none;
    background: transparent;
    color: #fff;
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 12px;
    flex-shrink: 0;

    &:hover,
    &:focus,
    &:focus-visible {
      background: transparent;
      outline: none;
    }
  }

  &__brand-icon {
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;

    svg {
      width: 24px;
      height: 24px;
    }
  }

  &__brand-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1px;
    line-height: 1.15;
    color: #ffffff;
    white-space: nowrap;
  }

  &__brand-en {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.01em;

    span {
      color: #bef264;
      font-weight: 600;
      margin-left: 0;
    }
  }

  &__brand-zh {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.04em;
    color: var(--gotham-text-muted, #8b8790);
  }

  &__spacer {
    flex: 1;
    display: flex;
    justify-content: center;
    min-width: 0;
    padding: 0 12px;
  }

  &__right {
    position: relative;
    display: flex;
    align-items: center;
    flex-shrink: 0;
    gap: 10px;
  }

  &__project {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    max-width: 280px;
    min-height: 36px;
    padding: 4px 14px;
    border-radius: 999px;
    background: rgba(163, 230, 53, 0.12);
    border: 1px solid rgba(163, 230, 53, 0.28);
    color: #fff;
  }

  &__project-label {
    font-size: 10px;
    letter-spacing: 0.06em;
    color: rgba(190, 200, 212, 0.75);
    white-space: nowrap;
  }

  &__project-name {
    font-size: 12px;
    font-weight: 600;
    color: #ecfccb;
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__user {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: none;
    background: transparent;
    padding: 4px 8px 4px 4px;
    border-radius: 999px;
    cursor: pointer;
    color: #fff;

    &:hover,
    &.is-open {
      background: rgba(255, 255, 255, 0.08);
    }
  }

  &__avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid rgba(180, 200, 220, 0.18);
  }

  &__user-meta {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    text-align: left;
  }

  &__user-name {
    font-family: var(--font-mono, 'IBM Plex Mono', 'Cascadia Mono', monospace);
    font-size: 12px;
    font-weight: 600;
    color: var(--gotham-text, #e8e2d2);
  }

  &__user-sub {
    font-family: var(--font-mono, 'IBM Plex Mono', 'Cascadia Mono', monospace);
    font-size: 11px;
    color: var(--gotham-text-muted, #8b8790);
    margin-top: 2px;
  }

  &__chevron {
    width: 14px;
    height: 14px;
    color: var(--gotham-text-muted, #8b8790);
    display: inline-flex;

    svg {
      width: 14px;
      height: 14px;
    }
  }

  &__menu {
    --gotham-bg: #121412;
    --gotham-bg-elevated: #181a18;
    --gotham-panel: rgba(24, 26, 24, 0.92);
    --gotham-panel-solid: #1a1d1a;
    --gotham-border: rgba(255, 255, 255, 0.08);
    --gotham-border-strong: rgba(255, 255, 255, 0.16);
    --gotham-text: #ffffff;
    --gotham-text-muted: #9ca3af;
    --gotham-text-dim: #6b7280;
    --gotham-accent: #a3e635;
    --gotham-accent-soft: rgba(163, 230, 53, 0.16);
    --gotham-accent-hover: #b6f04a;
    --gotham-danger: #c45c4a;
    --font-mono: 'IBM Plex Mono', 'Cascadia Mono', monospace;
    --font-ui: 'IBM Plex Sans', 'Noto Sans SC', sans-serif;

    position: absolute;
    top: calc(100% + 12px);
    right: 0;
    width: 280px;
    padding: 10px;
    border-radius: 12px;
    background: var(--gotham-panel);
    border: 1px solid var(--gotham-border);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(22px) saturate(1.15);
    -webkit-backdrop-filter: blur(22px) saturate(1.15);
    z-index: 1300;
    font-family: var(--font-mono);
    font-variant-numeric: tabular-nums;
    font-size: 12px;
    line-height: 1.45;
    color: #e8e8e8;
    -webkit-font-smoothing: antialiased;
    box-sizing: border-box;
    scrollbar-width: thin;
    scrollbar-color: rgba(157, 223, 46, 0.55) transparent;

    *,
    *::before,
    *::after {
      box-sizing: border-box;
      font-family: inherit !important;
      font-size: inherit !important;
      line-height: inherit;
    }
  }

  &__menu-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 14px 10px 12px;
    border-radius: 10px;
    background: var(--gotham-bg-elevated);
    border: 1px solid var(--gotham-border);
    margin-bottom: 8px;
  }

  &__menu-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid var(--gotham-border-strong);
    margin-bottom: 8px;
  }

  &__menu-name {
    font-size: 12px !important;
    font-weight: 600;
    color: var(--gotham-text);
  }

  &__menu-email {
    margin-top: 2px;
    font-size: 11px !important;
    color: var(--gotham-text-muted);
  }

  &__menu-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  &__menu-item {
    width: 100%;
    min-height: 34px;
    border: none;
    background: transparent;
    color: var(--gotham-text);
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 10px;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    font-size: 12px !important;

    span {
      font-size: 12px !important;
    }

    &:hover,
    &.is-active,
    &.is-open {
      background: var(--gotham-accent-soft);
      color: var(--gotham-accent-hover);
    }

    &--danger:hover {
      background: rgba(196, 92, 74, 0.14);
      color: var(--gotham-danger);
    }
  }

  &__menu-icon {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
    display: inline-flex;
    color: var(--gotham-text-muted);

    svg {
      width: 14px;
      height: 14px;
    }
  }

  &__menu-arrow {
    margin-left: auto;
    width: 12px;
    height: 12px;
    display: inline-flex;
    color: var(--gotham-text-dim);
    transition: transform 0.18s ease;

    svg {
      width: 12px;
      height: 12px;
    }

    &.is-open {
      transform: rotate(90deg);
    }
  }

  &__submenu {
    padding: 2px 0 6px 16px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  &__submenu-item {
    width: 100%;
    min-height: 30px;
    border: none;
    background: transparent;
    color: var(--gotham-text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 10px;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    font-size: 12px !important;

    span {
      font-size: 12px !important;
    }

    img {
      width: 14px;
      height: 14px;
    }

    &:hover,
    &.is-active {
      background: var(--gotham-accent-soft);
      color: var(--gotham-text);
    }
  }

  &__menu-divider {
    height: 1px;
    margin: 6px 4px;
    background: var(--gotham-border);
  }
}
</style>
