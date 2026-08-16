// 居中展示一个 黑色的描述信息
export function Toast(msg: string, duration: number = 3000){
    var m = document.createElement('div');
    m.innerHTML = msg;
    m.style.cssText = `
        font-size: 14px;
        color: rgb(255, 255, 255);
        background-color: rgba(0, 0, 0, .8);
        padding: 10px 16px;
        margin: 0;
        border-radius: 8px;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: auto;
        max-width: 80vw;
        z-index:9999999;
        overflow:hidden;
        text-align: center;
        white-space: nowrap;`;
    document.body.appendChild(m);
    setTimeout(function(){
        var d = 0.5;
        m.style.opacity = '0';
        setTimeout(function () { document.body.removeChild(m) }, d * 1000);
    }, duration);
}

// json 置空
export function initJson(obj: any){
    let runJson = obj
    for(let i of Object.keys(runJson)){
        if(runJson[i] instanceof Array){
            runJson[i] = []
        }else if(typeof runJson[i] == "object"){
            // 日期格式也是属于 object 淦
            if(!isNaN(Date.parse(runJson[i]))){
                runJson[i] = ''
            }
            initJson(runJson[i]);
        } else {
            runJson[i] = '';
        }
    }
    return runJson;
}

// vite 中动态获取图片
export function getAssetsSrc(imgName: string){
    /**
     * 具体思路为：
     *  import.meta.url 会得到当前文件地址
     *  然后利用 new URL()  新创建的 URL 对象
     *  其中的 href 就是所需的名称
     */
    return new URL(`../image/${imgName}`, import.meta.url).href;
}

// 深度克隆
export function deepClone(source: object){
    if(!source && typeof source !== 'object'){
      throw new Error('error arguments');
    }
    const targetObj = source.constructor === Array ? [] : {};
    Object.keys(source).forEach(keys => {
        if(source[keys] && typeof source[keys] === 'object'){
            targetObj[keys] = deepClone(source[keys]);
        }else{
            targetObj[keys] = source[keys];
        }
    });
    return targetObj;
}

/**
* 参数处理
* @param {*} params  参数
*/
export function tansParams(params:object){
    let result = ''
    for (const propName of Object.keys(params)) {
        const value = params[propName];
        var part = encodeURIComponent(propName) + "=";
        if (value !== null && typeof (value) !== "undefined") {
            if (typeof value === 'object') {
                for (const key of Object.keys(value)) {
                    if (value[key] !== null && typeof (value[key]) !== 'undefined') {
                        let params = propName + '[' + key + ']';
                        var subPart = encodeURIComponent(params) + "=";
                        result += subPart + encodeURIComponent(value[key]) + "&";
                    }
                }
            } else {
                result += part + encodeURIComponent(value) + "&";
            }
        }
    }
    return result;
}

// 验证是否为blob格式
export async function blobValidate(data:Blob){
    try{
        const text = await data.text();
        JSON.parse(text);
        return false;
    }catch (error){
        return true;
    }
}