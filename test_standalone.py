"""
Standalone test of the ChatExporter
Run this without NoneBot installed to test the exporter functionality
"""
import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the modules directly
from nonebot_plugin_qq_chat_exporter import models
from nonebot_plugin_qq_chat_exporter import exporter


def main():
    """Test the ChatExporter"""
    
    # Create exporter
    exp = exporter.ChatExporter()
    exp.set_chat_info("挞群～🍜WB老师生日快乐🍰～", "group")
    
    # Add some example messages
    exp.add_message(
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
    
    exp.add_message(
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
    exp.add_message(
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
            models.ContentResource(
                type="image",
                url="https://example.com/image.jpg",
                filename="image.jpg"
            )
        ]
    )
    
    # Export to file
    output_path = str(Path(__file__).parent / "example_export.json")
    export_data = exp.export(output_path)
    
    print(f"✓ Export completed!")
    print(f"✓ Total messages: {export_data.statistics.totalMessages}")
    print(f"✓ Total senders: {len(export_data.statistics.senders)}")
    print(f"✓ Total resources: {export_data.statistics.resources.total}")
    
    # Print sender statistics
    print("\nSender statistics:")
    for sender in export_data.statistics.senders:
        print(f"  - {sender.name}: {sender.messageCount} messages ({sender.percentage}%)")
    
    # Load and display the JSON to verify format
    with open(output_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    print("\n✓ Exported JSON structure:")
    print(f"  - metadata: {json_data['metadata']}")
    print(f"  - chatInfo: {json_data['chatInfo']}")
    print(f"  - statistics.totalMessages: {json_data['statistics']['totalMessages']}")
    print(f"  - statistics.senders: {len(json_data['statistics']['senders'])} senders")
    print(f"  - messages: {len(json_data['messages'])} messages")
    print(f"  - exportOptions: {json_data['exportOptions']['options']}")
    
    # Verify format compatibility
    print("\n✓ Format verification:")
    assert 'metadata' in json_data
    assert 'chatInfo' in json_data
    assert 'statistics' in json_data
    assert 'messages' in json_data
    assert 'exportOptions' in json_data
    print("  All required fields present!")
    
    print(f"\n✓ Output saved to: {output_path}")


if __name__ == "__main__":
    main()
