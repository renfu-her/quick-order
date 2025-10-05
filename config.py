import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


def _default_database_url() -> str:
    """Return the default database URL used when DATABASE_URL is not set."""

    db_path = BASE_DIR / 'quick_orders.db'
    return f"sqlite:///{db_path}"


class Config:
    """基础配置类"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _default_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 图片上传配置
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
