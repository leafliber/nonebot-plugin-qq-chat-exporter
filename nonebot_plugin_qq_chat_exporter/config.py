"""
Plugin configuration
"""
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Plugin configuration"""
    
    # Export directory
    qq_chat_exporter_output_dir: str = Field(
        default="./exports",
        description="Directory to save exported chat data"
    )
    
    # Include system messages
    qq_chat_exporter_include_system: bool = Field(
        default=True,
        description="Include system messages in export"
    )
    
    # Include resource links
    qq_chat_exporter_include_resources: bool = Field(
        default=True,
        description="Include resource links in export"
    )
    
    # Time format
    qq_chat_exporter_time_format: str = Field(
        default="YYYY-MM-DD HH:mm:ss",
        description="Time format for exported messages"
    )
    
    # Encoding
    qq_chat_exporter_encoding: str = Field(
        default="utf-8",
        description="File encoding for exported data"
    )
