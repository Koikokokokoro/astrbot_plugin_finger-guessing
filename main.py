from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import random

@register("finger-guessing", "Koikokokokoro", "和群友来一把猜拳吧", "1.0.0")
class fingerguessing(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("猜拳")
    async def rock_paper_scissors(self, event: AstrMessageEvent):
        """
        /猜拳 @xxx
        与指定用户进行石头剪刀布（Emoji）游戏，随机生成双方手势并判定胜负
        """
        messages = event.get_messages()
        self_id = str(event.get_self_id())
        sender_id = str(event.get_sender_id())
        # 找到 @ 目标
        target_id = next(
            (str(seg.qq) for seg in messages
             if isinstance(seg, Comp.At) and str(seg.qq) != self_id),
            None
        )
        if not target_id:
            yield event.plain_result("请使用 /猜拳 @目标 来发起猜拳游戏。")
            return

        # 获取目标昵称
        nickname = target_id
        if event.get_platform_name() == "aiocqhttp":
            try:
                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
                assert isinstance(event, AiocqhttpMessageEvent)
                info = await event.bot.api.call_action('get_stranger_info', user_id=target_id)
                nickname = info.get('nick', nickname)
            except Exception as e:
                logger.error(f"获取昵称失败: {e}")

        # 手势列表（Emoji）
        gestures = ["✊", "✌️", "✋"]
        user_move = random.choice(gestures)
        target_move = random.choice(gestures)

        # 判定胜负
        result = "平局"
        wins = {
            "✊": "✌️",
            "✌️": "✋",
            "✋": "✊"
        }
        if user_move == target_move:
            result = "平局"
        elif wins[user_move] == target_move:
            result = "你赢了"
        else:
            result = "你输了"

        # 构造消息链
        chain = [
            Comp.Plain(f"你出了: {user_move}\n"),
            Comp.Plain(f"{nickname}出了: {target_move}\n"),
            Comp.Plain(f"结果: {result}")
        ]
        yield event.chain_result(chain)
