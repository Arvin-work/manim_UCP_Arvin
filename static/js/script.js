class VisualizationApp {
    constructor() {
        this.currentScene = '2D';
        this.currentInputType = 'explicit';
        this.selectedFunctions = [];
        this.currentTaskId = null;
        this.taskCheckInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateDisplay();
        this.updateTimestamp();
        
        setInterval(() => this.updateTimestamp(), 1000);
    }

    bindEvents() {
        // 场景切换
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchScene(e.target.closest('.tab-button').dataset.scene);
            });
        });

        // 输入类型切换 - 修改为单选
        document.querySelectorAll('.input-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const inputType = e.target.closest('.input-tab').dataset.inputType;
                this.switchInputType(inputType);
                
                // 移除其他输入类型的选中状态
                document.querySelectorAll('.input-tab').forEach(otherTab => {
                    if (otherTab !== e.target.closest('.input-tab')) {
                        otherTab.classList.remove('active');
                    }
                });
                
                // 添加当前输入类型的选中状态
                e.target.closest('.input-tab').classList.add('active');
            });
        });

        // 功能选择 - 修改为单选
        document.querySelectorAll('.function-checkbox input').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const func = e.target.value;
                const isSelected = e.target.checked;
                
                // 如果是选中状态，先取消其他所有功能的选择
                if (isSelected) {
                    document.querySelectorAll('.function-checkbox input').forEach(otherCheckbox => {
                        if (otherCheckbox !== e.target) {
                            otherCheckbox.checked = false;
                            // 从选中函数列表中移除其他函数
                            this.selectedFunctions = this.selectedFunctions.filter(f => f !== otherCheckbox.value);
                            
                            // 隐藏其他功能的参数
                            if (otherCheckbox.value === 'taylor') {
                                this.toggleTaylorParameters(false);
                            } else if (otherCheckbox.value === 'differentiation') {
                                this.toggleDifferentiationParameters(false);
                            } else if (otherCheckbox.value === 'integration') {
                                this.toggleIntegrationParameters(false);
                            }
                        }
                    });
                    
                    // 添加当前函数到选中列表
                    this.selectedFunctions.push(func);
                    
                    // 特别处理各功能的参数显示
                    if (func === 'taylor') {
                        this.toggleTaylorParameters(true);
                        this.toggleDifferentiationParameters(false);
                        this.toggleIntegrationParameters(false);
                    } else if (func === 'differentiation') {
                        this.toggleDifferentiationParameters(true);
                        this.toggleTaylorParameters(false);
                        this.toggleIntegrationParameters(false);
                    } else if (func === 'integration') {
                        this.toggleIntegrationParameters(true);
                        this.toggleTaylorParameters(false);
                        this.toggleDifferentiationParameters(false);
                    } else {
                        this.toggleTaylorParameters(false);
                        this.toggleDifferentiationParameters(false);
                        this.toggleIntegrationParameters(false);
                    }
                } else {
                    // 如果是取消选中，从选中函数列表中移除
                    this.selectedFunctions = this.selectedFunctions.filter(f => f !== func);
                    
                    // 如果取消的是某个功能，隐藏相关参数
                    if (func === 'taylor') {
                        this.toggleTaylorParameters(false);
                    } else if (func === 'differentiation') {
                        this.toggleDifferentiationParameters(false);
                    } else if (func === 'integration') {
                        this.toggleIntegrationParameters(false);
                    }
                }
                
                this.addLog(`${this.getFunctionName(func)} ${isSelected ? '已选择' : '已取消'}`, 'info');
            });
        });

        // 开始创作按钮
        document.getElementById('start-creation').addEventListener('click', () => {
            this.startCreation();
        });

        // 重置按钮
        document.getElementById('reset-config').addEventListener('click', () => {
            this.resetConfig();
        });
    }

    toggleTaylorParameters(show) {
        const taylorPointGroup = document.getElementById('taylor-point-group');
        const maxOrderGroup = document.getElementById('max-order-group');
        
        if (show) {
            taylorPointGroup.style.display = 'block';
            maxOrderGroup.style.display = 'block';
            this.addLog('泰勒展开功能已启用，请输入展开点和最高阶数', 'info');
        } else {
            taylorPointGroup.style.display = 'none';
            maxOrderGroup.style.display = 'none';
        }
    }

    toggleDifferentiationParameters(show) {
        const fitPointGroup = document.getElementById('fit-point-group');
        const radiusGroup = document.getElementById('radius-group');
        
        if (show) {
            fitPointGroup.style.display = 'block';
            radiusGroup.style.display = 'block';
            this.addLog('微分展示功能已启用，请输入拟合点和拟合半径', 'info');
        } else {
            fitPointGroup.style.display = 'none';
            radiusGroup.style.display = 'none';
        }
    }

    toggleIntegrationParameters(show) {
        const lowerBoundGroup = document.getElementById('lower-bound-group');
        const upperBoundGroup = document.getElementById('upper-bound-group');
        
        if (show) {
            lowerBoundGroup.style.display = 'block';
            upperBoundGroup.style.display = 'block';
            this.addLog('积分展示功能已启用，请输入积分上下限', 'info');
        } else {
            lowerBoundGroup.style.display = 'none';
            upperBoundGroup.style.display = 'none';
        }
    }

    async switchScene(sceneType) {
        try {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-scene="${sceneType}"]`).classList.add('active');
            
            this.currentScene = sceneType;
            
            const response = await fetch('/api/switch_scene', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scene_type: sceneType })
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.addLog(`切换到${sceneType}场景`, 'success');
                this.updateDisplay();
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            this.addLog(`场景切换失败: ${error.message}`, 'error');
        }
    }

    async switchInputType(inputType) {
        try {
            this.currentInputType = inputType;
            
            const response = await fetch('/api/switch_input_type', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input_type: inputType })
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.addLog(`切换到${inputType === 'explicit' ? '显函数' : '隐函数'}输入`, 'success');
                this.updateDisplay();
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            this.addLog(`输入类型切换失败: ${error.message}`, 'error');
        }
    }

    getFunctionName(func) {
        const names = {
            'plot': '单纯画图',
            'differentiation': '微分展示',
            'integration': '积分展示',
            'animation': '动画效果',
            'transformation': '变换展示',
            'taylor': '泰勒展开'
        };
        return names[func] || func;
    }

    validateTaylorParameters() {
        if (!this.selectedFunctions.includes('taylor')) {
            return { valid: true };
        }

        const taylorPoint = document.getElementById('taylor-point').value;
        const maxOrder = document.getElementById('max-order').value;
        const functionExpression = document.getElementById('function-input').value;

        if (!functionExpression.trim()) {
            return { 
                valid: false, 
                message: '请填写函数表达式' 
            };
        }

        if (!taylorPoint.trim()) {
            return { 
                valid: false, 
                message: '请填写泰勒展开点' 
            };
        }

        // 验证展开点是否为有效数字
        if (isNaN(parseFloat(taylorPoint))) {
            return { 
                valid: false, 
                message: '展开点必须是有效数字' 
            };
        }

        return { 
            valid: true, 
            taylorPoint: parseFloat(taylorPoint),
            maxOrder: parseInt(maxOrder),
            functionExpression: functionExpression
        };
    }

    validateDifferentiationParameters() {
        if (!this.selectedFunctions.includes('differentiation')) {
            return { valid: true };
        }

        const fitPoint = document.getElementById('fit-point').value;
        const radius = document.getElementById('radius').value;
        const functionExpression = document.getElementById('function-input').value;

        if (!functionExpression.trim()) {
            return { 
                valid: false, 
                message: '请填写函数表达式' 
            };
        }

        if (!fitPoint.trim()) {
            return { 
                valid: false, 
                message: '请填写拟合点' 
            };
        }

        if (!radius.trim()) {
            return { 
                valid: false, 
                message: '请填写拟合半径' 
            };
        }

        // 验证拟合点和半径是否为有效数字
        if (isNaN(parseFloat(fitPoint))) {
            return { 
                valid: false, 
                message: '拟合点必须是有效数字' 
            };
        }

        if (isNaN(parseFloat(radius)) || parseFloat(radius) <= 0) {
            return { 
                valid: false, 
                message: '拟合半径必须是正数' 
            };
        }

        return { 
            valid: true, 
            fitPoint: parseFloat(fitPoint),
            radius: parseFloat(radius),
            functionExpression: functionExpression
        };
    }

    validateIntegrationParameters() {
        if (!this.selectedFunctions.includes('integration')) {
            return { valid: true };
        }

        const lowerBound = document.getElementById('lower-bound').value;
        const upperBound = document.getElementById('upper-bound').value;
        const functionExpression = document.getElementById('function-input').value;

        if (!functionExpression.trim()) {
            return { 
                valid: false, 
                message: '请填写函数表达式' 
            };
        }

        if (!lowerBound.trim()) {
            return { 
                valid: false, 
                message: '请填写积分下限' 
            };
        }

        if (!upperBound.trim()) {
            return { 
                valid: false, 
                message: '请填写积分上限' 
            };
        }

        // 验证积分上下限是否为有效数字
        if (isNaN(parseFloat(lowerBound))) {
            return { 
                valid: false, 
                message: '积分下限必须是有效数字' 
            };
        }

        if (isNaN(parseFloat(upperBound))) {
            return { 
                valid: false, 
                message: '积分上限必须是有效数字' 
            };
        }

        if (parseFloat(lowerBound) >= parseFloat(upperBound)) {
            return { 
                valid: false, 
                message: '积分下限必须小于积分上限' 
            };
        }

        return { 
            valid: true, 
            lowerBound: parseFloat(lowerBound),
            upperBound: parseFloat(upperBound),
            functionExpression: functionExpression
        };
    }

    async checkTaskStatus(taskId) {
        try {
            const response = await fetch(`/api/task_status/${taskId}`);
            const status = await response.json();
            
            if (status.status === 'completed') {
                this.addLog('动画生成完成！正在打开播放器...', 'success');
                this.stopTaskChecking();
                
                // 提供下载链接
                this.addLog(`<a href="/api/download_animation/${taskId}" target="_blank">下载动画文件</a>`, 'info');
                
            } else if (status.status === 'error') {
                this.addLog(`动画生成失败: ${status.error}`, 'error');
                this.stopTaskChecking();
            }
            // 如果状态是processing，继续等待
            
        } catch (error) {
            this.addLog(`检查任务状态失败: ${error.message}`, 'error');
        }
    }

    startTaskChecking(taskId) {
        this.currentTaskId = taskId;
        this.taskCheckInterval = setInterval(() => {
            this.checkTaskStatus(taskId);
        }, 2000); // 每2秒检查一次
    }

    stopTaskChecking() {
        if (this.taskCheckInterval) {
            clearInterval(this.taskCheckInterval);
            this.taskCheckInterval = null;
        }
    }

    async startCreation() {
        try {
            this.addLog('开始处理可视化请求...', 'info');

            // 验证输入类型是否已选择
            if (!this.currentInputType) {
                this.addLog('请选择输入类型（显函数或隐函数）', 'error');
                return;
            }

            // 验证功能选项是否已选择
            if (this.selectedFunctions.length === 0) {
                this.addLog('请至少选择一个功能选项', 'error');
                return;
            }

            // 验证函数表达式是否已填写
            const functionExpression = document.getElementById('function-input').value;
            if (!functionExpression.trim()) {
                this.addLog('请填写函数表达式', 'error');
                return;
            }

            // 验证泰勒展开参数
            const taylorValidation = this.validateTaylorParameters();
            if (!taylorValidation.valid) {
                this.addLog(`参数错误: ${taylorValidation.message}`, 'error');
                return;
            }

            // 验证微分展示参数
            const differentiationValidation = this.validateDifferentiationParameters();
            if (!differentiationValidation.valid) {
                this.addLog(`参数错误: ${differentiationValidation.message}`, 'error');
                return;
            }

            // 验证积分展示参数
            const integrationValidation = this.validateIntegrationParameters();
            if (!integrationValidation.valid) {
                this.addLog(`参数错误: ${integrationValidation.message}`, 'error');
                return;
            }

            // 收集配置数据
            const config = {
                scene_type: this.currentScene,
                input_type: this.currentInputType,
                functions: this.selectedFunctions,
                parameters: {
                    function_expression: functionExpression,
                    x_range: document.getElementById('x-range').value,
                    y_range: document.getElementById('y-range').value,
                    resolution: document.getElementById('resolution').value,
                    color_scheme: document.getElementById('color-scheme').value,
                    stroke_width: document.getElementById('stroke-width').value,
                    animation_style: document.getElementById('animation-style').value
                }
            };

            // 如果选择了泰勒展开，添加相关参数
            if (this.selectedFunctions.includes('taylor')) {
                config.parameters.taylor_expansion = {
                    expansion_point: taylorValidation.taylorPoint,
                    max_order: taylorValidation.maxOrder,
                    animation_steps: true
                };
                this.addLog(`泰勒展开配置: 函数 ${taylorValidation.functionExpression} 在 x=${taylorValidation.taylorPoint} 处展开，最高 ${taylorValidation.maxOrder} 阶`, 'info');
            }

            // 如果选择了微分展示，添加相关参数
            if (this.selectedFunctions.includes('differentiation')) {
                config.parameters.differentiation = {
                    fit_point: differentiationValidation.fitPoint,
                    radius: differentiationValidation.radius
                };
                this.addLog(`微分展示配置: 函数 ${differentiationValidation.functionExpression} 在 x=${differentiationValidation.fitPoint} 处求导，拟合半径 ${differentiationValidation.radius}`, 'info');
            }

            // 如果选择了积分展示，添加相关参数
            if (this.selectedFunctions.includes('integration')) {
                config.parameters.integration = {
                    lower_bound: integrationValidation.lowerBound,
                    upper_bound: integrationValidation.upperBound
                };
                this.addLog(`积分展示配置: 函数 ${integrationValidation.functionExpression} 在 [${integrationValidation.lowerBound}, ${integrationValidation.upperBound}] 区间积分`, 'info');
            }

            // 发送创作请求
            const response = await fetch('/api/start_creation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.addLog(`创作完成: ${result.message}`, 'success');
                this.addLog(`数据已发送到后端处理`, 'info');
                
            } else if (result.status === 'processing') {
                if (this.selectedFunctions.includes('taylor')) {
                    this.addLog('泰勒展开动画正在生成中，请稍候...', 'info');
                } else if (this.selectedFunctions.includes('plot')) {
                    this.addLog('函数图像正在生成中，请稍候...', 'info');
                } else if (this.selectedFunctions.includes('differentiation')) {
                    this.addLog('微分展示动画正在生成中，请稍候...', 'info');
                } else if (this.selectedFunctions.includes('integration')) {
                    this.addLog('积分展示动画正在生成中，请稍候...', 'info');
                }
                this.startTaskChecking(result.task_id);
                
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            this.addLog(`创作失败: ${error.message}`, 'error');
        }
    }

    resetConfig() {
        // 重置功能选择
        document.querySelectorAll('.function-checkbox input').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.selectedFunctions = [];
        
        // 重置输入字段        
        document.getElementById('function-input').value = '';
        document.getElementById('x-range').value = '-10,10';
        document.getElementById('y-range').value = '-10,10';
        document.getElementById('resolution').value = '100';
        document.getElementById('color-scheme').value = 'yellow';
        document.getElementById('stroke-width').value = '4';
        document.getElementById('animation-style').value = 'none';
        document.getElementById('taylor-point').value = '';
        document.getElementById('max-order').value = '10';
        document.getElementById('fit-point').value = '';
        document.getElementById('radius').value = '';
        document.getElementById('lower-bound').value = '';
        document.getElementById('upper-bound').value = '';
        
        // 停止任务检查
        this.stopTaskChecking();
        
        // 隐藏所有参数
        this.toggleTaylorParameters(false);
        this.toggleDifferentiationParameters(false);
        this.toggleIntegrationParameters(false);
        
        this.addLog('配置已重置', 'info');
    }

    updateDisplay() {
        const sceneText = this.currentScene === '2D' ? '2维场景' : '3维场景';
        const inputText = this.currentInputType === 'explicit' ? '显函数输入' : '隐函数输入';
        document.getElementById('current-scene-title').textContent = `${sceneText} - ${inputText}`;
    }

    updateTimestamp() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-CN');
        document.getElementById('last-update').textContent = timeString;
    }

    addLog(message, type = 'info') {
        const logOutput = document.getElementById('log-output');
        const time = new Date().toLocaleTimeString('zh-CN');
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logOutput.appendChild(logEntry);
        logOutput.scrollTop = logOutput.scrollHeight;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new VisualizationApp();
});