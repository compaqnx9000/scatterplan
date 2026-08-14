import path from "path";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { mars3dPlugin } from "vite-plugin-mars3d";

// 用于自动按需导入
import AutoImport from "unplugin-auto-import/vite";

// import ElementPlus from 'unplugin-element-plus/vite'

// https://cn.vitejs.dev/config/  vite config 配置
export default defineConfig(({ mode }) => {
  return {
    build: {
      commonjsOptions: {
        include: /node_modules|packages/,
      },
    },
    plugins: [
      vue(),
      mars3dPlugin(),
      // or use unplugin-element-plus
      // ElementPlus({
      //   useSource: true,
      // }),
      AutoImport({
        // 自动导入 Vue 相关函数，如：ref, reactive, toRef 等
        imports: ["vue"],
        // 防止报错
        dts: path.resolve(path.resolve(__dirname, "src"), "auto-imports.d.ts"),
      }),
    ],
    resolve: {
      // 配置路径别名
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      hmr: {
        overlay: false, //屏蔽开发期间报错信息弹出大窗口展示
      },
      host: "0.0.0.0",
      open: true, //运行完是否打开浏览器
      port: 8086, //端口
      proxy: {
        //请求转发
        "/prod-api/": {
          //匹配前缀
          target: loadEnv(mode, process.cwd()).VITE_APP_BASE_url, //转发地址 - 环境变量
          changeOrigin: true, //是否允许跨域
          rewrite: (path) => path.replace(/^\/prod-api/, ""), // 本地环境需要过滤，线上环境不需要过滤
        },
        // 上图资源全部直接访问，不走转发
        '/geoserver': {     //匹配前缀
          // target: loadEnv(mode, process.cwd()).VITE_APP_BASE_url,   //转发地址 - 环境变量
          target: 'http://127.0.0.1:8080',   //转发地址 - 环境变量
          changeOrigin: true, //是否允许跨域
          // rewrite: (path) => path.replace(/^\/geoserver/, '') // 不可以省略rewrite
        },
        // '/rts3d': {     //匹配前缀
        //   // target: loadEnv(mode, process.cwd()).VITE_APP_BASE_url,   //转发地址 - 环境变量
        //   target: loadEnv(mode, process.cwd()).VITE_APP_QXSY_url,   //转发地址 - 环境变量
        //   changeOrigin: true, //是否允许跨域
        //   // rewrite: (path) => path.replace(/^\/geoserver/, '') // 不可以省略rewrite
        // },
        "/common/upload": {
          target: loadEnv(mode, process.cwd()).VITE_APP_BASE_url, //转发地址 - 环境变量
          changeOrigin: true, //是否允许跨域
        },
        "/api": {
          target: "https://ark.cn-beijing.volces.com",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, "/api/v3/chat/completions"),
          secure: false,
          headers: {
            Authorization: "Bearer 6a91f282-1831-4a8c-a3bd-4d2f78c2a46e",
          },
        },
        "/nominatim": {
          target: "https://nominatim.openstreetmap.org",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/nominatim/, ""),
          configure: (proxy) => {
            proxy.on("proxyReq", (proxyReq) => {
              proxyReq.setHeader(
                "User-Agent",
                "ScatterPlan/1.0 (scatter communication planning)"
              );
            });
          },
        },
        "/biyingMaps": {
          target: "http://cn.bing.com",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/biyingMaps/, "/maps"),
          configure: (proxy, options) => {
            // 解决请求403问题：invalid CORS request。非常重要的代码！！
            // proxy.on('proxyReq', function (proxyReq, req, res) {
            //   proxyReq.removeHeader('referer')  // 移除请求头
            //   proxyReq.removeHeader('origin') // 移除请求头
            //   proxyReq.removeHeader('X-Frame-Options') // 移除请求头
            //   // 添加请求头
            //   req.setHeader('X-Frame-Options', 'ALLOWALL')
            // })
          },
        },
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          //用于声明全局变量

          additionalData: `@use "./src/assets/style/publiStyle.scss" as *;`,
          // additionalData: '@import "./src/assets/style/publiStyle.scss";',
        },
      },
    },
  };
});
