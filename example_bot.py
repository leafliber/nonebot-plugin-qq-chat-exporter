"""
NoneBot2 配置示例

将此文件内容添加到你的 bot.py 或单独的配置文件中
"""

# 导入必要的模块
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

# 加载插件
# 注意：必须先加载 chatrecorder 插件
nonebot.load_plugin("nonebot_plugin_chatrecorder")
nonebot.load_plugin("nonebot_plugin_qq_chat_exporter")

if __name__ == "__main__":
    nonebot.run()
