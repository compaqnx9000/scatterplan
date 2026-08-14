<template>
  <div class="screenshot-container">
    <!-- 触发按钮 -->
    <button @click="startScreenshot" class="screenshot-btn">
      <i class="fa fa-crop"></i>
      <span>开始截图</span>
    </button>

    <!-- 截图遮罩层 -->
    <div 
      v-if="isActive"
      class="screenshot-overlay"
      :style="{ cursor: isSelectionCompleted ? 'default' : 'crosshair' }"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @keydown.esc="cancelScreenshot"
      tabindex="0"
      ref="overlayRef"
    >
      <!-- 选中区域高亮显示 -->
      <div 
        class="selected-area-highlight"
        :style="{
          clipPath: isSelecting ? `inset(${clipTop}px ${clipRight}px ${clipBottom}px ${clipLeft}px)` : 'none'
        }"
      ></div>

      <!-- 选中区域的边框 -->
      <div 
        v-if="isSelectionCompleted || isSelecting"
        :style="{
          top: `${clipTop}px`,
          left: `${clipLeft}px`,
          width: `${clipWidth}px`,
          height: `${clipHeight}px`,
        }"
        class="selection-border"
      >
        <!-- 边角控制点 -->
        <div class="control-point" data-control="topleft"></div>
        <div class="control-point" data-control="topright"></div>
        <div class="control-point" data-control="bottomleft"></div>
        <div class="control-point" data-control="bottomright"></div>
      </div>

      <!-- 绘制的标注内容 -->
      <canvas 
        v-if="isSelectionCompleted || isSelecting"
        :style="{
          top: `${clipTop}px`,
          left: `${clipLeft}px`,
          width: `${clipWidth}px`,
          height: `${clipHeight}px`,
        }"
        class="drawing-canvas"
        :width="clipWidth"
        :height="clipHeight"
        ref="drawCanvas"
      ></canvas>

      <!-- 工具栏 -->
      <div 
        v-if="isSelectionCompleted || isSelecting"
        :style="{
            color: '#000',
          top: `${clipTop + clipHeight + 10}px`,
          left: `calc(${clipLeft}px + ${clipWidth / 2}px - 150px)`,
        }"
        class="toolbar"
      >
        <el-button 
          @click.stop="setTool('arrow')"
          :class="{ active: currentTool === 'arrow' }"
        >
          <i class="fa fa-long-arrow-right">箭头</i>
        </el-button>
        <el-button 
          @click.stop="setTool('rectangle')"
          :class="{ active: currentTool === 'rectangle' }"
        >
          <i class="fa fa-square-o">矩形</i>
        </el-button>
        <el-button 
          @click.stop="setTool('circle')"
          :class="{ active: currentTool === 'circle' }"
        >
          <i class="fa fa-circle-o">圆形</i>
        </el-button>
        <el-button 
          @click.stop="setTool('text')"
          :class="{ active: currentTool === 'text' }"
        >
          <i class="fa fa-font">文字</i>
        </el-button>
        <div class="toolbar-divider"></div>
        <el-button 
          @click.stop="undo"
        >
          <i class="fa fa-undo">撤销</i>
        </el-button>
        <div class="toolbar-divider"></div>
        <el-button 
          @click.stop="cancelScreenshot"
        >
          <i class="fa fa-times">取消</i>
        </el-button>
        <el-button 
          @click.stop="saveScreenshot"
          class="save-btn"
        >
          <i class="fa fa-check">保存</i>
        </el-button>
      </div>

      <!-- 文字输入框 (仅在文字工具激活且点击时显示) -->
      <input
        v-if="isTextEditing"
        v-model="textContent"
        :style="{
          top: `${textPosition.y}px`,
          left: `${textPosition.x}px`,
        }"
        class="text-input"
        type="text"
        @blur="finishTextEditing"
        @keydown.enter="finishTextEditing"
        @click.stop
        ref="textInput"
        placeholder="输入文字..."
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';

// 截图状态
const isActive = ref(false);
const isSelecting = ref(false);
const isSelectionCompleted = ref(false); // 新增：表示区域选择是否已完成
const isDrawing = ref(false);
const isTextEditing = ref(false);

// 截图区域坐标
const startX = ref(0);
const startY = ref(0);
const clipLeft = ref(0);
const clipTop = ref(0);
const clipRight = ref(0);
const clipBottom = ref(0);
const clipWidth = ref(0);
const clipHeight = ref(0);

// 绘制相关
const drawCanvas = ref<HTMLCanvasElement | null>(null);
const currentTool = ref<'arrow' | 'rectangle' | 'circle' | 'text'>('arrow');
const drawHistory = ref<ImageData[]>([]);
const overlayRef = ref<HTMLDivElement | null>(null);

// 文字工具相关
const textContent = ref('');
const textPosition = ref({ x: 0, y: 0 });
const textInput = ref<HTMLInputElement | null>(null);

// 开始截图
const startScreenshot = async () => {
  try {
    // 请求屏幕捕获权限
    const stream = await navigator.mediaDevices.getDisplayMedia({
      // preferCurrentTab: true,
      video: {
        // cursor: 'always'
      }
    });

    // 初始化截图状态
    isActive.value = true;
    isSelecting.value = false;
    isDrawing.value = false;
    isTextEditing.value = false;
    drawHistory.value = [];
    
    // 等待DOM更新后聚焦遮罩层以捕获键盘事件
    await nextTick();
    overlayRef.value?.focus();

    // 监听流结束事件
    stream.getTracks().forEach(track => {
      track.onended = () => {
        cancelScreenshot();
      };
    });
  } catch (err) {
    console.error('截图失败:', err);
    alert('无法启动截图功能，请确保您的浏览器支持屏幕捕获');
  }
};

// 取消截图
const cancelScreenshot = () => {
  isActive.value = false;
  isSelecting.value = false;
  isSelectionCompleted.value = false; // 重置选择完成状态
  isDrawing.value = false;
  isTextEditing.value = false;
  drawHistory.value = [];
};

// 鼠标按下事件 - 开始选择区域
const handleMouseDown = (e: MouseEvent) => {
  if (!isActive.value) return;

  // 如果区域选择已完成，不允许再次选择区域
  if (isSelectionCompleted.value) {
    // 直接处理标注工具
    isSelecting.value = false;
  }
  // 如果还未选择区域，则开始选择
  else if (!isSelecting.value) {
    startX.value = e.clientX;
    startY.value = e.clientY;
    isSelecting.value = true;
    return;
  }

  // 已选择区域，处理标注工具
  const canvas = drawCanvas.value;
  if (!canvas) return;

  // 计算鼠标在画布内的相对位置
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  // 处理不同工具
  if (currentTool.value === 'text') {
    // 文字工具 - 显示输入框
    isTextEditing.value = true;
    textPosition.value = { x: e.clientX, y: e.clientY };
    textContent.value = '';
    
    nextTick(() => {
      textInput.value?.focus();
    });
    return;
  }

  // 其他绘图工具
  isDrawing.value = true;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 保存当前状态到历史记录
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  drawHistory.value.push(imageData);

  // 记录绘图起点
  (canvas as any).drawStartX = x;
  (canvas as any).drawStartY = y;
};

// 鼠标移动事件 - 调整选择区域或绘制
const handleMouseMove = (e: MouseEvent) => {
  if (!isActive.value) return;

  // 调整选择区域
  if (isSelecting.value && !isDrawing.value && currentTool.value !== 'text') {
    const currentX = e.clientX;
    const currentY = e.clientY;

    // 计算裁剪区域
    clipLeft.value = Math.min(startX.value, currentX);
    clipTop.value = Math.min(startY.value, currentY);
    clipRight.value = window.innerWidth - Math.max(startX.value, currentX);
    clipBottom.value = window.innerHeight - Math.max(startY.value, currentY);
    clipWidth.value = Math.abs(currentX - startX.value);
    clipHeight.value = Math.abs(currentY - startY.value);
  }

  // 绘制操作
  if (isDrawing.value && drawCanvas.value) {
    const canvas = drawCanvas.value;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 清除当前绘制（使用历史记录的最后状态）
    const lastState = drawHistory.value[drawHistory.value.length - 1];
    if (lastState) {
      ctx.putImageData(lastState, 0, 0);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // 计算相对位置
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const startX = (canvas as any).drawStartX;
    const startY = (canvas as any).drawStartY;

    // 设置绘图样式
    ctx.strokeStyle = '#ff0000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';

    // 根据当前工具绘制
    switch (currentTool.value) {
      case 'arrow':
        drawArrow(ctx, startX, startY, x, y);
        break;
        
      case 'rectangle':
        ctx.strokeRect(
          Math.min(startX, x),
          Math.min(startY, y),
          Math.abs(x - startX),
          Math.abs(y - startY)
        );
        break;
        
      case 'circle':
        const radius = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2));
        ctx.beginPath();
        ctx.arc(startX, startY, radius, 0, Math.PI * 2);
        ctx.stroke();
        break;
    }
  }
};

// 绘制箭头
const drawArrow = (ctx: CanvasRenderingContext2D, startX: number, startY: number, endX: number, endY: number) => {
  // 绘制箭头线
  ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.lineTo(endX, endY);
  ctx.stroke();
  
  // 绘制箭头头部
  const angle = Math.atan2(endY - startY, endX - startX);
  const arrowSize = 10;
  ctx.beginPath();
  ctx.moveTo(endX, endY);
  ctx.lineTo(
    endX - arrowSize * Math.cos(angle - Math.PI / 6),
    endY - arrowSize * Math.sin(angle - Math.PI / 6)
  );
  ctx.lineTo(
    endX - arrowSize * Math.cos(angle + Math.PI / 6),
    endY - arrowSize * Math.sin(angle + Math.PI / 6)
  );
  ctx.closePath();
  ctx.fillStyle = '#ff0000';
  ctx.fill();
};

// 鼠标释放事件 - 结束选择或绘制
const handleMouseUp = () => {
  // 结束绘制状态
  isDrawing.value = false;
  
  // 如果是初次选择区域且区域有效（宽度和高度大于0），则完成区域选择
  if (isSelecting.value && clipWidth.value > 10 && clipHeight.value > 10 && !isSelectionCompleted.value) {
    // 标记区域选择已完成
    isSelectionCompleted.value = true;
    console.log('区域选择完成', { clipLeft: clipLeft.value, clipTop: clipTop.value, clipWidth: clipWidth.value, clipHeight: clipHeight.value });
    
    // 显示短暂提示
    const tooltip = document.createElement('div');
    tooltip.textContent = '区域选择完成，可使用工具栏进行标注';
    tooltip.style.position = 'fixed';
    tooltip.style.top = '20px';
    tooltip.style.left = '50%';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.padding = '10px 20px';
    tooltip.style.backgroundColor = '#4CAF50';
    tooltip.style.color = 'white';
    tooltip.style.borderRadius = '4px';
    tooltip.style.zIndex = '10000';
    document.body.appendChild(tooltip);
    
    setTimeout(() => {
      tooltip.remove();
    }, 2000);
  }
};

// 设置当前工具
const setTool = (tool: 'arrow' | 'rectangle' | 'circle' | 'text') => {
  currentTool.value = tool;
  isTextEditing.value = false;
};

// 完成文字编辑
const finishTextEditing = () => {
  if (!textContent.value || !drawCanvas.value) {
    isTextEditing.value = false;
    return;
  }

  const canvas = drawCanvas.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 保存当前状态到历史记录
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  drawHistory.value.push(imageData);

  // 计算文字在画布中的位置
  const rect = canvas.getBoundingClientRect();
  const x = textPosition.value.x - rect.left;
  const y = textPosition.value.y - rect.top;

  // 绘制文字
  ctx.font = 'bold 16px sans-serif';
  ctx.fillStyle = '#ff0000';
  ctx.fillText(textContent.value, x, y);

  // 关闭文字编辑
  isTextEditing.value = false;
};

// 撤销操作
const undo = () => {
  if (drawHistory.value.length === 0 || !drawCanvas.value) return;

  const canvas = drawCanvas.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 移除最后一步并恢复到上一步
  drawHistory.value.pop();
  const lastState = drawHistory.value[drawHistory.value.length - 1];
  
  if (lastState) {
    ctx.putImageData(lastState, 0, 0);
  } else {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
};

// 保存截图
const saveScreenshot = async () => {
  if (!isSelectionCompleted.value && !isSelecting.value) return;

  try {
    // 创建一个新的canvas用于合成最终截图
    const canvas = document.createElement('canvas');
    canvas.width = clipWidth.value;
    canvas.height = clipHeight.value;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('无法获取Canvas上下文');

    // 捕获选中区域的内容
    const stream = await navigator.mediaDevices.getDisplayMedia({
      // preferCurrentTab: true,
      video: true
    });

    const video = document.createElement('video');
    video.srcObject = stream;
    await video.play();

    // 等待一帧确保视频已经开始播放并有画面
    await new Promise(resolve => requestAnimationFrame(resolve));
    
    // 创建一个临时canvas来捕获整个屏幕
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    if (!tempCtx) throw new Error('无法获取临时Canvas上下文');
    
    // 先将整个视频帧绘制到临时canvas
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    
    // 计算正确的裁剪比例 - 解决截图区域和选中区域不一致的问题
    const scaleX = tempCanvas.width / window.innerWidth;
    const scaleY = tempCanvas.height / window.innerHeight;
    
    // 使用缩放后的坐标绘制到最终canvas
    ctx.drawImage(
      tempCanvas,
      clipLeft.value * scaleX,  // 缩放后的X坐标
      clipTop.value * scaleY,   // 缩放后的Y坐标
      clipWidth.value * scaleX, // 缩放后的宽度
      clipHeight.value * scaleY,// 缩放后的高度
      0,
      0,
      clipWidth.value,          // 保持原始显示宽度
      clipHeight.value          // 保持原始显示高度
    );

    // 绘制标注内容
    if (drawCanvas.value) {
      ctx.drawImage(drawCanvas.value, 0, 0);
    }

    // 停止媒体流
    stream.getTracks().forEach(track => track.stop());

    // 转换为图片URL
    const dataUrl = canvas.toDataURL('image/png');

    // 关闭截图模式
    cancelScreenshot();

    // 自动下载图片
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = `screenshot-${new Date().getTime()}.png`;
    link.click();
  } catch (err) {
    console.error('保存截图失败:', err);
    alert('保存截图失败，请重试');
  }
};

onMounted(() => {
  // 初始化组件
});
</script>

<style scoped>
.screenshot-container {
  position: relative;
  display: inline-block;
}

.screenshot-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #4CAF50;
  color: #000;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.screenshot-btn:hover {
  background-color: #45a049;
}

.screenshot-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  outline: none;
}

.selected-area-highlight {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  border: 1px dashed #fff;
}

.selection-border {
  position: absolute;
  border: 2px solid #4CAF50;
  background-color: transparent;
}

.control-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: white;
  border: 2px solid #4CAF50;
  border-radius: 50%;
}

.control-point[data-control="topleft"] {
  top: -5px;
  left: -5px;
  cursor: nwse-resize;
}

.control-point[data-control="topright"] {
  top: -5px;
  right: -5px;
  cursor: nesw-resize;
}

.control-point[data-control="bottomleft"] {
  bottom: -5px;
  left: -5px;
  cursor: nesw-resize;
}

.control-point[data-control="bottomright"] {
  bottom: -5px;
  right: -5px;
  cursor: nwse-resize;
}

.drawing-canvas {
  position: absolute;
  pointer-events: none;
}

.toolbar {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.toolbar button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  color: #000 !important;
  transition: background-color 0.2s;
}

/* 确保Font Awesome图标也是黑色 */
.toolbar button i {
  color: #000 !important;
}

/* 针对Element UI按钮的样式覆盖 */
.toolbar .el-button {
  color: #000 !important;
}

.toolbar .el-button i {
  color: #000 !important;
}

.toolbar button:hover {
  background-color: #f5f5f5;
}

.toolbar button.active {
  color: #000 !important;
}

/* Element UI按钮活动状态 */
.toolbar .el-button.is-active {
  color: #000 !important;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background-color: #ddd;
}

/* 覆盖保存按钮的特殊样式 */
.toolbar button.save-btn {
  color: #4CAF50 !important; /* 保存按钮保持绿色 */
}

.text-input {
  position: absolute;
  border: none;
  background-color: transparent;
  color: white;
  font: bold 16px sans-serif;
  outline: none;
  padding: 2px;
  min-width: 100px;
}
</style>