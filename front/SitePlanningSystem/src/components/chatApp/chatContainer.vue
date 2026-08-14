<template>
  <div class="schemePanel" v-if="modelValue">
    <div class="close" @click="closePanel">
      <el-icon>
        <CloseBold />
      </el-icon>
    </div>
    <div class="main">
      <div class="download" @click="btnFlag && exportToWord()">
        <el-icon><Download /></el-icon>
      </div>
      <div
        class="download-main"
        ref="messagesDom"
        v-html="renderMessageContent(messages)"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, onMounted, PropType } from "vue";
interface InfoType {
  docxName: string;
  instruction: string;
}
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  info: {
    type: Object as PropType<InfoType>,
    default: () => ({
      docxName: "文档",
      instruction: "",
    }),
  },
});

const emits = defineEmits(["update:modelValue"]);

const closePanel = () => {
  emits("update:modelValue", false);
};

const messagesDom = ref();

// 定义消息类型
interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  file?: {
    name: string;
    url: string;
    size: number;
  };
  isStreaming?: boolean; // 标记是否正在流式输出
}
//
const getGPt = async (content = "你是什么ai") => {
  // 添加用户消息
  let acl = new AbortController();
  const userMessage: Message = {
    role: "user",
    content,
    timestamp: new Date(),
  };
  try {
    const requestData = {
      model: "deepseek-r1-250528",
      messages: [userMessage],
      stream: true, // 启用流式输出
    };
    const response = await fetch("/api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
      signal: acl.signal,
    });
    if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);
    const assistantMessage: Message = {
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isStreaming: true,
    };
    await handleStreamResponse(response, assistantMessage);
  } catch (error) {
    console.log("发生了错误:" + error);
  }
};

const renderMessageContent = (content: any) => {
  // 基础HTML特殊字符转义

  let formattedContent = content
    ?.replace(/&/g, "&amp;")
    ?.replace(/</g, "&lt;")
    ?.replace(/>/g, "&gt;");

  // 处理标题（# H1 ~ ###### H6）
  formattedContent = formattedContent?.replace(
    /#{1,6} (.*$)/gm,
    (match: any, title: any) => {
      const level = match.split("#").length - 1;
      // return `<h${level} class="markdown-heading">${title}</h${level}>`
      return `<h5 class="markdown-heading">${title}</h5>`;
    }
  );

  // 处理无序列表（- 项目）
  formattedContent = formattedContent?.replace(/^- (.*$)/gm, "<li>$1</li>");
  formattedContent = formattedContent?.replace(
    /(<li>.*?<\/li>)+/gms,
    '<ul class="markdown-ul">$&</ul>'
  );

  // 处理有序列表（1. 项目）
  formattedContent = formattedContent?.replace(
    /^(\d+)\. (.*$)/gm,
    "<li>$2</li>"
  );
  formattedContent = formattedContent?.replace(
    /(<li>.*?<\/li>)+/gms,
    '<ol class="markdown-ol">$&</ol>'
  );

  // 处理加粗（**文本**）和斜体（*文本*）
  formattedContent = formattedContent?.replace(
    /\*\*(.*?)\*\*/g,
    "<strong>$1</strong>"
  );
  formattedContent = formattedContent?.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // 处理链接（[文本](链接)）
  formattedContent = formattedContent?.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" class="markdown-link">$1</a>'
  );

  // 处理换行
  formattedContent = formattedContent?.replace(/\n/g, "<br>");

  // 处理水平线（---）
  formattedContent = formattedContent?.replace(
    /---/g,
    '<hr class="markdown-hr">'
  );

  // 处理引用（> 内容）
  formattedContent = formattedContent?.replace(
    /^> (.*$)/gm,
    '<blockquote class="markdown-blockquote">$1</blockquote>'
  );

  return formattedContent;
};

const btnFlag = ref(false)

const messages = ref("正在生成中......");

// 处理流式响应核心逻辑
const handleStreamResponse = async (response: Response, message: Message) => {
  if (!response.body) throw new Error("响应没有数据流");

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let accumulatedContent = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        message.isStreaming = false;
        btnFlag.value = true
        break;
      }
      // 解码数据块
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n").filter((line) => line.trim() !== "");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.substring(6).trim();
          if (data === "[DONE]") {
            message.isStreaming = false;
            btnFlag.value = true
            messages.value += '\n\n\n注：内容有ai生成，仅供参考。'
            continue;
          }
          try {
            const parsedData = JSON.parse(data);
            if (parsedData.choices && parsedData.choices[0].delta?.content) {
              const contentChunk = parsedData.choices[0].delta.content;
              accumulatedContent += contentChunk;
              // 核心：更新内容并触发视图更新
              // message.content = accumulatedContent
              messages.value = accumulatedContent;
              // message.content += contentChunk
              // 延迟滚动，避免阻塞内容渲染
            }
          } catch (err) {
            console.error("解析流数据失败", err);
            message.content += "[数据解析错误]";
          }
        }
      }
    }
  } catch (err) {
    console.error("流式响应处理失败", err);
  } finally {
  }
};

const exportToWord = () => {
  try {
    const dom = messagesDom.value as HTMLElement;
    if (!dom) {
      console.error("No DOM element found");
      return;
    }

    // 克隆 DOM 以避免修改原始内容
    const content = dom.cloneNode(true) as HTMLElement;

    // 预处理内容 - 移除不需要的元素或添加样式
    const styleElements = content.querySelectorAll(
      'style, link[rel="stylesheet"]'
    );
    styleElements.forEach((el) => el.remove());

    // 转换内容为 Word 兼容的 HTML
    const convertedContent = convertToWordDocument(content.innerHTML);

    // 创建 Blob 并下载
    const blob = new Blob([convertedContent], {
      type: "application/msword",
    });

    const now = new Date();
    const timestamp = now.getTime();
    const fileName = `${props.info.docxName || "未命名"}_${timestamp}.doc`;

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
};
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

onMounted(() => {
  if (props.modelValue && props.info?.instruction) {
    nextTick(() => {
      let target = props.info?.instruction;
      getGPt(target);
    });
  }
});
</script>

<style lang="scss" scoped>
.schemePanel {
  position: fixed;
  width: 800px;
  left: 50%;
  transform: translate(-50%, -50%);
  top: 50%;
  bottom: 40px;
  z-index: 9999;
  height: 900px;
  border: 1px solid #1a3642;
  background: linear-gradient(180deg, rgba(7, 43, 59) 0%, rgba(6, 27, 35) 100%);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  pointer-events: all;
  .download {
    display: flex;
    justify-content: flex-end;
    margin: 10px;
    * {
      cursor: pointer;
    }
  }

  .close {
    position: absolute;
    width: 20px;
    height: 20px;
    right: 0;
    top: 0; // 添加 top:0 确保按钮在可见区域
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.3);
    z-index: 10; // 确保按钮在最上层
    * {
      cursor: pointer;
    }
  }
  .main {
    padding: 20px;
    flex: 1;
    height: 0;
    display: flex;
    flex-direction: column;
    .download-main {
      overflow-y: auto;
      flex: 1;
    }
  }
}
</style>
