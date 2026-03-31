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
                
                const unsupportedInImplicit = ['taylor', 'integration'];
                const unsupportedInPolar = ['taylor', 'integration', 'differentiation'];
                const funcNames = {
                    'taylor': '泰勒展开',
                    'integration': '积分展示',
                    'differentiation': '微分展示'
                };
                
                if (isSelected && this.currentInputType === 'implicit' && unsupportedInImplicit.includes(func)) {
                    e.target.checked = false;
                    this.addLog(`⚠️ 隐函数模式不支持 "${funcNames[func]}" 功能`, 'warning');
                    this.addLog('隐函数模式仅支持: 单纯画图、微分展示', 'warning');
                    return;
                }
                
                if (isSelected && this.currentInputType === 'polar' && unsupportedInPolar.includes(func)) {
                    e.target.checked = false;
                    this.addLog(`⚠️ 极坐标模式不支持 "${funcNames[func]}" 功能`, 'warning');
                    this.addLog('极坐标模式仅支持: 单纯画图', 'warning');
                    return;
                }
                
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
        
        // 参数方程模式切换
        document.querySelectorAll('input[name="parametric-mode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.switchParametricMode(e.target.value);
            });
        });
    }
    
    switchParametricMode(mode) {
        const curveInputs = document.getElementById('parametric-curve-inputs');
        const surfaceInputs = document.getElementById('parametric-surface-inputs');
        const tRangeGroup = document.getElementById('param-t-range-group');
        const uRangeGroup = document.getElementById('param-u-range-group');
        const vRangeGroup = document.getElementById('param-v-range-group');
        
        if (mode === 'curve') {
            curveInputs.style.display = 'block';
            surfaceInputs.style.display = 'none';
            tRangeGroup.style.display = 'block';
            uRangeGroup.style.display = 'none';
            vRangeGroup.style.display = 'none';
            this.addLog('已切换到参数曲线模式', 'info');
        } else {
            curveInputs.style.display = 'none';
            surfaceInputs.style.display = 'block';
            tRangeGroup.style.display = 'none';
            uRangeGroup.style.display = 'block';
            vRangeGroup.style.display = 'block';
            this.addLog('已切换到参数曲面模式', 'info');
        }
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
            
            if (this.currentScene === '3D') {
                this.toggle3DDifferentiationParameters(true);
            }
            
            this.addLog('微分展示功能已启用，请输入拟合点和拟合半径', 'info');
        } else {
            fitPointGroup.style.display = 'none';
            radiusGroup.style.display = 'none';
            this.toggle3DDifferentiationParameters(false);
        }
    }
    
    toggle3DDifferentiationParameters(show) {
        const verifyPointGroup = document.getElementById('3d-diff-verify-point-group');
        const tParamGroup = document.getElementById('3d-diff-t-param-group');
        const animDurationGroup = document.getElementById('3d-diff-animation-duration-group');
        const tangentScaleGroup = document.getElementById('3d-diff-tangent-scale-group');
        const coordDisplayPanel = document.getElementById('3d-coord-display-panel');
        
        if (show && this.currentScene === '3D') {
            verifyPointGroup.style.display = 'block';
            tParamGroup.style.display = 'block';
            animDurationGroup.style.display = 'block';
            tangentScaleGroup.style.display = 'block';
            coordDisplayPanel.style.display = 'block';
            this.addLog('三维微分展示已启用，可验证点坐标并显示切线向量', 'info');
            
            this.bind3DDifferentiationEvents();
        } else {
            verifyPointGroup.style.display = 'none';
            tParamGroup.style.display = 'none';
            animDurationGroup.style.display = 'none';
            tangentScaleGroup.style.display = 'none';
            coordDisplayPanel.style.display = 'none';
        }
    }
    
    bind3DDifferentiationEvents() {
        const verifyPointInput = document.getElementById('3d-diff-verify-point');
        const tParamInput = document.getElementById('3d-diff-t-param');
        
        if (verifyPointInput && !verifyPointInput.hasAttribute('data-bound')) {
            verifyPointInput.setAttribute('data-bound', 'true');
            verifyPointInput.addEventListener('input', () => {
                this.validate3DPoint();
            });
        }
        
        if (tParamInput && !tParamInput.hasAttribute('data-bound')) {
            tParamInput.setAttribute('data-bound', 'true');
            tParamInput.addEventListener('input', () => {
                this.update3DCurvePoint();
            });
        }
    }
    
    async validate3DPoint() {
        const verifyPointInput = document.getElementById('3d-diff-verify-point').value;
        const statusElement = document.getElementById('3d-verify-status');
        const verifyCoordElement = document.getElementById('3d-verify-coord');
        
        if (!verifyPointInput.trim()) {
            statusElement.textContent = '等待输入';
            statusElement.className = 'coord-status waiting';
            verifyCoordElement.textContent = '--';
            return;
        }
        
        try {
            const coords = verifyPointInput.split(',').map(c => parseFloat(c.trim()));
            if (coords.length !== 3 || coords.some(isNaN)) {
                statusElement.textContent = '格式错误';
                statusElement.className = 'coord-status invalid';
                verifyCoordElement.textContent = verifyPointInput;
                return;
            }
            
            verifyCoordElement.textContent = `(${coords[0].toFixed(2)}, ${coords[1].toFixed(2)}, ${coords[2].toFixed(2)})`;
            
            const parametricData = this.getParametricData();
            if (parametricData && parametricData.mode === 'curve') {
                const response = await fetch('/api/validate_3d_point', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        point: coords,
                        parametric: parametricData
                    })
                });
                
                const result = await response.json();
                
                if (result.valid) {
                    statusElement.textContent = '验证通过 ✓';
                    statusElement.className = 'coord-status valid';
                    document.getElementById('3d-curve-coord').textContent = 
                        `(${result.curve_point[0].toFixed(2)}, ${result.curve_point[1].toFixed(2)}, ${result.curve_point[2].toFixed(2)})`;
                    document.getElementById('3d-tangent-vector').textContent = 
                        `(${result.tangent[0].toFixed(2)}, ${result.tangent[1].toFixed(2)}, ${result.tangent[2].toFixed(2)})`;
                } else {
                    statusElement.textContent = '点不在曲线上';
                    statusElement.className = 'coord-status invalid';
                }
            } else {
                statusElement.textContent = '请先输入参数曲线';
                statusElement.className = 'coord-status waiting';
            }
        } catch (error) {
            statusElement.textContent = '验证失败';
            statusElement.className = 'coord-status invalid';
        }
    }
    
    async update3DCurvePoint() {
        const tParam = document.getElementById('3d-diff-t-param').value;
        const curveCoordElement = document.getElementById('3d-curve-coord');
        const tangentElement = document.getElementById('3d-tangent-vector');
        
        if (!tParam.trim()) {
            curveCoordElement.textContent = '--';
            tangentElement.textContent = '--';
            return;
        }
        
        try {
            const t = parseFloat(tParam);
            if (isNaN(t)) {
                curveCoordElement.textContent = '无效参数';
                return;
            }
            
            const parametricData = this.getParametricData();
            if (parametricData && parametricData.mode === 'curve') {
                const response = await fetch('/api/get_curve_point', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        t: t,
                        parametric: parametricData
                    })
                });
                
                const result = await response.json();
                
                if (result.point) {
                    curveCoordElement.textContent = 
                        `(${result.point[0].toFixed(2)}, ${result.point[1].toFixed(2)}, ${result.point[2].toFixed(2)})`;
                    tangentElement.textContent = 
                        `(${result.tangent[0].toFixed(2)}, ${result.tangent[1].toFixed(2)}, ${result.tangent[2].toFixed(2)})`;
                }
            }
        } catch (error) {
            curveCoordElement.textContent = '计算错误';
        }
    }
    
    getParametricData() {
        const mode = document.querySelector('input[name="parametric-mode"]:checked');
        if (!mode) return null;
        
        const modeValue = mode.value;
        
        if (modeValue === 'curve') {
            return {
                mode: 'curve',
                x_expr: document.getElementById('param-x-t').value,
                y_expr: document.getElementById('param-y-t').value,
                z_expr: document.getElementById('param-z-t').value,
                t_range: document.getElementById('param-t-range').value
            };
        } else {
            return {
                mode: 'surface',
                x_expr: document.getElementById('param-x-uv').value,
                y_expr: document.getElementById('param-y-uv').value,
                z_expr: document.getElementById('param-z-uv').value,
                u_range: document.getElementById('param-u-range').value,
                v_range: document.getElementById('param-v-range').value
            };
        }
    }

    toggleIntegrationParameters(show) {
        const lowerBoundGroup = document.getElementById('lower-bound-group');
        const upperBoundGroup = document.getElementById('upper-bound-group');
        const subdivisionsGroup = document.getElementById('3d-integration-subdivisions-group');
        const durationGroup = document.getElementById('3d-integration-duration-group');
        const progressionGroup = document.getElementById('3d-integration-progression-group');
        const volumeGroup = document.getElementById('3d-integration-volume-group');
        
        if (show) {
            if (this.currentScene === '3D') {
                subdivisionsGroup.style.display = 'block';
                durationGroup.style.display = 'block';
                progressionGroup.style.display = 'block';
                volumeGroup.style.display = 'block';
                lowerBoundGroup.style.display = 'none';
                upperBoundGroup.style.display = 'none';
                this.addLog('三维黎曼积分功能已启用，请调整细分程度', 'info');
                this.initIntegrationSlider();
            } else {
                lowerBoundGroup.style.display = 'block';
                upperBoundGroup.style.display = 'block';
                subdivisionsGroup.style.display = 'none';
                durationGroup.style.display = 'none';
                progressionGroup.style.display = 'none';
                volumeGroup.style.display = 'none';
                this.addLog('积分展示功能已启用，请输入积分上下限', 'info');
            }
        } else {
            lowerBoundGroup.style.display = 'none';
            upperBoundGroup.style.display = 'none';
            subdivisionsGroup.style.display = 'none';
            durationGroup.style.display = 'none';
            progressionGroup.style.display = 'none';
            volumeGroup.style.display = 'none';
        }
    }
    
    initIntegrationSlider() {
        const slider = document.getElementById('3d-integration-subdivisions');
        const valueDisplay = document.getElementById('3d-integration-subdivisions-value');
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                const value = e.target.value;
                valueDisplay.textContent = `${value}×${value}`;
            });
        }
    }

    toggle3DParameters(show) {
        const zRangeGroup = document.getElementById('z-range-group');
        const plotTypeGroup = document.getElementById('plot-type-group');
        const cameraPhiGroup = document.getElementById('camera-phi-group');
        const cameraThetaGroup = document.getElementById('camera-theta-group');
        const cameraPresetGroup = document.getElementById('camera-preset-group');
        const cameraSaveGroup = document.getElementById('camera-save-group');
        
        if (show) {
            zRangeGroup.style.display = 'block';
            plotTypeGroup.style.display = 'block';
            cameraPhiGroup.style.display = 'block';
            cameraThetaGroup.style.display = 'block';
            cameraPresetGroup.style.display = 'block';
            cameraSaveGroup.style.display = 'block';
            this.addLog('三维场景功能已启用，请选择绘制类型和Z轴范围', 'info');
            this.initCameraControls();
            this.loadCameraPresets();
        } else {
            zRangeGroup.style.display = 'none';
            plotTypeGroup.style.display = 'none';
            cameraPhiGroup.style.display = 'none';
            cameraThetaGroup.style.display = 'none';
            cameraPresetGroup.style.display = 'none';
            cameraSaveGroup.style.display = 'none';
        }
    }
    
    initCameraControls() {
        const phiSlider = document.getElementById('camera-phi');
        const phiInput = document.getElementById('camera-phi-value');
        const thetaSlider = document.getElementById('camera-theta');
        const thetaInput = document.getElementById('camera-theta-value');
        
        if (phiSlider && phiInput) {
            phiSlider.addEventListener('input', (e) => {
                phiInput.value = e.target.value;
            });
            phiInput.addEventListener('input', (e) => {
                let value = parseFloat(e.target.value);
                if (isNaN(value)) value = 45;
                if (value < 0) value = 0;
                if (value > 90) value = 90;
                phiSlider.value = value;
                e.target.value = value;
            });
        }
        
        if (thetaSlider && thetaInput) {
            thetaSlider.addEventListener('input', (e) => {
                thetaInput.value = e.target.value;
            });
            thetaInput.addEventListener('input', (e) => {
                let value = parseFloat(e.target.value);
                if (isNaN(value)) value = -45;
                if (value < -180) value = -180;
                if (value > 180) value = 180;
                thetaSlider.value = value;
                e.target.value = value;
            });
        }
        
        const applyPresetBtn = document.getElementById('apply-preset-btn');
        if (applyPresetBtn) {
            applyPresetBtn.addEventListener('click', () => {
                this.applyCameraPreset();
            });
        }
        
        const savePresetBtn = document.getElementById('save-camera-preset-btn');
        if (savePresetBtn) {
            savePresetBtn.addEventListener('click', () => {
                this.saveCameraPreset();
            });
        }
    }
    
    applyCameraPreset() {
        const presetSelect = document.getElementById('camera-preset');
        const preset = presetSelect.value;
        
        const presets = {
            'default': { phi: 45, theta: -45 },
            'top': { phi: 90, theta: 0 },
            'front': { phi: 0, theta: 0 },
            'side': { phi: 0, theta: 90 },
            'isometric': { phi: 54.7, theta: 45 }
        };
        
        if (presets[preset]) {
            const phiSlider = document.getElementById('camera-phi');
            const phiInput = document.getElementById('camera-phi-value');
            const thetaSlider = document.getElementById('camera-theta');
            const thetaInput = document.getElementById('camera-theta-value');
            
            phiSlider.value = presets[preset].phi;
            phiInput.value = presets[preset].phi;
            thetaSlider.value = presets[preset].theta;
            thetaInput.value = presets[preset].theta;
            
            this.addLog(`已应用预设视角: φ=${presets[preset].phi}°, θ=${presets[preset].theta}°`, 'info');
        }
    }
    
    saveCameraPreset() {
        const nameInput = document.getElementById('camera-preset-name');
        const name = nameInput.value.trim();
        
        if (!name) {
            this.addLog('请输入预设名称', 'error');
            return;
        }
        
        const phi = parseFloat(document.getElementById('camera-phi').value);
        const theta = parseFloat(document.getElementById('camera-theta').value);
        
        let presets = JSON.parse(localStorage.getItem('cameraPresets') || '[]');
        
        const existingIndex = presets.findIndex(p => p.name === name);
        if (existingIndex >= 0) {
            presets[existingIndex] = { name, phi, theta };
            this.addLog(`预设 "${name}" 已更新`, 'success');
        } else {
            presets.push({ name, phi, theta });
            this.addLog(`预设 "${name}" 已保存`, 'success');
        }
        
        localStorage.setItem('cameraPresets', JSON.stringify(presets));
        nameInput.value = '';
        this.loadCameraPresets();
    }
    
    loadCameraPresets() {
        const presetsList = document.getElementById('camera-presets-list');
        const presets = JSON.parse(localStorage.getItem('cameraPresets') || '[]');
        
        presetsList.innerHTML = '';
        
        if (presets.length === 0) {
            presetsList.innerHTML = '<div class="no-presets-hint" style="color: #6c757d; font-size: 0.85em; padding: 10px;">暂无自定义预设</div>';
            return;
        }
        
        presets.forEach((preset, index) => {
            const item = document.createElement('div');
            item.className = 'camera-preset-item';
            item.innerHTML = `
                <div>
                    <div class="camera-preset-item-name">${preset.name}</div>
                    <div class="camera-preset-item-values">φ=${preset.phi}°, θ=${preset.theta}°</div>
                </div>
                <div class="camera-preset-item-actions">
                    <button type="button" class="btn-load-preset" data-index="${index}">加载</button>
                    <button type="button" class="btn-delete-preset" data-index="${index}">删除</button>
                </div>
            `;
            presetsList.appendChild(item);
        });
        
        presetsList.querySelectorAll('.btn-load-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.loadCameraPresetByIndex(index);
            });
        });
        
        presetsList.querySelectorAll('.btn-delete-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.deleteCameraPresetByIndex(index);
            });
        });
    }
    
    loadCameraPresetByIndex(index) {
        const presets = JSON.parse(localStorage.getItem('cameraPresets') || '[]');
        if (presets[index]) {
            const preset = presets[index];
            document.getElementById('camera-phi').value = preset.phi;
            document.getElementById('camera-phi-value').value = preset.phi;
            document.getElementById('camera-theta').value = preset.theta;
            document.getElementById('camera-theta-value').value = preset.theta;
            this.addLog(`已加载预设 "${preset.name}"`, 'info');
        }
    }
    
    deleteCameraPresetByIndex(index) {
        let presets = JSON.parse(localStorage.getItem('cameraPresets') || '[]');
        const name = presets[index]?.name || '未知';
        presets.splice(index, 1);
        localStorage.setItem('cameraPresets', JSON.stringify(presets));
        this.addLog(`预设 "${name}" 已删除`, 'info');
        this.loadCameraPresets();
    }
    
    getCameraParameters() {
        const phi = parseFloat(document.getElementById('camera-phi')?.value) || 45;
        const theta = parseFloat(document.getElementById('camera-theta')?.value) || -45;
        return { phi, theta };
    }

    async switchScene(sceneType) {
        try {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-scene="${sceneType}"]`).classList.add('active');
            
            this.currentScene = sceneType;
            
            if (sceneType === '3D') {
                this.toggle3DParameters(true);
                if (this.selectedFunctions.includes('differentiation')) {
                    this.toggle3DDifferentiationParameters(true);
                }
            } else {
                this.toggle3DParameters(false);
                this.toggle3DDifferentiationParameters(false);
            }
            
            if (this.selectedFunctions.includes('integration')) {
                this.toggleIntegrationParameters(true);
            }
            
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
                const inputTypeNames = {
                    'explicit': '显函数',
                    'implicit': '隐函数',
                    'polar': '极坐标',
                    'parametric': '参数方程'
                };
                this.addLog(`切换到${inputTypeNames[inputType]}输入`, 'success');
                
                if (inputType === 'implicit') {
                    this.addLog('⚠️ 隐函数模式仅支持: 单纯画图、微分展示', 'warning');
                    this.checkImplicitFunctionSupport();
                }
                
                if (inputType === 'polar') {
                    this.addLog('⚠️ 极坐标模式仅支持: 单纯画图', 'warning');
                    this.checkPolarFunctionSupport();
                }
                
                if (inputType === 'parametric') {
                    this.addLog('⚠️ 参数方程模式仅支持: 单纯画图', 'warning');
                    this.checkParametricFunctionSupport();
                }
                
                this.updateDisplay();
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            this.addLog(`输入类型切换失败: ${error.message}`, 'error');
        }
    }
    
    checkParametricFunctionSupport() {
        const unsupportedFunctions = ['taylor', 'integration', 'differentiation'];
        const funcNames = {
            'taylor': '泰勒展开',
            'integration': '积分展示',
            'differentiation': '微分展示'
        };
        
        for (const func of unsupportedFunctions) {
            if (this.selectedFunctions.includes(func)) {
                this.addLog(`⚠️ 参数方程模式不支持 "${funcNames[func]}" 功能，已自动取消`, 'warning');
                
                const checkbox = document.querySelector(`input[value="${func}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                }
                
                this.selectedFunctions = this.selectedFunctions.filter(f => f !== func);
                
                if (func === 'taylor') {
                    this.toggleTaylorParameters(false);
                } else if (func === 'integration') {
                    this.toggleIntegrationParameters(false);
                } else if (func === 'differentiation') {
                    this.toggleDifferentiationParameters(false);
                }
            }
        }
    }
    
    checkImplicitFunctionSupport() {
        const unsupportedFunctions = ['taylor', 'integration'];
        const funcNames = {
            'taylor': '泰勒展开',
            'integration': '积分展示'
        };
        
        for (const func of unsupportedFunctions) {
            if (this.selectedFunctions.includes(func)) {
                this.addLog(`⚠️ 隐函数模式不支持 "${funcNames[func]}" 功能，已自动取消`, 'warning');
                
                const checkbox = document.querySelector(`input[value="${func}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                }
                
                this.selectedFunctions = this.selectedFunctions.filter(f => f !== func);
                
                if (func === 'taylor') {
                    this.toggleTaylorParameters(false);
                } else if (func === 'integration') {
                    this.toggleIntegrationParameters(false);
                }
            }
        }
    }
    
    checkPolarFunctionSupport() {
        const unsupportedFunctions = ['taylor', 'integration', 'differentiation'];
        const funcNames = {
            'taylor': '泰勒展开',
            'integration': '积分展示',
            'differentiation': '微分展示'
        };
        
        for (const func of unsupportedFunctions) {
            if (this.selectedFunctions.includes(func)) {
                this.addLog(`⚠️ 极坐标模式不支持 "${funcNames[func]}" 功能，已自动取消`, 'warning');
                
                const checkbox = document.querySelector(`input[value="${func}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                }
                
                this.selectedFunctions = this.selectedFunctions.filter(f => f !== func);
                
                if (func === 'taylor') {
                    this.toggleTaylorParameters(false);
                } else if (func === 'integration') {
                    this.toggleIntegrationParameters(false);
                } else if (func === 'differentiation') {
                    this.toggleDifferentiationParameters(false);
                }
            }
        }
    }
    
    togglePolarParameters(show) {
        const polarRadiusMaxGroup = document.getElementById('polar-radius-max-group');
        const polarAzimuthStepGroup = document.getElementById('polar-azimuth-step-group');
        const polarRadiusStepGroup = document.getElementById('polar-radius-step-group');
        const polarThetaRangeGroup = document.getElementById('polar-theta-range-group');
        
        if (show) {
            polarRadiusMaxGroup.style.display = 'block';
            polarAzimuthStepGroup.style.display = 'block';
            polarRadiusStepGroup.style.display = 'block';
            polarThetaRangeGroup.style.display = 'block';
            this.addLog('极坐标参数已启用', 'info');
        } else {
            polarRadiusMaxGroup.style.display = 'none';
            polarAzimuthStepGroup.style.display = 'none';
            polarRadiusStepGroup.style.display = 'none';
            polarThetaRangeGroup.style.display = 'none';
        }
    }

    async switchScene(sceneType) {
        try {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-scene="${sceneType}"]`).classList.add('active');
            
            this.currentScene = sceneType;
            
            if (sceneType === '3D') {
                this.toggle3DParameters(true);
                if (this.selectedFunctions.includes('differentiation')) {
                    this.toggle3DDifferentiationParameters(true);
                }
            } else {
                this.toggle3DParameters(false);
                this.toggle3DDifferentiationParameters(false);
            }
            
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

    getFunctionName(func) {
        const names = {
            'plot': '单纯画图',
            'differentiation': '微分展示',
            'integration': '积分展示',
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

        if (this.currentScene === '3D' && this.currentInputType === 'parametric') {
            const parametricData = this.getParametricData();
            if (!parametricData || parametricData.mode !== 'curve') {
                return {
                    valid: false,
                    message: '三维微分展示仅支持参数曲线模式'
                };
            }
            
            if (!parametricData.x_expr || !parametricData.y_expr || !parametricData.z_expr) {
                return {
                    valid: false,
                    message: '请填写完整的参数曲线方程'
                };
            }
            
            const tParam = document.getElementById('3d-diff-t-param').value;
            const animDuration = document.getElementById('3d-diff-animation-duration').value;
            const tangentScale = document.getElementById('3d-diff-tangent-scale').value;
            
            return {
                valid: true,
                is3D: true,
                parametric: parametricData,
                tParam: tParam ? parseFloat(tParam) : null,
                animationDuration: animDuration ? parseFloat(animDuration) : 5,
                tangentScale: tangentScale ? parseFloat(tangentScale) : 1,
                functionExpression: `x(t)=${parametricData.x_expr}, y(t)=${parametricData.y_expr}, z(t)=${parametricData.z_expr}`
            };
        }

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

        const functionExpression = document.getElementById('function-input').value;

        if (!functionExpression.trim()) {
            return { 
                valid: false, 
                message: '请填写函数表达式' 
            };
        }

        if (this.currentScene === '3D') {
            const subdivisions = document.getElementById('3d-integration-subdivisions').value;
            const duration = document.getElementById('3d-integration-duration').value;
            const progression = document.getElementById('3d-integration-progression').checked;
            
            if (!subdivisions || isNaN(parseInt(subdivisions)) || parseInt(subdivisions) < 4) {
                return {
                    valid: false,
                    message: '细分程度必须至少为4'
                };
            }
            
            if (!duration || isNaN(parseFloat(duration)) || parseFloat(duration) <= 0) {
                return {
                    valid: false,
                    message: '动画时长必须是正数'
                };
            }
            
            return { 
                valid: true, 
                subdivisions: parseInt(subdivisions),
                animationDuration: parseFloat(duration),
                showProgression: progression,
                functionExpression: functionExpression
            };
        }

        const lowerBound = document.getElementById('lower-bound').value;
        const upperBound = document.getElementById('upper-bound').value;

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
                this.addLog('请选择输入类型', 'error');
                return;
            }

            // 验证功能选项是否已选择
            if (this.selectedFunctions.length === 0) {
                this.addLog('请至少选择一个功能选项', 'error');
                return;
            }

            // 根据输入类型验证不同的参数
            let functionExpression = '';
            let polarR = '';
            let polarPhi = '';
            let parametricData = null;
            
            if (this.currentInputType === 'polar') {
                // 极坐标模式验证
                polarR = document.getElementById('polar-r-input').value;
                if (!polarR.trim()) {
                    this.addLog('请填写极坐标方程 r(θ)', 'error');
                    return;
                }
                
                if (this.currentScene === '3D') {
                    polarPhi = document.getElementById('polar-phi-input').value;
                }
            } else if (this.currentInputType === 'parametric') {
                // 参数方程模式验证
                const mode = document.querySelector('input[name="parametric-mode"]:checked').value;
                
                if (mode === 'curve') {
                    const xT = document.getElementById('param-x-t').value.trim();
                    const yT = document.getElementById('param-y-t').value.trim();
                    
                    if (this.currentScene === '3D') {
                        const zT = document.getElementById('param-z-t').value.trim();
                        if (!xT || !yT || !zT) {
                            this.addLog('请填写完整的参数曲线方程 x(t), y(t), z(t)', 'error');
                            return;
                        }
                        parametricData = {
                            mode: 'curve',
                            x_expr: xT,
                            y_expr: yT,
                            z_expr: zT,
                            t_range: document.getElementById('param-t-range').value
                        };
                    } else {
                        if (!xT || !yT) {
                            this.addLog('请填写完整的参数曲线方程 x(t), y(t)', 'error');
                            return;
                        }
                        parametricData = {
                            mode: 'curve',
                            x_expr: xT,
                            y_expr: yT,
                            t_range: document.getElementById('param-t-range').value
                        };
                    }
                } else {
                    const xUV = document.getElementById('param-x-uv').value.trim();
                    const yUV = document.getElementById('param-y-uv').value.trim();
                    const zUV = document.getElementById('param-z-uv').value.trim();
                    
                    if (!xUV || !yUV || !zUV) {
                        this.addLog('请填写完整的参数曲面方程 x(u,v), y(u,v), z(u,v)', 'error');
                        return;
                    }
                    
                    parametricData = {
                        mode: 'surface',
                        x_expr: xUV,
                        y_expr: yUV,
                        z_expr: zUV,
                        u_range: document.getElementById('param-u-range').value,
                        v_range: document.getElementById('param-v-range').value
                    };
                }
            } else {
                // 显函数/隐函数模式验证
                functionExpression = document.getElementById('function-input').value;
                if (!functionExpression.trim()) {
                    this.addLog('请填写函数表达式', 'error');
                    return;
                }
            }

            // 如果是三维场景，验证Z轴范围
            if (this.currentScene === '3D') {
                const zRange = document.getElementById('z-range').value;
                if (!zRange.trim()) {
                    this.addLog('请填写Z轴范围', 'error');
                    return;
                }
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
            
            // 极坐标参数
            if (this.currentInputType === 'polar') {
                config.parameters.polar = {
                    r_expression: polarR,
                    phi_expression: polarPhi,
                    radius_max: parseFloat(document.getElementById('polar-radius-max').value) || 4,
                    azimuth_step: parseFloat(document.getElementById('polar-azimuth-step').value) || 30,
                    radius_step: parseFloat(document.getElementById('polar-radius-step').value) || 1,
                    theta_range: document.getElementById('polar-theta-range').value
                };
                this.addLog(`极坐标配置: r = ${polarR}`, 'info');
            }
            
            // 参数方程参数
            if (this.currentInputType === 'parametric' && parametricData) {
                config.parameters.parametric = parametricData;
                if (parametricData.mode === 'curve') {
                    if (this.currentScene === '3D') {
                        this.addLog(`参数曲线配置: x(t)=${parametricData.x_expr}, y(t)=${parametricData.y_expr}, z(t)=${parametricData.z_expr}`, 'info');
                    } else {
                        this.addLog(`参数曲线配置: x(t)=${parametricData.x_expr}, y(t)=${parametricData.y_expr}`, 'info');
                    }
                } else {
                    this.addLog(`参数曲面配置: x(u,v)=${parametricData.x_expr}, y(u,v)=${parametricData.y_expr}, z(u,v)=${parametricData.z_expr}`, 'info');
                }
            }

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
                if (differentiationValidation.is3D) {
                    config.parameters.differentiation = {
                        is_3d: true,
                        parametric: differentiationValidation.parametric,
                        t_param: differentiationValidation.tParam,
                        animation_duration: differentiationValidation.animationDuration,
                        tangent_scale: differentiationValidation.tangentScale
                    };
                    this.addLog(`三维微分展示配置: ${differentiationValidation.functionExpression}`, 'info');
                } else {
                    config.parameters.differentiation = {
                        fit_point: differentiationValidation.fitPoint,
                        radius: differentiationValidation.radius
                    };
                    this.addLog(`微分展示配置: 函数 ${differentiationValidation.functionExpression} 在 x=${differentiationValidation.fitPoint} 处求导，拟合半径 ${differentiationValidation.radius}`, 'info');
                }
            }

            // 如果选择了积分展示，添加相关参数
            if (this.selectedFunctions.includes('integration')) {
                if (this.currentScene === '3D') {
                    config.parameters.integration = {
                        subdivisions: integrationValidation.subdivisions,
                        animation_duration: integrationValidation.animationDuration,
                        show_progression: integrationValidation.showProgression
                    };
                    this.addLog(`三维黎曼积分配置: 函数 ${integrationValidation.functionExpression}, 细分 ${integrationValidation.subdivisions}×${integrationValidation.subdivisions}`, 'info');
                } else {
                    config.parameters.integration = {
                        lower_bound: integrationValidation.lowerBound,
                        upper_bound: integrationValidation.upperBound
                    };
                    this.addLog(`积分展示配置: 函数 ${integrationValidation.functionExpression} 在 [${integrationValidation.lowerBound}, ${integrationValidation.upperBound}] 区间积分`, 'info');
                }
            }

            // 如果是三维场景，添加Z轴范围
            if (this.currentScene === '3D') {
                config.parameters.z_range = document.getElementById('z-range').value;
                config.parameters.plot_type = document.getElementById('plot-type').value;
                
                const cameraParams = this.getCameraParameters();
                config.parameters.camera = {
                    phi: cameraParams.phi,
                    theta: cameraParams.theta
                };
            }

            // 在任务状态检查中添加三维场景

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
                } else if (this.selectedFunctions.includes('plot') && this.currentScene === '3D') {
                    this.addLog('三维场景绘制中，请稍候...', 'info');
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
        const inputTypeNames = {
            'explicit': '显函数输入',
            'implicit': '隐函数输入',
            'polar': '极坐标输入',
            'parametric': '参数方程'
        };
        const inputText = inputTypeNames[this.currentInputType];
        document.getElementById('current-scene-title').textContent = `${sceneText} - ${inputText}`;
        
        // 显示/隐藏参数方程选项卡（二维和三维模式都支持）
        const parametricTab = document.getElementById('parametric-tab');
        parametricTab.style.display = 'flex';
        
        // 根据场景类型调整参数方程输入界面
        const paramZRow = document.getElementById('param-z-t-row');
        const paramSurfaceRadio = document.getElementById('parametric-surface-radio');
        const paramSurfaceInputs = document.getElementById('parametric-surface-inputs');
        
        if (this.currentScene === '3D') {
            paramZRow.style.display = 'flex';
            paramSurfaceRadio.style.display = 'flex';
        } else {
            paramZRow.style.display = 'none';
            paramSurfaceRadio.style.display = 'none';
            paramSurfaceInputs.style.display = 'none';
            document.querySelector('input[name="parametric-mode"][value="curve"]').checked = true;
        }
        
        // 显示/隐藏输入区域
        const explicitImplicitGroup = document.getElementById('explicit-implicit-input-group');
        const polarGroup = document.getElementById('polar-input-group');
        const polarPhiGroup = document.getElementById('polar-phi-group');
        const parametricGroup = document.getElementById('parametric-input-group');
        const paramTRangeGroup = document.getElementById('param-t-range-group');
        const paramURangeGroup = document.getElementById('param-u-range-group');
        const paramVRangeGroup = document.getElementById('param-v-range-group');
        
        if (this.currentInputType === 'polar') {
            explicitImplicitGroup.style.display = 'none';
            polarGroup.style.display = 'block';
            parametricGroup.style.display = 'none';
            this.togglePolarParameters(true);
            this.toggleParametricParameters(false);
            
            // 三维模式下显示俯角输入
            if (this.currentScene === '3D') {
                polarPhiGroup.style.display = 'block';
            } else {
                polarPhiGroup.style.display = 'none';
            }
        } else if (this.currentInputType === 'parametric') {
            explicitImplicitGroup.style.display = 'none';
            polarGroup.style.display = 'none';
            polarPhiGroup.style.display = 'none';
            parametricGroup.style.display = 'block';
            this.togglePolarParameters(false);
            this.toggleParametricParameters(true);
        } else {
            explicitImplicitGroup.style.display = 'block';
            polarGroup.style.display = 'none';
            polarPhiGroup.style.display = 'none';
            parametricGroup.style.display = 'none';
            this.togglePolarParameters(false);
            this.toggleParametricParameters(false);
        }
    }
    
    toggleParametricParameters(show) {
        const tRangeGroup = document.getElementById('param-t-range-group');
        const uRangeGroup = document.getElementById('param-u-range-group');
        const vRangeGroup = document.getElementById('param-v-range-group');
        
        if (show) {
            const mode = document.querySelector('input[name="parametric-mode"]:checked').value;
            if (mode === 'curve') {
                tRangeGroup.style.display = 'block';
                uRangeGroup.style.display = 'none';
                vRangeGroup.style.display = 'none';
            } else {
                tRangeGroup.style.display = 'none';
                uRangeGroup.style.display = 'block';
                vRangeGroup.style.display = 'block';
            }
        } else {
            tRangeGroup.style.display = 'none';
            uRangeGroup.style.display = 'none';
            vRangeGroup.style.display = 'none';
        }
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