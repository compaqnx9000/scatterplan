<template>
  <!-- 整体容器 - 悬浮球和功能轮盘作为一个整体 -->
  <div 
    class="floating-container" 
    :style="{ left: `${containerX}px`, top: `${containerY}px` }"
    @mouseenter="handleContainerMouseEnter"
    @mouseleave="handleContainerMouseLeave"
  >
    <!-- 悬浮球 -->
    <div 
      class="floating-ball" 
      @mousedown="handleMouseDown"
      :class="{ 'is-dragging': isDragging }"
    >
      <i class="fa fa-bars"></i>
    </div>

    <!-- 功能轮盘 -->
    <div 
      class="menu" 
      :style="{ 
        left: menuLeft, 
        top: '4px',
        opacity: isMenuShow ? 1 : 0,
        transform: isMenuShow ? 'scale(1)' : 'scale(0)',
        pointerEvents: isMenuShow ? 'auto' : 'none'
      }"
    >
      <div 
        class="menu-item" 
        v-for="(item, index) in menuItems" 
        :key="index"
        :data-tip="item.tip"
        @click="handleMenuItemClick(index)"
        :style="{ transform: isMenuShow ? 'scale(1)' : 'scale(0)', transitionDelay: `${index * 50}ms` }"
      >
        <i :class="item.icon"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

// 定义菜单项目类型
interface MenuItem {
  tip: string;
  icon: string;
}

// 状态变量
const isDragging = ref(false);
const startX = ref(0);
const startY = ref(0);
const containerX = ref(0);
const containerY = ref(0);
const isLeftSide = ref(false);
const isMenuShow = ref(false);
let leaveTimer: number | null = null;

// 菜单项目数据
const menuItems: MenuItem[] = [
  { tip: '主页', icon: 'fa fa-home' },
  { tip: '搜索', icon: 'fa fa-search' },
  { tip: '设置', icon: 'fa fa-cog' },
  { tip: '个人', icon: 'fa fa-user' },
  { tip: '通知', icon: 'fa fa-bell' }
];

// 计算菜单左侧位置
const menuLeft = ref('-299px');

// 初始化位置
const initPosition = () => {
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  // 初始右侧位置
  containerX.value = windowWidth + 160;
  containerY.value = windowHeight / 2 ;
  updateMenuPosition();
};

// 更新菜单位置
const updateMenuPosition = () => {
  if (isLeftSide.value) {
    // 左侧 -> 轮盘显示在悬浮球右侧
    menuLeft.value = '66px'; // 悬浮球宽度(56px) + 间距(10px)
  } else {
    // 右侧 -> 轮盘显示在悬浮球左侧
    menuLeft.value = '-299px'; // -(5个功能项宽度(48*5) + 间距(12*4) + 间距(10px))
  }
};

// 自动贴边逻辑
const autoStick = () => {
  const windowCenter = window.innerWidth / 2;
  isLeftSide.value = containerX.value < windowCenter;
  
  if (isLeftSide.value) {
    // 贴左侧
    containerX.value = 20;
  } else {
    // 贴右侧
    containerX.value = window.innerWidth + 160;
  }
  updateMenuPosition();
};

// 显示菜单
const showMenu = () => {
  if (isMenuShow.value) return;
  isMenuShow.value = true;
  updateMenuPosition();
};

// 隐藏菜单
const hideMenu = () => {
  if (!isMenuShow.value) return;
  isMenuShow.value = false;
};

// 鼠标按下事件
const handleMouseDown = (e: MouseEvent) => {
  console.log('e',e);
  
  isDragging.value = true;
  const container = e.currentTarget as HTMLElement;
  const rect = container.getBoundingClientRect();
  console.log('rect',rect);
  
  startX.value = e.clientX - rect.left ;
  startY.value = e.clientY - rect.top;
  
  // 隐藏菜单
  hideMenu();
  
  // 添加鼠标移动和释放事件监听
  const handleMouseMove = (moveEvent: MouseEvent) => {
    if (!isDragging.value) return;
    
    // 计算新位置
    let newX = moveEvent.clientX - startX.value;
    let newY = moveEvent.clientY - startY.value;
    
    // 限制在窗口内
    newX = Math.max(20, Math.min(window.innerWidth - 56 - 20, newX));
    newY = Math.max(20, Math.min(window.innerHeight - 56 - 20, newY));
    
    // 更新位置
    containerX.value = newX;
    containerY.value = newY;
  };
  
  const handleMouseUp = () => {
    if (isDragging.value) {
      isDragging.value = false;
      autoStick();
    }
    // 移除事件监听
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };
  
  // 添加事件监听
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};

// 容器鼠标进入事件
const handleContainerMouseEnter = () => {
  if (leaveTimer) {
    clearTimeout(leaveTimer);
    leaveTimer = null;
  }
  showMenu();
};

// 容器鼠标离开事件
const handleContainerMouseLeave = () => {
  leaveTimer = window.setTimeout(() => {
    hideMenu();
  }, 300);
};

// 菜单项点击事件
const handleMenuItemClick = (index: number) => {
  ElMessage.success(`点击了${menuItems[index].tip}`);
  hideMenu();
};

// 窗口大小变化处理
const handleWindowResize = () => {
  autoStick();
  if (isMenuShow.value) {
    updateMenuPosition();
  }
};

// 初始化
onMounted(() => {
  initPosition();
  // 监听窗口大小变化
  window.addEventListener('resize', handleWindowResize);
  
  // 清理函数
  return () => {
    window.removeEventListener('resize', handleWindowResize);
    if (leaveTimer) {
      clearTimeout(leaveTimer);
    }
  };
});
</script>

<style scoped>
.floating-container {
  position: fixed;
  z-index: 9999;
 pointer-events: all;
}

.floating-ball {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  color: #fff;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.floating-ball.is-dragging {
  cursor: grabbing;
  transition: none;
}

.menu {
  position: absolute;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
  z-index: 1;
  display: flex;
  gap: 12px;
}

.menu-item {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #409eff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-item i {
  font-size: 20px;
}

.menu-item:hover {
  background-color: #409eff;
  color: #fff;
}
</style>
    