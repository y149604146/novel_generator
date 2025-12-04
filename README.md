# novel_generator小说生成器
通过少量配置，调用大模型，自动生成小说

# 项目运行前置条件
需要本地用ollama部署好qwen3:8B或者其他你的其它大模型

# 项目启动
1. cd 到novel_writer目录下运行`pip install requirements.txt`
2. 找到`novel_writer/globals/noval_configues.py`,修改参数'novel_theme'，'novel_style'，'sample_novel_info'，'special_requires'，可参见给定的例子。
   'novel_theme'表示小说主题，
   'novel_style'表示小说风格，
   'sample_novel_info'表示生成小说的内容可以参考的已有小说
   'special_requires'表示其它具体的小说生成的细节，如章节结构，字数长度等等。
4. 找到`novel_writer/globals/OpenAIClient.py`，修改参数`model`为你的大模型的名字，如果用的是qwen3:8B则不用更改，修改参数`base_url`中ip的配置为你的ip
5. 找到`novel_writer/content_generator/content_generator.py`，运行它。

# 项目输出
运行结束后，可以在`novel_writer/output/`目录下面看到依照你在''里的小说设定，生成长篇小说。

