import os

from novel_writer.content_generator.abstract_titles import Abstract_Title
from novel_writer.globals import OpenAIClient
from novel_writer.globals.novel_configues import novel_configs
from novel_writer.utilities import FileUtility
from novel_writer.utilities.Logger import logger
from novel_writer.utilities.WordGenerator import WordGenerator
from novel_writer.content_generator.outline_designer import Outline_Design


class Novel_Content:

    def __init__(self):
        print("Novel_Content is initiated.")
        self.novel_content = None

    def __create_prompt(self,
                        outline_design:Outline_Design=None,
                        title=None
                        ):
        content = f"""
            你是一个小说作家，已经构思好了一个小说的提纲和章节以及背景要求如下：
            {outline_design}
            以诸多章节中的《{title}》为题，完成小说内容的编写，5000字左右的小说体，每出现一个新人物的时候需要做简单介绍。
            不要再分出小标题，不要写任何跟小说内容无关的注解、内容。

        """
        return content

    def get_novel_contents(self,
                           outline_design:Outline_Design,
                           title:str=None):
        if self.novel_content is None:
            content = self.__create_prompt(outline_design=outline_design, title=title)
            # client = OpenAI(api_key="0", base_url="http://localhost:11434/v1")
            messages = [
                {
                    "role": "system",
                    "content": f"""
                                你是一个小说家，需要按照提供的背景要求，完成小说内容。
                                """
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
            self.novel_content = OpenAIClient.chat(messages).choices[0].message.content
            # self.outline_desgin = client.chat.completions.create(messages=messages, model="qwen:4b")

        return self.novel_content

if __name__ == "__main__":
    # 1. 生成提纲
    rd = Outline_Design()
    out_line = rd.get_outline_designs()
    logger.info(f"out_line generated: {out_line}")
    # 2. 根据提纲生成各层级标题
    tt = Abstract_Title()
    titles = tt.get_novel_titles(out_line)
    logger.info(f"abstract_titles json format : {tt}")
    logger.info(titles)
    # 3. 根据提纲、各层级生成小说
    # 3.1 以小说名字，生成根目录
    title = titles["novel_name"]
    title_dir = str(os.path.join(novel_configs.output_base_dir,title))
    logger.info(f"title_dir = {title_dir}")
    FileUtility.create_folder_if_not_exists(title_dir)
    # 提纲生成到小说根目录下
    outline_wg = WordGenerator(title="整体设计思路", save_full_path=str(os.path.join(title_dir, "整体设计思路")))
    outline_wg.add_paragraph_section("", "", out_line)
    outline_wg.save_document()
    # 3.2 以部为名字，生成二级目录
    parts = titles["novel_parts"]
    for i, e in enumerate(parts):
        part_name = "Part"+str(e["part_number"])+"_"+e["part_name"]
        part_dir = str(os.path.join(str(title_dir), str(part_name)))
        logger.info(f"part_dir = {part_dir}")
        FileUtility.create_folder_if_not_exists(part_dir)
        # 3.3 以章节为名字，生成小说内容
        chapters = e["chapters"]
        for c in chapters:
            chapter_name = "Chapter"+str(c["chapter_number"])+"_" + c["chapter_name"]
            cg = Novel_Content()
            novel_content = cg.get_novel_contents(out_line, chapter_name)
            # 生成word文档
            chapter_dir = str(os.path.join(part_dir, chapter_name))
            logger.info(f"Prepare generate {chapter_dir}.doxc")
            wg = WordGenerator(title = chapter_name, save_full_path=chapter_dir)
            wg.add_paragraph_section("", "", novel_content)
            wg.save_document()

