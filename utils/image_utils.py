import os
from PIL import Image
from flask import current_app

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def resize_and_convert_image(file_path, max_size=(800, 800), quality=85):
    """调整图片大小并转换为WebP格式"""
    try:
        # 打开图片
        with Image.open(file_path) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # 调整大小
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 生成新的文件名（WebP格式）
            base_name = os.path.splitext(file_path)[0]
            webp_path = f"{base_name}.webp"
            
            # 保存为WebP格式
            img.save(webp_path, 'WebP', quality=quality, optimize=True)
            
            # 删除原文件
            if file_path != webp_path:
                os.remove(file_path)
            
            return webp_path
    except Exception as e:
        print(f"图片处理错误: {e}")
        return None

def save_uploaded_file(file, upload_folder, filename=None):
    """保存上传的文件"""
    if not filename:
        filename = file.filename
    
    # 确保文件名安全
    filename = secure_filename(filename)
    
    # 创建上传目录
    os.makedirs(upload_folder, exist_ok=True)
    
    # 完整的文件路径
    file_path = os.path.join(upload_folder, filename)
    
    # 保存文件
    file.save(file_path)
    
    # 处理图片
    if allowed_file(filename):
        processed_path = resize_and_convert_image(file_path)
        if processed_path:
            return os.path.basename(processed_path)
    
    return filename

def secure_filename(filename):
    """安全的文件名处理"""
    import re
    # 移除危险字符
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename
