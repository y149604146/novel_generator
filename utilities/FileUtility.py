import os

from novel_writer.utilities.Logger import logger


def create_folder_if_not_exists(folder_name):
    """
    如果文件夹不存在则创建，存在则跳过

    Args:
        folder_name (str): 文件夹名称
    """
    try:
        # 检查文件夹是否存在，不存在则创建
        if not os.path.exists(folder_name):
            # 使用 exist_ok=True 时，若文件夹已存在不会报错
            os.makedirs(folder_name, exist_ok=True)
            logger.info(f"文件夹 '{folder_name}' 创建成功")
        # else:
        #     print(f"文件夹 '{folder_name}' 已存在，无需创建")

    except PermissionError:
        print(f"错误：没有权限创建文件夹 '{folder_name}'")
    except Exception as e:
        print(f"创建文件夹时出错：{str(e)}")