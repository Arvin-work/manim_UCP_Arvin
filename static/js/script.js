class VisualizationApp {
    constructor() {
        this.currentScene = '2D';
        this.currentInputType = 'explicit';
        this.selectedFunctions = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateDisplay();
        this.updateTimestamp();
        
        // 每秒更新一次时间戳
        setInterval(() => this.updateTimestamp(), 1000);
    }

    bindEvents() {
        // 场景切换
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchScene(e.target.closest('.tab-button').dataset.scene);
            });
        });

        // 输入类型切换
        document.querySelectorAll('.input-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchInputType(e.target.closest('.input-tab').dataset.inputType);
            });
        });

        // 功能选择
        document.querySelectorAll('.function-checkbox input').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleFunction(e.target.value, e.target.checked);
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

    async switchScene(sceneType) {
        try {
            // 更新UI
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-scene="${sceneType}"]`).classList.add('active');
            
            this.currentScene = sceneType;
            
            // 发送API请求
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
            // 更新UI
            document.querySelectorAll('.input-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`[data-input-type="${inputType}"]`).classList.add('active');
            
            this.currentInputType = inputType;
            
            // 发送API请求
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

    toggleFunction(func, isSelected) {
        if (isSelected) {
            this.selectedFunctions.push(func);
        } else {
            this.selectedFunctions = this.selectedFunctions.filter(f => f !== func);
        }
        
        this.addLog(`${this.getFunctionName(func)} ${isSelected ? '已选择' : '已取消'}`, 'info');
    }

    getFunctionName(func) {
        const names = {
            'plot': '单纯画图',
            'differentiation': '微分展示',
            'integration': '积分展示',
            'animation': '动画效果',
            'transformation': '变换展示'
        };
        return names[func] || func;
    }

    async startCreation() {
        try {
            this.addLog('开始处理可视化请求...', 'info');

            // 收集配置数据
            const config = {
                scene_type: this.currentScene,
                input_type: this.currentInputType,
                functions: this.selectedFunctions,
                parameters: {
                    function_expression: document.getElementById('function-input').value,
                    x_range: document.getElementById('x-range').value,
                    y_range: document.getElementById('y-range').value,
                    resolution: document.getElementById('resolution').value,
                    color_scheme: document.getElementById('color-scheme').value
                }
            };

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
        document.getElementById('color-scheme').value = 'default';
        
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