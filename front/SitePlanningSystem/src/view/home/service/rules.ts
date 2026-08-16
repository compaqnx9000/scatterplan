const stripCoord = (value: string) =>
  String(value || "")
    .trim()
    .replace(/°/g, " ")
    .replace(/\u00A0/g, " ")
    .replace(/\s+/g, " ")
    .trim();

/** Accept plain numbers or display forms like `11.2345° E` / `45.8321° N`. */
const parseLongitude = (value: string | number) => {
  if (value === "" || value === null || value === undefined) return NaN;
  if (typeof value === "number") return value;
  const text = stripCoord(value);
  const match = text.match(/^([+-]?\d+(?:\.\d+)?)\s*([EWew])?$/);
  if (!match) {
    const num = Number(text);
    return num;
  }
  let num = Number(match[1]);
  if (match[2] && match[2].toUpperCase() === "W") num = -Math.abs(num);
  if (match[2] && match[2].toUpperCase() === "E") num = Math.abs(num);
  return num;
};

const parseLatitude = (value: string | number) => {
  if (value === "" || value === null || value === undefined) return NaN;
  if (typeof value === "number") return value;
  const text = stripCoord(value);
  const match = text.match(/^([+-]?\d+(?:\.\d+)?)\s*([NSns])?$/);
  if (!match) {
    const num = Number(text);
    return num;
  }
  let num = Number(match[1]);
  if (match[2] && match[2].toUpperCase() === "S") num = -Math.abs(num);
  if (match[2] && match[2].toUpperCase() === "N") num = Math.abs(num);
  return num;
};

/** Format like code.html: `11.2345° E` / `45.8321° N` (NBSP keeps the space visible). */
const formatLongitude = (value: string | number, digits = 4) => {
  const num = parseLongitude(value);
  if (isNaN(num)) return "";
  const abs = Math.abs(num).toFixed(digits);
  return `${abs}°\u00A0${num < 0 ? "W" : "E"}`;
};

const formatLatitude = (value: string | number, digits = 4) => {
  const num = parseLatitude(value);
  if (isNaN(num)) return "";
  const abs = Math.abs(num).toFixed(digits);
  return `${abs}°\u00A0${num < 0 ? "S" : "N"}`;
};

// 定义经度的自定义校验规则
const validateLongitude = (rule: any, value: string, callback: any) => {
  // 先判断是否为空
  if (!value && value !== 0) {
    return callback(new Error("请输入经度"));
  }

  const num = parseLongitude(value);

  // 判断是否为有效数字
  if (isNaN(num)) {
    return callback(new Error("请输入有效的数字"));
  }

  // 校验范围
  if (num < -180 || num > 180) {
    return callback(new Error("经度输入范围为-180到180"));
  }

  // 校验通过
  callback();
};

// 定义纬度的自定义校验规则
const validateLatitude = (rule: any, value: string, callback: any) => {
  // 先判断是否为空
  if (!value && value !== 0) {
    return callback(new Error("请输入纬度"));
  }

  const num = parseLatitude(value);

  // 判断是否为有效数字
  if (isNaN(num)) {
    return callback(new Error("请输入有效的数字"));
  }

  // 校验范围
  if (num < -90 || num > 90) {
    return callback(new Error("纬度输入范围为-90到90"));
  }

  // 校验通过
  callback();
};
const validateFileName = (rule: any, value: string, callback: any) => {
  const trimmedValue = (value || "").trim();
  if (!trimmedValue) {
    return callback(new Error("工程名称不能为空"));
  }

  const invalidChars = /[\\/:*?"<>|]/g;
  if (invalidChars.test(trimmedValue)) {
    return callback(new Error('工程名称不能包含 \\ / : * ? " < > | 字符'));
  }

  const controlChars = /[\x00-\x1F\x7F]/g;
  if (controlChars.test(trimmedValue)) {
    return callback(new Error("工程名称不能包含不可见控制字符"));
  }

  const reservedNames = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i;
  const baseName = trimmedValue.split(".")[0];
  if (reservedNames.test(baseName)) {
    return callback(new Error("工程名称不能使用系统保留名称（如 con、prn 等）"));
  }

  if (trimmedValue.length > 255) {
    return callback(new Error("工程名称长度不能超过 255 字符"));
  }

  callback();
};

export {
  validateLongitude,
  validateLatitude,
  validateFileName,
  parseLongitude,
  parseLatitude,
  formatLongitude,
  formatLatitude,
};