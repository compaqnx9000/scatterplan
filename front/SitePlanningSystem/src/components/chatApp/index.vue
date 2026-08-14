<template>
  <div class="app-container" v-if="showChat">
    <!-- 聊天内容区域 -->
    <div class="app-container-header">
      <el-icon @mouseenter="historyShow"><Operation /></el-icon>
      <el-icon class="close_icon" @click="closeChat">
        <Close />
      </el-icon>
      <el-icon class="el-icon-notebook-2"></el-icon>
    </div>
    <div class="tooltip-container" v-if="isShowHistory" @mouseenter="historyShow" @mouseleave="historyLeave">
      <div class="tooltip-container-header">
        <div>历史记录</div>
        <el-icon class="close_icon"><Clock /></el-icon>
      </div>
      <el-divider/>
      <div v-for="item in aiHistory" @click="historyItemClick(item)" class="aiHistoryList">
        <el-icon><ChatDotRound /></el-icon>
        <div class="aiHistoryContent">{{item.title}}</div>
        <div>{{formatDate(item.createTime)}}</div>
      </div>

    </div>
    <div class="chat-container" ref="chatContainer">
      <div class="message-list" ref="messagesWrapper">
        <!-- 系统消息 -->
        <div class="system-message">
          <div class="content">欢迎使用智能聊天助手，我可以回答您的问题并提供帮助。</div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(message, index) in messages" :key="index"
          :class="['message-item', message.role === 'user' ? 'user-message' : 'assistant-message']">
          <div class="message-content">
            <el-icon class="icon" v-if="message.role === 'assistant'" @click="downloadMessage(renderMessageContent(message.content))"><Download /></el-icon>
            <div class="bubble" v-html="renderMessageContent(message.content)"></div>
<!--            <div class="bubble" v-html="message.content"></div>-->
            <div class="timestamp">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- 正在输入提示 -->
        <div v-show="isLoading" class="assistant-message">
          <div class="message-content">
            <div class="bubble typing-indicator">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input v-model="userInput" type="textarea" :rows="2" placeholder="请输入问题..." @keyup.enter.native="sendMessage"
        ref="inputRef"></el-input>
      <div class="send-area">
        <el-button :disabled="isLoading || !userInput.trim()" type="primary" @click="sendMessage">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, watch, defineEmits,onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
//获取招商楼宇的接口
import {getMerchantsBuilding, getAiHistory, addHistory} from "@/request/attractInvestment";
let currentInstance = getCurrentInstance()
let $bus = currentInstance?.appContext.config.globalProperties.$bus
let loginData = localStorage.getItem('loginData')
const emits = defineEmits(['update:showChat']);
// 定义消息类型
interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  file?: {
    name: string
    url: string
    size: number
  }
  isStreaming?: boolean // 标记是否正在流式输出
}


const props = defineProps({
  showChat: {
    type: Boolean,
    default: false
  }
});
// 状态管理
const chatContainer = ref<HTMLElement | null>(null)
const messagesWrapper = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)
const uploadRef = ref<any>(null)
const messages = ref<Message[]>([])
const userInput = ref('')
const isLoading = ref(false)
const currentFile = ref<File | null>(null)
const uploadUrl = ref('https://example.com/upload')
const userAvatar = ref('https://picsum.photos/200/200?random=1')
const assistantAvatar = ref('https://picsum.photos/200/200?random=2')
const abortController = ref<AbortController | null>(null)
const merchantsBuildingData = ref(null)// 楼宇信息
const aiHistory = ref<Array<any>>([]);//ai会话信息
const isShowHistory = ref(false);
// 格式化日期时间
const formatTime = (dateStr: Date) => {
  const date = new Date(dateStr);

  if (isNaN(date.getTime())) {
    // 解析失败时的处理（旧浏览器可能出现）
    console.error('日期解析失败');
  } else {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const result = `${hours}:${minutes}`;
    console.log(result); // 输出: "13:57"
  }
}
function formatDate(timestamp:any) {
  // 假设 timestamp 是时间戳或日期字符串
  const date = new Date(timestamp);
  const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从 0 开始，需要 +1
  const day = String(date.getDate()).padStart(2, '0');
  const result = `${month}-${day}`;
  return result;
}
// 格式化消息内容
// const renderMessageContent = (content: string) => {
//   // 处理代码块
//   let formattedContent = content.replace(/```([\s\S]*?)```/g, (match, code) => {
//     return `<pre class="code-block"><code>${code}</code></pre>`
//   })
//   // 处理换行
//   formattedContent = formattedContent.replace(/\n/g, '<br>')
//   return formattedContent
// }


const renderMessageContent = (content:any) => {
  // 基础HTML特殊字符转义
  let formattedContent = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')



  // 处理标题（# H1 ~ ###### H6）
  formattedContent = formattedContent.replace(/#{1,6} (.*$)/gm, (match:any, title:any) => {
    const level = match.split('#').length - 1
    // return `<h${level} class="markdown-heading">${title}</h${level}>`
    return `<h5 class="markdown-heading">${title}</h5>`
  })

  // 处理无序列表（- 项目）
  formattedContent = formattedContent.replace(/^- (.*$)/gm, '<li>$1</li>')
  formattedContent = formattedContent.replace(/(<li>.*?<\/li>)+/gms, '<ul class="markdown-ul">$&</ul>')

  // 处理有序列表（1. 项目）
  formattedContent = formattedContent.replace(/^(\d+)\. (.*$)/gm, '<li>$2</li>')
  formattedContent = formattedContent.replace(/(<li>.*?<\/li>)+/gms, '<ol class="markdown-ol">$&</ol>')

  // 处理加粗（**文本**）和斜体（*文本*）
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>')

  // 处理链接（[文本](链接)）
  formattedContent = formattedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="markdown-link">$1</a>')

  // 处理换行
  formattedContent = formattedContent.replace(/\n/g, '<br>')

  // 处理水平线（---）
  formattedContent = formattedContent.replace(/---/g, '<hr class="markdown-hr">')

  // 处理引用（> 内容）
  formattedContent = formattedContent.replace(/^> (.*$)/gm, '<blockquote class="markdown-blockquote">$1</blockquote>')

  return formattedContent
}
//历史记录
function historyShow() {
  getHistoryContent()
  isShowHistory.value = true;

}

function historyItemClick(item:any) {
  messages.value = JSON.parse(item.result);
}
function historyLeave() {
  isShowHistory.value = false;
}
function closeChat() {
  emits('update:showChat', false);
}
// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value && messagesWrapper.value) {
      chatContainer.value.scrollTop = messagesWrapper.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content && !currentFile.value) return

  // 添加用户消息
  const userMessage: Message = {
    role: 'user',
    content,
    timestamp: new Date()
  }

  if (currentFile.value) {
    userMessage.file = {
      name: currentFile.value.name,
      url: URL.createObjectURL(currentFile.value),
      size: currentFile.value.size
    }
  }

  messages.value.push(userMessage)
  userInput.value = ''
  currentFile.value = null
  scrollToBottom()
  isLoading.value = true
  abortController.value = new AbortController()

  try {
    // 准备请求数据
    const requestData = {
      model: 'deepseek-r1-250528',
      messages: [
        { role: 'system', content: '参考这个数据:' + JSON.stringify(merchantsBuildingData.value) },
        ...messages.value.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      ],
      stream: true // 启用流式输出
    }

    // 使用fetch处理流式响应
    const response = await fetch('/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
      signal: abortController.value.signal
    })

    if (!response.ok) throw new Error(`HTTP错误: ${response.status}`)

    // 添加流式响应的助手消息
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    }
    messages.value.push(assistantMessage)
    scrollToBottom()

    // 处理流式数据
    await handleStreamResponse(response, assistantMessage)
  } catch (error: any) {
    if (error.name === 'AbortError') {
      ElMessage.warning('请求已取消')
    } else {
      console.error('发送消息失败', error)
      ElMessage.error('发送消息失败，请重试')
      messages.value.push({
        role: 'assistant',
        content: '抱歉，发送消息时出现错误，请重试。',
        timestamp: new Date()
      })
    }
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 处理流式响应核心逻辑
const handleStreamResponse = async (response: Response, message: Message) => {
  if (!response.body) throw new Error('响应没有数据流')

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let accumulatedContent = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        message.isStreaming = false
        break
      }

      // 解码数据块
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n').filter(line => line.trim() !== '')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6).trim()
          if (data === '[DONE]') {
            message.isStreaming = false;

            //处理完数据后直接添加历史记录到后台
            await addHistory({
              title:messages.value[0].content,
              result:JSON.stringify(messages.value)
            })
            continue
          }
          try {
            const parsedData = JSON.parse(data)
            if (parsedData.choices && parsedData.choices[0].delta?.content) {
              const contentChunk = parsedData.choices[0].delta.content
              accumulatedContent += contentChunk
              // 核心：更新内容并触发视图更新
              // message.content = accumulatedContent
              console.log(accumulatedContent);
              console.log(messages.value);
              messages.value[messages.value.length - 1].content = accumulatedContent;
              // message.content += contentChunk
              // 延迟滚动，避免阻塞内容渲染
              nextTick(() => {
                scrollToBottom()
              })
            }
          } catch (err) {
            console.error('解析流数据失败', err)
            message.content += '[数据解析错误]'
          }
        }
      }
    }
  } catch (err) {
    console.error('流式响应处理失败', err)
    message.content += '\n\n[响应中断，请重试]'
    message.isStreaming = false
  } finally {
    reader.releaseLock()
  }
}

// 取消请求
const cancelRequest = () => {
  if (abortController.value) {
    abortController.value.abort('用户取消请求')
    abortController.value = null
  }
}

// 文件上传处理
const beforeUpload = (file: File) => {
  currentFile.value = file
  uploadRef.value?.submit()
  return false
}

const handleUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
}

async function initData() {
  let res: any = await getMerchantsBuilding({
    pageNum: 1,
    pageSize:10000
  })
  merchantsBuildingData.value = res.rows;
  getHistoryContent()
}
async function getHistoryContent() {
  if (loginData) {
    let historyRes: any = await getAiHistory({
      pageNum: 1,
      pageSize: 10000,
      createBy: JSON.parse(loginData).userName
    })
    console.log(historyRes);
    aiHistory.value = historyRes.rows;
  }
}
initData();

const getSendMessage = (e:String) => {
    userInput.value = e.trim()
    sendMessage()
}

//完善Html格式
const convertToWordDocument = (content: string) => {
  // 添加 Word 兼容的 HTML 结构和样式
  return `<!DOCTYPE html>
              <html xmlns:o="urn:schemas-microsoft-com:office:office"
                    xmlns:w="urn:schemas-microsoft-com:office:word">
              <head>
                <meta charset="UTF-8">
                <meta name="ProgId" content="Word.Document">
                <meta name="Generator" content="Microsoft Word">
                <title>Exported Document</title>
                <style>
                  body {
                    font-family: "Microsoft YaHei", SimSun, sans-serif;
                    margin: 20px;
                    line-height: 1.5;
                  }
                  table {
                    border-collapse: collapse;
                    width: 100%;
                  }
                  table, th, td {
                    border: 1px solid #ddd;
                  }
                  th, td {
                    padding: 8px;
                    text-align: left;
                  }
                  img {
                    max-width: 100%;
                    height: auto;
                  }
                </style>
              </head>
              <body>
                ${content}
              </body>
              </html>`;
};

const downloadMessage = (val:string) => {
  try {
    if (!val) {
      ElMessage({
        message: '暂无内容，请稍后！',
        type: 'warning',
      })
      console.error("No DOM element found");
      return;
    }
    // 转换内容为 Word 兼容的 HTML
    const convertedContent = convertToWordDocument(val);

    // 创建 Blob 并下载
    const blob = new Blob([convertedContent], {
      type: "application/msword",
    });

    const now = new Date();
    const timestamp = now.getTime();
    const fileName = `${timestamp}.doc`;

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();

    // 清理
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
  } catch (error) {
    console.error("导出 Word 失败:", error);
  }
  
}

// 组件挂载后滚动到底部
onMounted(() => {
  scrollToBottom();
  //获取基础数据
  $bus.on("sendChatMessage",getSendMessage)
})
onUnmounted(() => {
  $bus.off('sendChatMessage', getSendMessage);
});
</script>



<style scoped lang="scss">
.app-container {
  width: 900px;
  height: 800px;
  display: flex;
  flex-direction: column;
  border: 1px solid #1c6f8d;
  box-shadow: 0px 0px 2px 0px #468fce;
  background: rgba(11, 48, 61, 0.8);
  padding: 5px;
  backdrop-filter: blur(3px);
}

.app-container-header {
  display: flex;
  height: 15px;
  padding: 5px;
  border-bottom: 1px solid $color-primary;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  max-width: 80%;
}



.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  margin: 0 4px;
  position: relative;
  .icon {
    position: absolute;
    right: -20px;
    top: 5px;
    z-index: 999999;
    cursor: pointer;
    color: #303133;
    * {
      cursor: pointer;
    }
  }
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  font-size: 10px;
  line-height: 1.5;
  width: 100%;
}

.user-message .bubble {
  background-color: rgba(64, 158, 255, 0.92);
  color: white;
}

.assistant-message .bubble {
  background-color: white;
  color: #303133;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.timestamp {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.system-message {
  text-align: center;
  margin: 16px 0;
}

.system-message .content {
  display: inline-block;
  border-radius: 12px;
  font-size: 14px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  width: 30px;
  height: 15px;
  align-items: center;
  justify-content: center;
}

.dot {
  width: 3px;
  height: 3px;
  background-color: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}


.code-block {
  border-radius: 4px;
  padding: 8px 12px;
  margin: 8px 0;
  overflow-x: auto;
  font-family: Consolas, Monaco, 'Andale Mono', monospace;
  font-size: 13px;
}

.input-area {
  padding: 16px;
}



.send-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.el-textarea{
  border: 2px solid #1c6f8d!important;
}
.close_icon{
  margin-left: auto;
  cursor: pointer;
}

//历史记录框
.tooltip-container{
  position: absolute;
  left: 10px;
  top: 50px;
  border-radius: 10px;
  height: 75%;
  width: 200px;
  background: rgba(11, 48, 61, 0.5);
  padding: 5px;
  z-index: 999999;
  &-header{
    display: flex;
  }
  .aiHistoryList{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
}
.aiHistoryContent{
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100px;
}


.code-block {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
}

ul, ol {
  margin: 10px 0;
  padding-left: 20px;
}

li {
  margin: 5px 0;
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 15px;
  margin-bottom: 10px;
}

blockquote {
  border-left: 4px solid #ddd;
  padding-left: 10px;
  margin-left: 0;
  color: #666;
}
</style>
