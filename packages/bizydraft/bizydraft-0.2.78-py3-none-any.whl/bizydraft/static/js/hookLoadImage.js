import { app } from "../../scripts/app.js";
import { getCookie, computeIsLoadNode, computeExt, hideWidget } from './tool.js';
import { getMediaNodeConfig, getMediaInputKeys, possibleMediaWidgetNames } from './hookLoad/media.js';


app.registerExtension({
    name: "bizyair.image.to.oss",
    async beforeRegisterNodeDef(nodeType, nodeData) {
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
        if (computeIsLoadNode(nodeData.name)) {
            nodeType.prototype.onNodeCreated = async function() {
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
                    // 如果找到va_widgets，处理它们
                    if (va_widgets.length > 0) {
                        // 隐藏所有va_widgets
                        va_widgets.forEach(va_widget => {
                            hideWidget(this, va_widget.name);
                        });

                        // 创建image_name_widget来替代显示
                        if (!image_name_widget) {
                            image_name_widget = this.addWidget("combo", "image_name", "", function(e){
                                const item = image_list.find(item => item.name === e)
                                if (item) {
                                    const image_url = decodeURIComponent(item.url);
                                    // 更新所有va_widgets的值
                                    va_widgets.forEach(va_widget => {
                                        va_widget.value = image_url;
                                        if (va_widget.callback) {
                                            va_widget.callback(e);
                                        }
                                    });
                                }
                            }, {
                                serialize: true,
                                values: image_list.map(item => item.name)
                            });
                        }

                        // 为每个va_widget重写callback
                        va_widgets.forEach(va_widget => {
                            // 保存va_widget的原始callback
                            const originalVaCallback = va_widget.callback;

                            // 重写va_widget的callback，当被触发时给image_name_widget赋值
                            va_widget.callback = function(e) {
                                // 调用原始callback
                                if (originalVaCallback) {
                                    originalVaCallback(e);
                                }

                                // 给image_name_widget赋值
                                if (image_name_widget) {
                                    if (typeof e === 'string') {
                                        const item = image_list.find(item => item.url === e);
                                        if (item) {
                                            image_name_widget.value = item.name;
                                        } else {
                                            // 如果没找到对应的item，尝试从URL中提取文件名
                                            const fileName = e.split('/').pop();
                                            image_name_widget.value = fileName;
                                        }
                                    }
                                }
                            };

                            // 监听widget的value变化
                            const originalSetValue = va_widget.setValue;
                            if (originalSetValue) {
                                va_widget.setValue = function(value) {
                                    originalSetValue.call(this, value);

                                    // 当value变化时，更新image_name_widget
                                    if (image_name_widget && value) {
                                        if (typeof value === 'string') {
                                            const item = image_list.find(item => item.url === value);
                                            if (item) {
                                                image_name_widget.value = item.name;
                                            } else {
                                                const fileName = value.split('/').pop();
                                                image_name_widget.value = fileName;
                                            }
                                        }
                                    }
                                };
                            }
                        });
                    }

                    // 如果va_widgets没有创建image_name_widget，使用原有逻辑创建
                    if (!image_name_widget && media_widget) {
                        image_name_widget = this.addWidget("combo", "image_name", "", function(e){
                            const item = image_list.find(item => item.name === e)
                            const image_url = decodeURIComponent(item.url);
                            media_widget.value = image_url;
                            if (media_widget.callback) {
                                media_widget.callback(e);
                            }
                        }, {
                            serialize: true,
                            values: image_list.map(item => item.name)
                        });
                    }
                    const val = image_list.find(item => item.url === media_widget.value)?.name || media_widget.value
                    image_name_widget.label = media_widget.label
                    image_name_widget.value = val

                    const currentIndex = this.widgets.indexOf(image_name_widget);
                    if (currentIndex > 1) {
                        this.widgets.splice(currentIndex, 1);
                        this.widgets.splice(1, 0, image_name_widget);
                    }
                    hideWidget(this, media_widget.name)
                    media_widget.options.values = image_list.map(item => item.name);

                    const callback = media_widget.callback
                    media_widget.callback = async function(e) {
                        if (typeof e == 'string') {
                            const item = e.includes('http') ?
                                image_list.find(item => item.url === e) :
                                image_list.find(item => item.name === e)

                            const image_url = item ? decodeURIComponent(item.url) : e;

                            image_name_widget.value = item ? item.name : e;
                            media_widget.value = image_url;
                            callback([image_url])
                        } else {
                            const item = e[0].split('/')
                            image_name_widget.options.values.pop()
                            image_name_widget.options.values.push(item[item.length - 1])
                            image_name_widget.value = item[item.length - 1]
                            image_list.push({
                                name: item[item.length - 1],
                                url: e[0]
                            })
                            callback(e)
                        }
                    }
                    return true
                }
                await getData()


                function applyWorkflowImageSettings(workflowParams, image_list, media_widget, image_name_widget, currentNodeId) {
                    if (workflowParams && workflowParams.nodes) {
                        // 根据当前节点ID查找对应的节点数据，而不是总是选择第一个
                        const imageNode = workflowParams.nodes.find(item =>
                            computeIsLoadNode(item.type) && item.id === currentNodeId
                        )
                        if (imageNode && imageNode.widgets_values) {
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
                    applyWorkflowImageSettings(window.currentWorkflowData, image_list, media_widget, image_name_widget, this.id);
                    // 清除存储的数据，避免重复处理
                    delete window.currentWorkflowData;
                } else {
                    // 原有的调用
                    applyWorkflowImageSettings(workflowParams, image_list, media_widget, image_name_widget, this.id);
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
