"""
Example usage of the ChatExporter
"""
from nonebot_plugin_qq_chat_exporter import ChatExporter
from nonebot_plugin_qq_chat_exporter.models import ContentResource


def main():
    """Example of using ChatExporter programmatically"""
    
    # Create exporter
    exporter = ChatExporter()
    exporter.set_chat_info("挞群～🍜WB老师生日快乐🍰～", "group")
    
    # Add some example messages
    exporter.add_message(
        message_id="7455223690249164332",
        message_seq="599433",
        timestamp="2025-01-01T03:20:01.000Z",
        sender_uid="u_p5xtAG4HzR1XVy_4Iy699A",
        sender_name="唐嘉上小天使是用头脑作战",
        sender_uin="765576958",
        receiver_uid="543612610",
        receiver_type="group",
        content_text="[1]",
        message_type=5,
        is_system=True,
        is_recalled=True,
    )
    
    exporter.add_message(
        message_id="7455223690249164333",
        message_seq="599434",
        timestamp="2025-01-01T03:21:00.000Z",
        sender_uid="u_AAZF7VI5YhKKyQ2y17LTBg",
        sender_name="小爱",
        sender_uin="123456789",
        receiver_uid="543612610",
        receiver_type="group",
        content_text="Hello, World!",
        message_type=0,
        is_system=False,
        is_recalled=False,
    )
    
    # Add message with image
    exporter.add_message(
        message_id="7455223690249164334",
        message_seq="599435",
        timestamp="2025-01-01T03:22:00.000Z",
        sender_uid="u_AAZF7VI5YhKKyQ2y17LTBg",
        sender_name="小爱",
        sender_uin="123456789",
        receiver_uid="543612610",
        receiver_type="group",
        content_text="看这张图片",
        message_type=0,
        is_system=False,
        is_recalled=False,
        resources=[
            ContentResource(
                type="image",
                url="https://example.com/image.jpg",
                filename="image.jpg"
            )
        ]
    )
    
    # Export to file
    export_data = exporter.export("./example_export.json")
    
    print(f"Export completed!")
    print(f"Total messages: {export_data.statistics.totalMessages}")
    print(f"Total senders: {len(export_data.statistics.senders)}")
    print(f"Total resources: {export_data.statistics.resources.total}")
    
    # Print sender statistics
    print("\nSender statistics:")
    for sender in export_data.statistics.senders:
        print(f"  - {sender.name}: {sender.messageCount} messages ({sender.percentage}%)")


if __name__ == "__main__":
    main()
