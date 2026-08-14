// 定义经度的自定义校验规则
const validateLongitude = (rule: any, value: string, callback: any) => {
  // 先判断是否为空
  if (!value) {
    return callback(new Error('请输入经度'));
  }

  // 将字符串转换为数值
  const num = Number(value);

  // 判断是否为有效数字
  if (isNaN(num)) {
    return callback(new Error('请输入有效的数字'));
  }

  // 校验范围
  if (num < -180 || num > 180) {
    return callback(new Error('经度输入范围为-180到180'));
  }

  // 校验通过
  callback();
};

// 定义纬度的自定义校验规则
const validateLatitude = (rule: any, value: string, callback: any) => {
  // 先判断是否为空
  if (!value) {
    return callback(new Error('请输入纬度'));
  }

  // 将字符串转换为数值
  const num = Number(value);

  // 判断是否为有效数字
  if (isNaN(num)) {
    return callback(new Error('请输入有效的数字'));
  }

  // 校验范围
  if (num < -90 || num > 90) {
    return callback(new Error('纬度输入范围为-90到90'));
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

export { validateLongitude, validateLatitude, validateFileName };