// 媒体节点配置获取与工具函数（与 hookLoad/model.js 结构一致，面向 media_load_nodes）
import { fetchMediaConfig } from './configLoader.js'

// 动态配置缓存（仅缓存媒体部分）
let mediaConfigCache = null;
let mediaConfigLoadPromise = null;

export const mediaNodeList = [
    'LoadImage',
    'LoadImageMask',
    'LoadAudio',
    'LoadVideo',
    'Load3D',
    'VHS_LoadVideo',
    'VHS_LoadAudioUpload'
]
// 常见的媒体输入字段名（作为回退匹配）
export const possibleMediaWidgetNames = [
    "image",
    "file",
    "audio",
    "video",
    "model_file"
];

// 获取媒体配置的API函数（使用共享配置加载器）
export async function fetchMediaConfigWithCache() {
    if (mediaConfigCache) return mediaConfigCache;
    if (mediaConfigLoadPromise) return mediaConfigLoadPromise;

    mediaConfigLoadPromise = (async () => {
        const config = await fetchMediaConfig();
        if (config) {
            mediaConfigCache = config;
        }
        return config;
    })();

    return mediaConfigLoadPromise;
}

// 根据节点名称获取媒体节点配置（仅使用缓存，不阻塞返回；触发后台预取）
export async function getMediaNodeConfig(nodeName) {
    // 后台触发一次预取
    if (!mediaConfigLoadPromise) { try { void fetchMediaConfigWithCache(); } catch (e) {} }

    if (mediaConfigCache && mediaConfigCache[nodeName]) {
        return { nodeName, config: mediaConfigCache[nodeName] };
    }
    return null;
}

// 从媒体配置中提取此节点的输入键（过滤 disable_comfyagent）
export function getMediaInputKeys(mediaNodeConfig) {
    if (!mediaNodeConfig || !mediaNodeConfig.config || !mediaNodeConfig.config.inputs) return [];
    const inputs = mediaNodeConfig.config.inputs;
    const keys = [];
    for (const key of Object.keys(inputs)) {
        const cfg = inputs[key];
        if (cfg && !cfg.disable_comfyagent) keys.push(key);
    }
    return keys;
}


export async function computeIsMediaNode(nodeName) {
    if (mediaNodeList.includes(nodeName)) {
        return true;
    }

    // 2. 检查media_load_nodes的keys
    const config = await fetchMediaConfigWithCache();
    if (config) {
        if (config.hasOwnProperty(nodeName)) {
            return true;
        }
    }

    return false;
}

// 启动时后台预取（不阻塞后续逻辑）
try { void fetchMediaConfigWithCache(); } catch (e) {}
