from novel_writer.globals import OpenAIClient
from novel_writer.globals.novel_configues import novel_configs
from novel_writer.utilities.Logger import logger
from novel_writer.utilities.WordGenerator import WordGenerator


class Outline_Design:

    def __init__(self):
        print("Outline_Design is initiated.")
        self.outline_design = None

    def __create_prompt(self,
                        novel_theme:str = novel_configs.novel_theme,
                        novel_style:str = novel_configs.novel_style,
                        sample_novel_info:str=novel_configs.sample_novel_info,
                        special_requires:str=novel_configs.special_requires):
        content = f"""
            你是一个小说作家，以一个整体题目开始，构思一个每个章节有强前后人物联系和事物发展联系的小说的提纲和章节，需要列出人物关系图、小说概要、小说中心立意。
            小说的主题是：{novel_theme},
            小说的写作风格是：{novel_style}
            小说写作样例：{sample_novel_info}
            小说写作要求：{special_requires}
            输出如果有表格则用markdown格式，否则用文字表述。

        """
        return content

    def get_outline_designs(self):
        if self.outline_design is None:
            content = self.__create_prompt()
            # client = OpenAI(api_key="0", base_url="http://localhost:11434/v1")
            messages = [
                {
                    "role": "system",
                    "content": "你是一个小说家，现需要构思小说提纲，每一章节前后需要有连贯的人物关系和事务发展逻辑，用中文回答。"
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
            self.outline_design = OpenAIClient.chat(messages).choices[0].message.content
            # self.outline_desgin = client.chat.completions.create(messages=messages, model="qwen:4b")
            logger.info(f"outline generated: {self.outline_design}")
        return self.outline_design

if __name__ == "__main__":
    rd = Outline_Design()
    out_line = rd.get_outline_designs()
    # out_line = TextUtility.remove_block("<think>","</think>")
    wg = WordGenerator("科幻小说提纲设计",save_full_path="outline_designs")
    wg.add_paragraph_section("","",out_line)
    wg.save_document()