/**
 * Prefer installed CJK fonts first. Do not put "Noto Sans SC" first:
 * a latin-only web subset will paint tofu and canvas will not fall back.
 */
export const ECHARTS_CJK_FONT =
  '"Microsoft YaHei", "微软雅黑", "PingFang SC", "Hiragino Sans GB", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "Source Han Sans SC", "Noto Sans SC", sans-serif';

export const echartsTextStyle = {
  fontFamily: ECHARTS_CJK_FONT,
};

const CJK_PROBE = "高程剖面发射点接收点障碍物散射体距离";

export const waitEchartsFonts = async () => {
  if (typeof document === "undefined") return;
  const probe = document.createElement("span");
  probe.textContent = CJK_PROBE;
  probe.style.cssText = `position:absolute;left:-9999px;top:-9999px;font:12px ${ECHARTS_CJK_FONT}`;
  document.body.appendChild(probe);
  try {
    if (document.fonts) {
      await Promise.allSettled([
        document.fonts.load(`12px "Microsoft YaHei"`, CJK_PROBE),
        document.fonts.load(`12px "微软雅黑"`, CJK_PROBE),
        document.fonts.load(`12px "Noto Sans SC"`, CJK_PROBE),
        document.fonts.ready,
      ]);
    }
    void probe.offsetWidth;
  } catch {
    /* keep going with the fallback stack */
  }
  probe.remove();
};
