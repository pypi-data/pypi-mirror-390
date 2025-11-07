import { app } from "../../scripts/app.js";
import { getCookie, computeExt, hideWidget } from './tool.js';
import { getMediaNodeConfig, getMediaInputKeys, possibleMediaWidgetNames, computeIsMediaNode, mediaNodeList, fetchMediaConfigWithCache } from './hookLoad/media.js';



app.registerExtension({
    name: "bizyair.image.to.oss",
    beforeRegisterNodeDef(nodeType, nodeData) {
        let workflowParams = null
        document.addEventListener('workflowLoaded', (event) => {
            workflowParams = event.detail;
        })
        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;

            Array.from(files).forEach((file) => {
                if (file.type === 'application/json' || file.name.endsWith('.json')) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        try {
                            const jsonContent = JSON.parse(event.target.result);
                            if (jsonContent && jsonContent.nodes) {
                                window.currentWorkflowData = jsonContent;
                            }
                        } catch (error) {
                            console.error('解析JSON文件失败:', error);
                        }
                    };
                    reader.readAsText(file);
                }
            });
        })
        nodeType.prototype.onNodeCreated = async function() {
            if (await computeIsMediaNode(nodeData.name)) {
                const apiHost = 'https://bizyair.cn/api'
                // 优先使用 API 的媒体输入键匹配到具体的 widget；若未命中则回退到原有字段集合
                let media_widget = null;
                const mediaNodeConfig = await getMediaNodeConfig(nodeData.name);
                const apiInputKeys = getMediaInputKeys(mediaNodeConfig);
                if (apiInputKeys && apiInputKeys.length > 0) {
                    for (const key of apiInputKeys) {
                        const w = this.widgets.find(x => x.name === key);
                        if (w) { media_widget = w; break; }
                    }
                }
                if (!media_widget) {
                    media_widget = this.widgets.find(w => {
                        return possibleMediaWidgetNames.includes(w.name);
                    });
                }
                // 查找所有name等于接口配置中inputs下的字段的widget（如video、audio等）
                let va_widgets = [];
                if (apiInputKeys && apiInputKeys.length > 0) {
                    for (const key of apiInputKeys) {
                        const w = this.widgets.find(x => x.name === key);
                        if (w) {
                            va_widgets.push(w);
                        }
                    }
                }

                // 如果API配置没有找到，使用回退逻辑查找常见的媒体widget
                if (va_widgets.length === 0) {
                    for (const widgetName of possibleMediaWidgetNames) {
                        const w = this.widgets.find(x => x.name === widgetName);
                        if (w) {
                            va_widgets.push(w);
                        }
                    }
                }
                let image_name_widget = this.widgets.find(w => w.name === 'image_name');
                let image_list = []
                const getData = async () => {
                    const res = await fetch(`${apiHost}/special/community/commit_input_resource?${
                        new URLSearchParams({
                            ext: computeExt(nodeData.name),
                            current: 1,
                            page_size: 100

                        }).toString()
                    }`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getCookie('bizy_token')}`
                        }
                    })
                    const {data} = await res.json()
                    const list = (data && data.data && data.data.data && data.data.data.list) || []
                    image_list = list.filter(item => item.name).map(item => {
                        return {
                            url: item.url,
                            id: item.id,
                            name: item.name
                        }
                    })

                    // 📊 方案：使用 Map 缓存 URL→Name 映射（O(1) 查找）
                    const urlToNameMap = new Map();
                    const nameToItemMap = new Map();
                    image_list.forEach(item => {
                        urlToNameMap.set(item.url, item.name);
                        nameToItemMap.set(item.name, item);
                    });

                    // 如果找到va_widgets，处理它们
                    if (va_widgets.length > 0) {
                        // 标志位：防止批量更新时触发监听
                        let isBatchUpdating = false;

                        // 创建image_name_widget来替代显示
                        if (!image_name_widget) {
                            image_name_widget = this.addWidget("combo", "image_name", "", function(e){
                                const item = nameToItemMap.get(e);
                                if (item) {
                                    const image_url = decodeURIComponent(item.url);
                                    // 批量更新时跳过监听
                                    isBatchUpdating = true;
                                    va_widgets.forEach(va_widget => {
                                        va_widget.value = image_url;
                                        if (va_widget.callback) {
                                            va_widget.callback(image_url);
                                        }
                                    });
                                    isBatchUpdating = false;
                                }
                            }, {
                                serialize: true,
                                values: image_list.map(item => item.name)
                            });
                        }

                        // 隐藏所有va_widgets 并设置监听
                        va_widgets.forEach(va_widget => {
                            hideWidget(this, va_widget.name);
                            let _value = va_widget.value;

                            // 检查并删除现有的 value 属性描述符（如果存在）
                            const existingDescriptor = Object.getOwnPropertyDescriptor(va_widget, 'value');
                            if (existingDescriptor && !existingDescriptor.configurable) {
                                // 如果不可配置，跳过重新定义
                                return;
                            }

                            // 删除现有属性（如果存在）
                            if (existingDescriptor) {
                                delete va_widget.value;
                            }

                            Object.defineProperty(va_widget, 'value', {
                                get: function() {
                                    return _value;
                                },
                                set: function(newValue) {
                                    _value = newValue;

                                    // 批量更新时跳过监听逻辑
                                    if (isBatchUpdating) {
                                        return;
                                    }
                                    // 使用 Map 快速查找（O(1)）
                                    const name = urlToNameMap.get(newValue);
                                    if (name) {
                                        image_name_widget.value = name;
                                    } else {
                                        // 如果没找到，从URL提取文件名
                                        const fileName = newValue.split('/').pop();
                                        image_name_widget.value = fileName;
                                    }
                                },
                                enumerable: true,
                                configurable: true
                            });
                        });


                        // 为每个va_widget重写callback
                        va_widgets.forEach(va_widget => {
                            // 保存va_widget的原始callback
                            const originalVaCallback = va_widget.callback;
                            // 重写va_widget的callback，当被触发时给image_name_widget赋值
                            va_widget.callback = function(e) {
                                if (image_name_widget) {
                                    if (typeof e === 'string') {
                                        // 使用 Map 快速查找（O(1)）
                                        const name = urlToNameMap.get(e);
                                        if (name) {
                                            image_name_widget.value = name;
                                        } else {
                                            // 如果没找到，从URL提取文件名
                                            const fileName = e.split('/').pop();
                                            image_name_widget.value = fileName;
                                        }
                                    }
                                }

                                // 调用原始callback
                                if (originalVaCallback) {
                                    originalVaCallback(e);
                                }
                            };
                        });
                    }

                    // 如果va_widgets没有创建image_name_widget，使用原有逻辑创建
                    if (!image_name_widget && media_widget) {
                        image_name_widget = this.addWidget("combo", "image_name", "", function(e){
                            const item = nameToItemMap.get(e);
                            if (item) {
                                const image_url = decodeURIComponent(item.url);
                                media_widget.value = image_url;
                                if (media_widget.callback) {
                                    media_widget.callback(image_url);
                                }
                            }
                        }, {
                            serialize: true,
                            values: image_list.map(item => item.name)
                        });
                    }

                    // 如果进入了va_widgets分支，使用va_widgets中第一个作为media_widget的替代
                    const actualMediaWidget = va_widgets.length > 0 ? va_widgets[0] : media_widget;

                    if (image_name_widget && actualMediaWidget) {
                        const val = urlToNameMap.get(actualMediaWidget.value) || actualMediaWidget.value
                        image_name_widget.label = actualMediaWidget.label
                        image_name_widget.value = val

                        const currentIndex = this.widgets.indexOf(image_name_widget);
                        if (currentIndex > 1) {
                            this.widgets.splice(currentIndex, 1);
                            this.widgets.splice(1, 0, image_name_widget);
                        }

                        // 如果没有进入va_widgets分支，才隐藏media_widget
                        if (va_widgets.length === 0) {
                            hideWidget(this, media_widget.name)
                        }

                        actualMediaWidget.options.values = image_list.map(item => item.name);

                        // 对于va_widgets的情况，callback已经在上面重写过了，不需要再次重写
                        if (va_widgets.length === 0 && media_widget) {
                            const callback = media_widget.callback
                            media_widget.callback = function(e) {
                                if (typeof e == 'string') {
                                    // 使用 Map 快速查找（O(1)）
                                    const item = e.includes('http') ?
                                        (urlToNameMap.has(e) ? {url: e, name: urlToNameMap.get(e)} : null) :
                                        (nameToItemMap ? nameToItemMap.get(e) : null);

                                    const image_url = item ? decodeURIComponent(item.url) : e;

                                    image_name_widget.value = item ? item.name : e;
                                    media_widget.value = image_url;
                                    if (callback) {
                                        callback([image_url])
                                    }
                                } else {
                                    const item = e[0].split('/')
                                    const fileName = item[item.length - 1];
                                    image_name_widget.options.values.pop()
                                    image_name_widget.options.values.push(fileName)
                                    image_name_widget.value = fileName
                                    image_list.push({
                                        name: fileName,
                                        url: e[0]
                                    })
                                    // 同步更新 Map
                                    urlToNameMap.set(e[0], fileName);
                                    if (nameToItemMap) {
                                        nameToItemMap.set(fileName, {url: e[0], name: fileName});
                                    }
                                    if (callback) {
                                        callback(e)
                                    }
                                }
                            }
                        }
                    }
                    return true
                }
                await getData()


                async function applyWorkflowImageSettings(workflowParams, image_list, media_widget, image_name_widget, currentNodeId) {
                    if (workflowParams && workflowParams.nodes) {
                        // 先获取配置，然后将 mediaNodeList 和配置的 keys 合并
                        const config = await fetchMediaConfigWithCache();
                        const allMediaNodeTypes = new Set(mediaNodeList);
                        if (config) {
                            // 将配置中的 keys 添加到集合中
                            for (const key of Object.keys(config)) {
                                allMediaNodeTypes.add(key);
                            }
                        }

                        // 使用同步的 includes 查找匹配的节点（完全避免循环中的异步）
                        const imageNode = workflowParams.nodes.find(item =>
                            item.id === currentNodeId && allMediaNodeTypes.has(item.type)
                        )

                        if (imageNode && imageNode.widgets_values && imageNode.widgets_values[0]) {
                            const item = imageNode.widgets_values[0].split('/')
                            image_list.push({
                                name: item[item.length - 1],
                                url: imageNode.widgets_values[0]
                            })
                            media_widget.value = imageNode.widgets_values[0]

                            media_widget.options.values = image_list.map(item => item.url)
                            image_name_widget.options.values = image_list.map(item => item.name)
                            media_widget.callback(imageNode.widgets_values[0])
                        }
                    }
                }

                // 如果有存储的工作流数据，应用图像设置
                if (window.currentWorkflowData) {
                    await applyWorkflowImageSettings(window.currentWorkflowData, image_list, media_widget, image_name_widget, this.id);
                    // 清除存储的数据，避免重复处理
                    delete window.currentWorkflowData;
                } else {
                    // 原有的调用
                    await applyWorkflowImageSettings(workflowParams, image_list, media_widget, image_name_widget, this.id);
                }
                //在这里发个postmessage
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'hookLoadImageCompleted',
                    params: {}
                }, '*');
            }
        }
    }
})

// app.api.addEventListener('graphChanged', (e) => {
//     console.log('Graph 发生变化，当前 workflow JSON:', e.detail)
//     window.parent.postMessage({
//         type: 'functionResult',
//         method: 'workflowChanged',
//         result: e.detail
//     }, '*');

//     document.dispatchEvent(new CustomEvent('workflowLoaded', {
//         detail: e.detail
//     }));
// })
