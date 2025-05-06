from flow import create_yarn_story_flow

def main():
    """
    运行Yarn故事游戏开发流程
    该流程包括以下步骤：
    1. 获取游戏需求
    2. 生成背景故事
    3. 设计游戏人物
    4. 设计故事流程
    5. 生成Yarn游戏脚本
    """
    # 初始化共享数据
    shared = {
        "requirement": None,  # 将在运行时从用户输入获取
        "background_story": None,
        "characters": None,
        "chapters": None,
        "yarn_scripts": None
    }

    # 创建并运行游戏开发流程
    yarn_story_flow = create_yarn_story_flow()

    print("\n===== Yarn故事游戏开发助手 =====")
    print("这个流程将帮助你创建一个基于Yarn语言的交互式文字游戏。")
    print("请按照提示输入游戏需求，系统将自动完成游戏内容的设计和脚本编写。")
    print("================================\n")

    # 运行流程
    yarn_story_flow.run(shared)

if __name__ == "__main__":
    main()
