from flask import Flask, render_template, request, jsonify
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visualization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

class VisualizationController:
    """可视化项目核心控制器"""
    
    def __init__(self):
        self.current_scene = "2D"
        self.current_input_type = "explicit"
        self.selected_functions = []
        
    def process_visualization_request(self, scene_data):
        """处理可视化请求"""
        try:
            logger.info(f"接收到可视化请求: {scene_data}")
            
            # 解析场景数据
            scene_type = scene_data.get('scene_type', '2D')
            input_type = scene_data.get('input_type', 'explicit')
            functions = scene_data.get('functions', [])
            parameters = scene_data.get('parameters', {})
            
            # 更新当前状态
            self.current_scene = scene_type
            self.current_input_type = input_type
            self.selected_functions = functions
            
            # 打印场景信息（模拟后端处理）
            self._log_scene_info(scene_type, input_type, functions, parameters)
            
            return {
                "status": "success",
                "message": f"{scene_type}场景处理完成",
                "timestamp": datetime.now().isoformat(),
                "data_received": scene_data
            }
            
        except Exception as e:
            logger.error(f"处理可视化请求时出错: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _log_scene_info(self, scene_type, input_type, functions, parameters):
        """记录场景信息"""
        logger.info("=" * 50)
        logger.info("场景配置信息")
        logger.info("=" * 50)
        logger.info(f"场景类型: {scene_type}")
        logger.info(f"输入类型: {input_type}")
        logger.info(f"功能选项: {', '.join(functions)}")
        logger.info(f"参数配置: {json.dumps(parameters, indent=2, ensure_ascii=False)}")
        logger.info("=" * 50)

# 初始化控制器
controller = VisualizationController()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/switch_scene', methods=['POST'])
def switch_scene():
    """切换2D/3D场景"""
    data = request.json
    scene_type = data.get('scene_type', '2D')
    logger.info(f"切换场景到: {scene_type}")
    
    return jsonify({
        "status": "success",
        "current_scene": scene_type,
        "message": f"已切换到{scene_type}场景"
    })

@app.route('/api/switch_input_type', methods=['POST'])
def switch_input_type():
    """切换输入类型"""
    data = request.json
    input_type = data.get('input_type', 'explicit')
    logger.info(f"切换输入类型到: {input_type}")
    
    return jsonify({
        "status": "success",
        "current_input_type": input_type,
        "message": f"已切换到{input_type}输入"
    })

@app.route('/api/start_creation', methods=['POST'])
def start_creation():
    """开始创作 - 处理用户配置"""
    try:
        data = request.json
        logger.info("接收到开始创作请求")
        
        # 处理可视化请求
        result = controller.process_visualization_request(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"开始创作处理失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理失败: {str(e)}"
        }), 500

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        "status": "running",
        "current_scene": controller.current_scene,
        "current_input_type": controller.current_input_type,
        "selected_functions": controller.selected_functions,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("启动Manim简化可视化工具...")
    app.run(debug=True, host='127.0.0.1', port=5000)