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
export { validateLongitude, validateLatitude };