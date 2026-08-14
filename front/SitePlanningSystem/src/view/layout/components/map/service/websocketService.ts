import { onUnmounted } from 'vue';

// WebSocket连接状态类型
type WebSocketStatus = 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED' | 'ERROR';

// 消息类型定义
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: number;
}

// 配置选项类型
interface WebSocketOptions {
  url: string;
  heartbeatInterval?: number; // 心跳间隔(ms)，默认30000
  reconnectInterval?: number; // 重连间隔(ms)，默认3000
  maxReconnectAttempts?: number; // 最大重连次数，默认无限
  pingMessage?: string | object; // 心跳消息，默认'ping'
  pongMessage?: string; // 心跳响应验证，默认'pong'
}

export class WebSocketService {
  private ws?: WebSocket;
  private status: WebSocketStatus = 'CLOSED';
  private heartbeatTimer?: NodeJS.Timeout;
  private reconnectTimer?: NodeJS.Timeout;
  private reconnectAttempts = 0;
  private messageQueue: WebSocketMessage[] = []; // 消息队列
  private isManualClose = false; // 是否手动关闭

  // 配置选项
  private options: WebSocketOptions = {
    url: '',
    heartbeatInterval: 30000,
    reconnectInterval: 3000,
    maxReconnectAttempts: Infinity,
    pingMessage: 'ping',
    pongMessage: 'pong'
  };

  // 事件回调
  private onOpenCallback?: () => void;
  private onMessageCallback?: (message: WebSocketMessage) => void;
  private onCloseCallback?: (code: number, reason: string) => void;
  private onErrorCallback?: (error: Event) => void;

  constructor(options: WebSocketOptions) {
    this.options = { ...this.options, ...options };
    this.connect();
  }

  // 建立连接
  private connect() {
    if (this.status === 'CONNECTING' || this.status === 'OPEN') return;

    this.status = 'CONNECTING';
    
    try {
    const token = localStorage.getItem('userToken');
    // 替换 this.options.url 的 token 参数 为新的 token,没有oldToken，直接删除token= 后面的，然后加上新token就可以
    this.options.url = this.options.url.split('=')[0] + '=' + token
    this.ws = new WebSocket(this.options.url);
      
      // 连接打开
      this.ws.onopen = () => {
        this.status = 'OPEN';
        this.reconnectAttempts = 0; // 重置重连次数
        this.startHeartbeat();
        this.flushMessageQueue(); // 发送队列中的消息
        
        if (this.onOpenCallback) {
          this.onOpenCallback();
        }
      };

      // 接收消息
      this.ws.onmessage = (event) => {
        try {
          // 处理心跳响应
          if (event.data === this.options.pongMessage) {
            return;
          }
          
          // 解析消息
          const message: WebSocketMessage = typeof event.data === 'string' 
            ? JSON.parse(event.data) 
            : event.data;
            
          if (this.onMessageCallback) {
            this.onMessageCallback(message);
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };

      // 连接关闭
      this.ws.onclose = (event) => {
        this.status = 'CLOSED';
        this.stopHeartbeat();
        
        if (this.onCloseCallback) {
          this.onCloseCallback(event.code, event.reason);
        }
        
        // 自动重连（非手动关闭且未达到最大重连次数）
        if (!this.isManualClose && this.reconnectAttempts < this.options.maxReconnectAttempts!) {
          this.reconnect();
        }
      };

      // 错误处理
      this.ws.onerror = (error) => {
        this.status = 'ERROR';
        
        if (this.onErrorCallback) {
          this.onErrorCallback(error);
        }
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.status = 'ERROR';
      this.reconnect();
    }
  }

  // 重连机制
  private reconnect() {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts!) {
      console.warn(`Reached maximum reconnection attempts (${this.options.maxReconnectAttempts})`);
      return;
    }

    this.reconnectAttempts++;
    this.status = 'CLOSED';
    
    // 清除现有重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    // 指数退避策略：重连间隔逐渐增加，最多5分钟
    const delay = Math.min(
      this.options.reconnectInterval! * Math.pow(2, this.reconnectAttempts - 1),
      300000 // 5分钟
    );
    
    console.log(`WebSocket reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  // 启动心跳检测
  private startHeartbeat() {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.status === 'OPEN' && this.ws) {
        try {
          const pingMsg = {
            message: 'ping',
          }
            
          this.ws.send(JSON.stringify(pingMsg));
        } catch (error) {
          console.error('WebSocket heartbeat error:', error);
          this.status = 'ERROR';
          this.reconnect();
        }
      }
    }, this.options.heartbeatInterval);
  }

  // 停止心跳检测
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  // 发送消息到队列
  private enqueueMessage(message: WebSocketMessage) {
    this.messageQueue.push(message);
  }

  // 发送队列中的所有消息
  private flushMessageQueue() {
    if (this.status !== 'OPEN' || !this.ws || this.messageQueue.length === 0) return;
    
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  // 发送消息
  public send(message: WebSocketMessage) {
    // 如果连接未打开，加入队列等待发送
    if (this.status !== 'OPEN' || !this.ws) {
      this.enqueueMessage(message);
      return false;
    }

    try {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: Date.now()
      }));
      return true;
    } catch (error) {
      console.error('WebSocket send error:', error);
      this.enqueueMessage(message);
      return false;
    }
  }

  // 手动关闭连接
  public close(code: number = 1000, reason: string = 'Manual close') {
    this.isManualClose = true;
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
    
    if (this.ws) {
      this.ws.close(code, reason);
    }
    
    this.status = 'CLOSED';
    this.messageQueue = [];
  }

  // 获取当前连接状态
  public getStatus(): WebSocketStatus {
    return this.status;
  }

  // 事件监听
  public onOpen(callback: () => void) {
    this.onOpenCallback = callback;
  }

  public onMessage(callback: (message: WebSocketMessage) => void) {
    this.onMessageCallback = callback;
  }

  public onClose(callback: (code: number, reason: string) => void) {
    this.onCloseCallback = callback;
  }

  public onError(callback: (error: Event) => void) {
    this.onErrorCallback = callback;
  }
}

// 创建WebSocket实例的工具函数
export function useWebSocket(options: WebSocketOptions) {
  const wsService = new WebSocketService(options);
  
  // 组件卸载时关闭连接
  onUnmounted(() => {
    wsService.close();
  });
  
  return wsService;
}
