from novel_writer.globals import samples, OpenAIClient
from novel_writer.utilities import TextUtility
from novel_writer.utilities.Logger import logger
from novel_writer.content_generator.outline_designer import Outline_Design


class Abstract_Title:

    def __init__(self):
        print("abstract_title is initiated.")
        self.abstract_title = None

    def __create_prompt(self, outline_design:Outline_Design=None):
        content = f"""
            你是一个小说作家，根据提纲设计{outline_design}，提取出设计里面所有的小说章节的名字，严格按照章节设计的部分提取，不能自己改变或多生成不一样的题目。
            输出必须是JSON格式，包括两级，一级表示整体部数的信息，二级表示坐在部的章节信息，其层级、JSON数据KEY的设计必须如：
            样例：{samples.abstract_title_sample1}
            JSON格式遵循sample中的层级、KEY的设计，KEY对应的数值（样例中的“小说名”、“部名”、“章节名”）用提纲中的设计的名字，返回JSON数据。
        """
        return content

    def get_novel_titles(self, outline_design:Outline_Design):
        if self.abstract_title is None:
            content = self.__create_prompt(outline_design=outline_design)
            # client = OpenAI(api_key="0", base_url="http://localhost:11434/v1")
            messages = [
                {
                    "role": "system",
                    "content": "你是一个小说家，现需要根据构思好的提纲列出题目列表，用中文回答。"
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
            self.abstract_title = OpenAIClient.chat(messages).choices[0].message.content
            self.abstract_title = TextUtility.extract_json_with_context(self.abstract_title,False)
            logger.info(f"abstract_title generated: {self.abstract_title}")
            # self.outline_desgin = client.chat.completions.create(messages=messages, model="qwen:4b")

        return self.abstract_title

if __name__ == "__main__":
    # 生成提纲
    rd = Outline_Design()
    out_line = rd.get_outline_designs()
    logger.info(f"out_line generated: {out_line}")
    # out_line = TextUtility.remove_block("<think>","</think>")
    # 根据提纲生成题目列表
    tt = Abstract_Title()
    titles = tt.get_novel_titles(out_line)
    print(titles)