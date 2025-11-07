// 媒体节点配置获取与工具函数（与 hookLoad/model.js 结构一致，面向 media_load_nodes）

// 动态配置缓存（仅缓存媒体部分）
let mediaConfigCache = null;
let mediaConfigLoadPromise = null;

// API配置（与模型相同接口，不同数据块）
const CONFIG_API_URL = 'https://bizyair.cn/api/special/comfyagent_node_config?t=' + Math.floor(Date.now() / 60000);

// 常见的媒体输入字段名（作为回退匹配）
export const possibleMediaWidgetNames = [
    "image",
    "file",
    "audio",
    "video",
    "model_file"
];

// 获取媒体配置的API函数（只解析 media_load_nodes）
export async function fetchMediaConfig() {
    if (mediaConfigCache) return mediaConfigCache;
    if (mediaConfigLoadPromise) return mediaConfigLoadPromise;

    mediaConfigLoadPromise = (async () => {
        try {
            const response = await fetch(CONFIG_API_URL, { credentials: 'include' });
            if (!response || !response.ok) {
                throw new Error('HTTP error ' + (response && response.status));
            }
            const result = await response.json();
            if (result && result.code === 20000 && result.data && result.data.media_load_nodes) {
                mediaConfigCache = result.data.media_load_nodes;
                return mediaConfigCache;
            }
            throw new Error('API返回数据不包含 media_load_nodes');
        } catch (err) {
            console.error('获取媒体配置失败:', err);
            mediaConfigCache = null;
            return null;
        }
    })();

    return mediaConfigLoadPromise;
}

// 根据节点名称获取媒体节点配置（仅使用缓存，不阻塞返回；触发后台预取）
export async function getMediaNodeConfig(nodeName) {
    // 后台触发一次预取
    if (!mediaConfigLoadPromise) { try { void fetchMediaConfig(); } catch (e) {} }

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

// 启动时后台预取（不阻塞后续逻辑）
try { void fetchMediaConfig(); } catch (e) {}
