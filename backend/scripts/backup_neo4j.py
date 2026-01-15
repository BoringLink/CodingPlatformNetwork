#!/usr/bin/env python3
"""Neo4j数据库备份脚本"""

import os
import subprocess
import logging
from datetime import datetime

from config import NEO4J_CONFIG, MIGRATION_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, MIGRATION_CONFIG["log_level"]),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"/Users/tk/Documents/CodingPlatformNetwork/backend/logs/neo4j_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("neo4j_backup")

def backup_neo4j_database():
    """
    备份Neo4j数据库
    使用neo4j-admin命令进行备份
    """
    logger.info("开始执行Neo4j数据库备份")
    
    # 确保备份目录存在
    backup_dir = MIGRATION_CONFIG["backup_dir"]
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名，使用当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"neo4j_backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 构建neo4j-admin备份命令
    # 注意：这里使用的是neo4j-admin命令，需要确保该命令在系统PATH中
    # 或者使用完整路径，例如：/path/to/neo4j/bin/neo4j-admin
    backup_command = [
        "neo4j-admin",
        "database",
        "backup",
        "--from",
        f"neo4j://{NEO4J_CONFIG['uri'].split('://')[1]}",
        "--backup-dir",
        backup_dir,
        "--database",
        NEO4J_CONFIG["database"],
        "--name",
        backup_name,
        "--username",
        NEO4J_CONFIG["user"],
        "--password",
        NEO4J_CONFIG["password"]
    ]
    
    logger.info(f"执行备份命令: {' '.join(backup_command)}")
    
    try:
        # 执行备份命令
        result = subprocess.run(
            backup_command,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"备份成功: {backup_path}")
        logger.info(f"备份输出: {result.stdout}")
        
        # 验证备份文件是否存在
        if os.path.exists(os.path.join(backup_dir, backup_name)):
            logger.info(f"备份文件验证成功: {os.path.join(backup_dir, backup_name)}")
            return backup_path
        else:
            logger.error(f"备份文件不存在: {os.path.join(backup_dir, backup_name)}")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"备份失败，退出码: {e.returncode}")
        logger.error(f"备份错误输出: {e.stderr}")
        logger.error(f"备份标准输出: {e.stdout}")
        return None
    except Exception as e:
        logger.error(f"备份过程中发生未知错误: {str(e)}")
        return None

if __name__ == "__main__":
    backup_path = backup_neo4j_database()
    if backup_path:
        logger.info(f"备份完成，备份文件路径: {backup_path}")
    else:
        logger.error("备份失败，请检查日志")
