from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
import os

class GetGameRequirementNode(Node):
    def exec(self, _):
        # Get game requirement directly from user input
        requirement = input("请输入游戏需求描述: ")
        return requirement

    def post(self, shared, prep_res, exec_res):
        # Store the requirement
        shared["requirement"] = exec_res
        return "default"

class BackgroundStoryNode(Node):
    def prep(self, shared):
        return shared["requirement"]

    def exec(self, requirement):
        prompt = f"""
你是一名富有想象力的专业游戏设计师，基于以下游戏需求，设计一个富有吸引力且符合用户意图的背景故事文案。

游戏需求: {requirement}

背景故事应包含：
- 故事发生的地点
- 时代背景
- 核心事件
- 冲突或悬念点

请以Markdown格式输出完整的背景故事文案。
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        # 提取所有```markdown ```标签包裹的内容
        import re
        markdown_blocks = re.findall(r'```markdown\s+(.*?)```', exec_res, re.DOTALL)

        # 如果找到了markdown块，将它们合并为最终结果
        if markdown_blocks:
            exec_res = '\n\n'.join(markdown_blocks)

        # Store the background story
        shared["background_story"] = exec_res

        # Save to file
        with open("background-story.md", "w", encoding="utf-8") as f:
            f.write(exec_res)

        print("✅ 背景故事已生成并保存至 background-story.md")
        return "default"

class CharactersDesignNode(Node):
    def prep(self, shared):
        # Read background story from file to ensure consistency
        with open("background-story.md", "r", encoding="utf-8") as f:
            background_story = f.read()
        return background_story, shared["requirement"]

    def exec(self, inputs):
        background_story, requirement = inputs
        prompt = f"""
你是一名具有专业背景的写作者，基于以下背景故事和游戏需求，设计游戏中出现的关键人物设定。

背景故事:
{background_story}

游戏需求:
{requirement}

为每个人物设定以下要素：
- 姓名
- 年龄
- 性别
- 性格特征
- 外貌描述
- 背景故事
- 在主故事中的角色定位

请至少设计3-5个核心人物，并以Markdown格式输出所有人物设定。
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        # 提取所有```markdown ```标签包裹的内容
        import re
        markdown_blocks = re.findall(r'```markdown\s+(.*?)```', exec_res, re.DOTALL)

        # 如果找到了markdown块，将它们合并为最终结果
        if markdown_blocks:
            exec_res = '\n\n'.join(markdown_blocks)

        # Store the characters design
        shared["characters"] = exec_res

        # Save to file
        with open("characters.md", "w", encoding="utf-8") as f:
            f.write(exec_res)

        print("✅ 人物设定已生成并保存至 characters.md")
        return "default"

class StoryFlowNode(BatchNode):
    def prep(self, shared):
        # Define how many chapters to generate
        num_chapters = 3  # Can be adjusted based on game requirements
        return list(range(1, num_chapters + 1))  # [1, 2, 3] for chapter numbers

    def exec(self, chapter_num):
        # Read background story and characters for context
        with open("background-story.md", "r", encoding="utf-8") as f:
            background_story = f.read()

        with open("characters.md", "r", encoding="utf-8") as f:
            characters = f.read()

        # For chapter 1, we focus on introduction
        # For middle chapters, we focus on development and conflicts
        # For the last chapter, we focus on resolution

        prompt = f"""
你是一名具有很深的文学素养的写作者，请设计游戏故事的第{chapter_num}章内容。

参考背景故事:
{background_story}

参考人物设定:
{characters}

请先以记叙文的形式编写这个章节的故事，包括时间、地点、人物、事件以及细致记录的完整的人物对话过程等。

再根据章节的记叙文，提取包含以下要素的章节信息:
- 章节标题
- 章节概要
- 关键剧情发展点
- 人物互动

{"这是开篇章节，需要引入背景故事和主要人物。" if chapter_num == 1 else ""}
{"这是中间章节，需要展现冲突和情节发展。" if 1 < chapter_num < 3 else ""}
{"这是结局章节，需要解决冲突并提供适当的结局。" if chapter_num == 3 else ""}

最后请以Markdown格式输出完整的章节内容。
"""
        return chapter_num, call_llm(prompt)

    def post(self, shared, prep_res, exec_res_list):
        # Store the chapters and save to files
        chapters = {}

        for chapter_num, content in exec_res_list:
            chapter_file = f"chapter-{chapter_num:02d}.md"
            chapters[chapter_file] = content

            # 提取所有```markdown ```标签包裹的内容
            import re
            markdown_blocks = re.findall(r'```markdown\s+(.*?)```', content, re.DOTALL)

            # 如果找到了markdown块，将它们合并为最终结果
            if markdown_blocks:
                content = '\n\n'.join(markdown_blocks)

            # Save to file
            with open(chapter_file, "w", encoding="utf-8") as f:
                f.write(content)

        shared["chapters"] = chapters
        print(f"✅ {len(chapters)}个章节已生成并保存")
        return "default"

class YarnScriptNode(BatchNode):
    def prep(self, shared):
        # Get all chapter files
        chapter_files = [f for f in os.listdir() if f.startswith("chapter-") and f.endswith(".md")]
        chapter_files.sort()  # Ensure proper ordering
        return chapter_files

    def exec(self, chapter_file):
        # Read the chapter content
        with open(chapter_file, "r", encoding="utf-8") as f:
            chapter_content = f.read()

        # Read background story and characters for context
        with open("background-story.md", "r", encoding="utf-8") as f:
            background_story = f.read()

        with open("characters.md", "r", encoding="utf-8") as f:
            characters = f.read()

        # Read Yarn syntax guide
        with open("introduction-to-yarn.md", "r", encoding="utf-8") as f:
            yarn_guide = f.read()

        chapter_num = chapter_file.replace("chapter-", "").replace(".md", "")

        prompt = f"""
请将以下章节内容转换为Yarn游戏脚本语言。

章节内容:
{chapter_content}

参考背景故事:
{background_story}

参考人物设定:
{characters}

Yarn语言规则:
{yarn_guide}

要求：
1. 使用标准 Yarn 语法生成互动对话节点，确保所有节点之间连接正确。
2. 脚本内容需包含不少于 300 行对话，并不少于 7 个独立节点。
3. 每个主要节点应包含多轮细腻对话（每个节点建议至少 20-30 句对话），人物语气自然丰富，展现个性与情感张力。
4. 为故事中的关键剧情节点设计多个互动分支，引导玩家进行选择，每个分支建议引出新的节点并展开内容，形成 树状结构。
5. 使用 Yarn 变量（如 <<set $hasRing to true>>）记录玩家关键行为和状态，后续分支需反映这些状态变化。
6. 在不同节点中加入自然流畅的旁白，提供场景描写、心理活动和时间推进，使故事更有代入感。
7. **允许在必要时补充细节（如增加人物动作描写、环境描写）**来增强文本长度和表现力，只要不偏离设定。
8. 禁止省略结构或使用“略去部分”之类的方式缩短内容。
9. 输出时请完整展开所有分支内容，避免使用省略号或简略表述。
10. 最后请仅输出符合 Yarn Spinner 格式的 .yarn 脚本文件内容，不需要任何解释或补充说明。
11. 请生成不少于 4000 个字符的完整 Yarn 脚本，确保故事连贯、有层次感，并包含多个发展路径。

参考故事脚本示例：

```yarn
Narrator: 门口的风铃清脆响起，她气喘吁吁地出现在你视线中。

莉莉: 对不起！我迟到了，你没等太久吧？

<<if $sentMessage is true>>
	莉莉: 啊，刚才看到你的短信了，谢谢你关心！
<<endif>>

-> 没关系，刚到不久
	<<set $kindResponse to true>>
	<<set $love += 1>>
-> 我都快以为你不来了
	<<set $kindResponse to false>>
	<<set $love -= 5>>

<<if $kindResponse>>
	我: 没关系，我也刚到不久。先坐下来休息一下吧。
	莉莉: 呼～谢谢你，今天的公交车实在太挤了！
<<else>>
	我: 我还以为你不来了呢，害我担心了这么久。
	莉莉: 抱歉啦……我下次一定早点出门！
<<endif>>

Narrator: 服务员端上了你们点的咖啡，醇香的味道弥漫开来。

莉莉: 对了，你平时都喜欢做些什么呢？我们之前还没聊太多。

-> 我喜欢读书、看电影
-> 我更喜欢运动和旅行
```

请直接输出符合Yarn语法的脚本内容，无需其他解释。
"""

        yarn_script = call_llm(prompt)

        return chapter_file, yarn_script

    def post(self, shared, prep_res, exec_res_list):
        # Store and save yarn scripts
        yarn_scripts = {}

        for chapter_file, yarn_script in exec_res_list:
            # 提取所有```yarn ```标签包裹的内容
            import re
            yarn_blocks = re.findall(r'```yarn\s+(.*?)```', yarn_script, re.DOTALL)

            # 如果找到了yarn块，将它们合并为最终结果
            if yarn_blocks:
                yarn_script = '\n\n'.join(yarn_blocks)

            yarn_file = chapter_file.replace(".md", ".yarn")
            yarn_scripts[yarn_file] = yarn_script

            # Save to file
            with open(yarn_file, "w", encoding="utf-8") as f:
                f.write(yarn_script)

        shared["yarn_scripts"] = yarn_scripts
        print(f"✅ {len(yarn_scripts)}个Yarn脚本已生成并保存")
        return "default"

class SummaryNode(Node):
    def prep(self, shared):
        # Get all the files we've generated
        background_file = "background-story.md"
        characters_file = "characters.md"
        chapter_files = [f for f in os.listdir() if f.startswith("chapter-") and f.endswith(".md")]
        yarn_files = [f for f in os.listdir() if f.startswith("chapter-") and f.endswith(".yarn")]

        return {
            "background": background_file,
            "characters": characters_file,
            "chapters": chapter_files,
            "yarn_scripts": yarn_files
        }

    def exec(self, files):
        return files

    def post(self, shared, prep_res, exec_res):
        # Print summary of generated files
        print("\n===== 游戏内容生成完成 =====")
        print(f"背景故事: {exec_res['background']}")
        print(f"人物设定: {exec_res['characters']}")
        print(f"章节文件: {', '.join(exec_res['chapters'])}")
        print(f"Yarn脚本: {', '.join(exec_res['yarn_scripts'])}")
        print("==========================\n")
        return "default"