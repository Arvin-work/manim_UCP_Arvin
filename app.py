from flask import Flask, render_template, request, jsonify, send_file
import json
import logging
import os
import tempfile
import threading
from datetime import datetime
from taylor_animator import TaylorExpansionAnimator

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

# 全局动画生成器
animator = TaylorExpansionAnimator()

class VisualizationController:
    """可视化项目核心控制器"""
    
    def __init__(self):
        self.current_scene = "2D"
        self.current_input_type = "explicit"
        self.selected_functions = []
        self.animation_tasks = {}
        
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
            
            # 特别处理泰勒展开
            if 'taylor' in functions:
                task_id = self._start_taylor_animation(parameters)
                return {
                    "status": "processing",
                    "message": "泰勒展开动画生成中...",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 打印场景信息
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
    
    def _start_taylor_animation(self, parameters):
        """启动泰勒展开动画生成任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            taylor_config = parameters.get('taylor_expansion', {})
            expansion_point = taylor_config.get('expansion_point', 0)
            max_order = taylor_config.get('max_order', 10)
            
            # 解析范围参数
            x_range_str = parameters.get('x_range', '-3,3')
            y_range_str = parameters.get('y_range', '-2,2')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-3, 3]
                y_range = [-2, 2]
            
            # 生成任务ID
            task_id = f"taylor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成动画
            def generate_animation():
                try:
                    logger.info(f"开始生成泰勒展开动画: {func_expression} 在 x={expansion_point}")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_animations")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成动画
                    video_path = animator.create_taylor_animation(
                        func_expression,
                        expansion_point,
                        max_order,
                        tuple(x_range),
                        tuple(y_range),
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"泰勒展开动画生成完成: {video_path}")
                    
                    # 自动播放动画
                    animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成泰勒展开动画失败: {str(e)}")
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动泰勒动画任务失败: {str(e)}")
            raise
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        return self.animation_tasks.get(task_id, {'status': 'not_found'})
    
    def _process_taylor_expansion(self, taylor_config):
        """处理泰勒展开配置"""
        expansion_point = taylor_config.get('expansion_point', 0)
        max_order = taylor_config.get('max_order', 10)
        animation_steps = taylor_config.get('animation_steps', True)
        
        logger.info("=" * 50)
        logger.info("泰勒展开配置")
        logger.info("=" * 50)
        logger.info(f"展开点: x = {expansion_point}")
        logger.info(f"最高阶数: {max_order}阶")
        logger.info(f"动画步骤: {'启用' if animation_steps else '禁用'}")
        logger.info("=" * 50)
    
    def _log_scene_info(self, scene_type, input_type, functions, parameters):
        """记录场景信息"""
        logger.info("=" * 50)
        logger.info("场景配置信息")
        logger.info("=" * 50)
        logger.info(f"场景类型: {scene_type}")
        logger.info(f"输入类型: {input_type}")
        logger.info(f"功能选项: {', '.join(functions)}")
        
        # 特别显示泰勒展开参数
        if 'taylor' in functions and 'taylor_expansion' in parameters:
            taylor_config = parameters['taylor_expansion']
            logger.info(f"泰勒展开点: {taylor_config.get('expansion_point', '未设置')}")
            logger.info(f"最高阶数: {taylor_config.get('max_order', '未设置')}")
        
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

@app.route('/api/task_status/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    status = controller.get_task_status(task_id)
    return jsonify(status)

@app.route('/api/download_animation/<task_id>')
def download_animation(task_id):
    """下载生成的动画"""
    task_info = controller.get_task_status(task_id)
    if task_info.get('status') == 'completed' and 'video_path' in task_info:
        return send_file(
            task_info['video_path'],
            as_attachment=True,
            download_name=f"taylor_expansion_{task_id}.mp4"
        )
    else:
        return jsonify({"status": "error", "message": "动画未就绪或不存在"}), 404

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