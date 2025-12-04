import json

def remove_block(content: str, start: str = "", end: str = "") -> str:
    """
    移除内容中所有以start开头、以end结尾的块（包括标记本身）

    Args:
        content: 原始内容字符串
        start: 起始标记（默认""）
        end: 结束标记（默认""）

    Returns:
        移除目标块后的字符串
    """
    result = []
    i = 0
    len_content = len(content)
    len_start = len(start)
    len_end = len(end)

    while i < len_content:
        # 查找起始标记
        if content.startswith(start, i):
            # 跳过起始标记
            i += len_start
            # 查找结束标记
            end_pos = content.find(end, i)
            if end_pos == -1:
                # 若未找到结束标记，保留剩余内容
                result.append(content[i:])
                break
            # 跳过结束标记及中间内容
            i = end_pos + len_end
        else:
            # 保留非标记内容
            result.append(content[i])
            i += 1

    return ''.join(result)


def json_to_markdown(data, level=1, md_content=None):
    """
    递归将多级JSON转换为Markdown格式
    :param data: 输入的JSON数据（dict/list）
    :param level: 当前层级（用于生成标题级别）
    :param md_content: 存储Markdown内容的列表（递归复用）
    :return: 完整的Markdown字符串
    """
    if md_content is None:
        md_content = []

    # 处理字典类型（键值对）
    if isinstance(data, dict):
        for key, value in data.items():
            # 生成当前层级标题（# 对应level=1，## 对应level=2，以此类推）
            md_content.append(f"{'#' * level} {key}")

            # 如果值是字典/列表，递归处理；否则直接作为内容
            if isinstance(value, (dict, list)):
                json_to_markdown(value, level + 1, md_content)
            else:
                # 普通值（字符串/数字/布尔）直接添加，支持换行符转义
                value_str = str(value).replace("\n", "  \n")  # Markdown换行需要2个空格+换行
                md_content.append(f"- {value_str}\n")

    # 处理列表类型（有序展示）
    elif isinstance(data, list):
        for idx, item in enumerate(data, 1):
            # 列表项标题（结合层级和索引）
            md_content.append(f"{'#' * level} 列表项 {idx}")

            # 如果列表项是字典/列表，递归处理；否则直接作为内容
            if isinstance(item, (dict, list)):
                json_to_markdown(item, level + 1, md_content)
            else:
                item_str = str(item).replace("\n", "  \n")
                md_content.append(f"- {item_str}\n")

    return "\n".join(md_content)


def extract_json_from_content(content: str, multiple: bool = False) -> list | dict | None:
    """
    从文本内容中提取JSON数据（纯字符遍历实现，兼容所有Python版本）

    Args:
        content: 包含JSON的文本内容
        multiple: 是否提取多个JSON对象（默认False，仅提取第一个）

    Returns:
        提取的JSON数据（dict/list），多个则返回列表，无则返回None
    """

    def find_json_blocks(text):
        """查找所有完整的JSON块（{}或[]）"""
        blocks = []

        # 查找{}包裹的JSON对象
        stack = []
        start = -1
        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start != -1:
                        blocks.append(text[start:i + 1])
                        start = -1

        # 查找[]包裹的JSON数组
        stack = []
        start = -1
        for i, char in enumerate(text):
            if char == '[':
                if not stack:
                    start = i
                stack.append(char)
            elif char == ']':
                if stack:
                    stack.pop()
                    if not stack and start != -1:
                        blocks.append(text[start:i + 1])
                        start = -1

        return blocks

    # 预处理内容（移除空白字符干扰）
    content = content.strip()

    # 查找所有JSON块
    json_blocks = find_json_blocks(content)

    if not json_blocks:
        return None

    result = []
    for block in json_blocks:
        try:
            # 尝试解析JSON
            json_data = json.loads(block.strip())
            result.append(json_data)

            # 如果不需要多个，找到第一个就返回
            if not multiple:
                return json_data
        except (json.JSONDecodeError, ValueError):
            continue

    return result if multiple else (result[0] if result else None)


def extract_json_enhanced(content: str, multiple: bool = False) -> list | dict | None:
    """
    增强版JSON提取，支持处理带注释、末尾逗号等不规范JSON

    Args:
        content: 包含JSON的文本内容
        multiple: 是否提取多个JSON对象

    Returns:
        提取的JSON数据
    """
    import re

    # 预处理：移除//注释
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    # 预处理：移除/* */注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # 预处理：移除末尾逗号（如 { "key": "value", }）
    content = re.sub(r',\s*([}\]])', r'\1', content)

    return extract_json_from_content(content, multiple)


def extract_json_with_context(content: str, multiple: bool = False) -> list | dict | None:
    """
    带上下文的JSON提取，处理更复杂的嵌套情况

    Args:
        content: 包含JSON的文本内容
        multiple: 是否提取多个JSON对象

    Returns:
        提取的JSON数据
    """

    def find_matching_bracket(text, start_index, open_char, close_char):
        """查找匹配的闭合括号位置"""
        count = 1
        for i in range(start_index + 1, len(text)):
            if text[i] == open_char:
                count += 1
            elif text[i] == close_char:
                count -= 1
                if count == 0:
                    return i
        return -1

    blocks = []
    i = 0

    while i < len(content):
        if content[i] == '{':
            end = find_matching_bracket(content, i, '{', '}')
            if end != -1:
                blocks.append(content[i:end + 1])
                i = end + 1
            else:
                i += 1
        elif content[i] == '[':
            end = find_matching_bracket(content, i, '[', ']')
            if end != -1:
                blocks.append(content[i:end + 1])
                i = end + 1
            else:
                i += 1
        else:
            i += 1

    if not blocks:
        return None

    result = []
    for block in blocks:
        try:
            json_data = json.loads(block.strip())
            result.append(json_data)

            if not multiple:
                return json_data
        except (json.JSONDecodeError, ValueError):
            continue

    return result if multiple else (result[0] if result else None)


# ------------------- 示例使用 -------------------
if __name__ == "__main__":
    # rs = remove_block("test start <think> test reason part </think> test end.", "<think>","</think>")
    # print(f"rs = {rs}")

    # 多级JSON示例（业务组给的sample）,转换为Markdown
    # sample_json = {
    #     "项目信息": {
    #         "名称": "risk_report_generator",
    #         "类型": "Python后端项目",
    #         "技术栈": ["FastAPI", "Docker", "CI/CD"],
    #         "版本": "1.0.0"
    #     },
    #     "接口配置": {
    #         "基础路径": "/api/v1",
    #         "接口列表": [
    #             {
    #                 "接口名称": "生成风险报告",
    #                 "请求方法": "POST",
    #                 "请求参数": {
    #                     "必选参数": [
    #                         {"参数名": "user_id", "类型": "str", "说明": "用户ID"},
    #                         {"参数名": "risk_type", "类型": "list", "说明": "风险类型列表"}
    #                     ],
    #                     "可选参数": {
    #                         "report_format": "pdf",
    #                         "expire_time": 3600
    #                     }
    #                 },
    #                 "响应格式": {
    #                     "code": 200,
    #                     "data": {"report_id": "xxx", "download_url": "xxx"},
    #                     "msg": "success"
    #                 }
    #             }
    #         ]
    #     }
    # }
    # markdown_result = json_to_markdown(sample_json)
    #
    # # 打印结果（或写入文件）
    # print(markdown_result)
    #
    # 写入Markdown文件（可选）
    # with open("json_to_md_result.md", "w", encoding="utf-8") as f:
    #     f.write(markdown_result)

    # 提取内容中json的部分
    # 示例1：简单JSON文本
    content1 = '这是一段文本 {"name": "test", "value": 123} 后面还有内容'
    json1 = extract_json_from_content(content1)
    print("示例1结果:", json1)

    # 示例2：嵌套JSON
    content2 = '数据: {"id": 1, "data": {"nested": [1, 2, {"key": "value"}]}} 结束'
    json2 = extract_json_with_context(content2)
    print("示例2结果:", json2)

    # 示例3：带注释的不规范JSON
    content3 = '''配置信息：
        {
            "server": "localhost", // 服务器地址
            "port": 8080, /* 端口号 */
            "options": [1, 2, 3,], // 末尾有逗号
        }
        '''
    json3 = extract_json_enhanced(content3)
    print("示例3结果:", json3)

    # 示例4：多个JSON对象
    content4 = '[{"id":1},{"id":2},{"id":3}] 额外内容 {"status":"success"}'
    json4 = extract_json_from_content(content4, multiple=True)
    print("示例4结果:", json4)

    # 示例5：title提取过程中llm生成的json
    content5 = """
    ```json
    {
        "novel_name": "《时空褶皱里的早餐摊》",
        "novel_parts": [
            {
                "part_number": 1,
                "part_name": "《量子煎饼果子》",
                "chapters": [
                    {
                        "chapter_number": 1,
                        "chapter_name": "煎饼的量子纠缠"
                    },
                    {
                        "chapter_number": 2,
                        "chapter_name": "实验室的油条危机"
                    },
                    {
                        "chapter_number": 3,
                        "chapter_name": "蝴蝶效应煎饼摊"
                    },
                    {
                        "chapter_number": 4,
                        "chapter_name": "薛定谔的豆浆"
                    },
                    {
                        "chapter_number": 5,
                        "chapter_name": "时空褶皱的真相"
                    }
                ]
            },
            {
                "part_number": 2,
                "part_name": "《平行宇宙的韭菜盒子》",
                "chapters": [
                    {
                        "chapter_number": 1,
                        "chapter_name": "韭菜盒子的宇宙分裂"
                    },
                    {
                        "chapter_number": 2,
                        "chapter_name": "时间掠夺者的早餐战争"
                    },
                    {
                        "chapter_number": 3,
                        "chapter_name": "薛定谔的韭菜"
                    },
                    {
                        "chapter_number": 4,
                        "chapter_name": "熵增与煎饼摊的熵减"
                    },
                    {
                        "chapter_number": 5,
                        "chapter_name": "早餐摊的宇宙重启"
                    }
                ]
            }
        ]
    }
    ```
    """
    json5 = extract_json_enhanced(content5)
    print("示例3结果:", json5)