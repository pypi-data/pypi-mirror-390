"""
FlaskIt Discord Notifications
Simple and elegant Discord webhook integration
"""
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class DiscordColors:
    """Predefined Discord embed colors"""
    BLUE = 0x3498db
    GREEN = 0x2ecc71
    RED = 0xe74c3c
    YELLOW = 0xf39c12
    PURPLE = 0x9b59b6
    ORANGE = 0xe67e22
    TEAL = 0x1abc9c
    PINK = 0xe91e63
    BLACK = 0x000000
    WHITE = 0xffffff
    
    # Aliases
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = BLUE


class Discord:
    """Discord notification manager"""
    
    _webhooks: Dict[str, str] = {}
    _loaded: bool = False
    
    @classmethod
    def _load_webhooks(cls) -> None:
        """Load Discord webhooks from environment variables"""
        if cls._loaded:
            return
        
        # Load all DISCORD_* environment variables
        for key, value in os.environ.items():
            if key.startswith('DISCORD_'):
                # DISCORD_NEWUSER -> newuser
                webhook_name = key.replace('DISCORD_', '').lower()
                cls._webhooks[webhook_name] = value
        
        cls._loaded = True
    
    @classmethod
    def send(
        cls,
        channel: str,
        message: str,
        *,
        title: Optional[str] = None,
        color: Optional[int] = None,
        fields: Optional[list] = None,
        footer: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        author: Optional[Dict[str, str]] = None,
        timestamp: bool = True
    ) -> bool:
        """
        Send a notification to Discord
        
        Args:
            channel: Webhook channel name (e.g., 'newuser', 'contact')
            message: Main message content
            title: Embed title (optional)
            color: Embed color (use discord_colors.*)
            fields: List of fields
            footer: Footer text
            thumbnail: Thumbnail image URL
            image: Large image URL
            author: Author info
            timestamp: Add timestamp (default: True)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        cls._load_webhooks()
        
        # Get webhook URL
        webhook_url = cls._webhooks.get(channel.lower())
        if not webhook_url:
            print(f"⚠️  Discord webhook '{channel}' not found in environment variables")
            return False
        
        # Build embed
        embed = {
            "description": message,
            "color": color or DiscordColors.BLUE
        }
        
        if title:
            embed["title"] = title
        
        if fields:
            embed["fields"] = fields
        
        if footer:
            embed["footer"] = {"text": footer}
        
        if thumbnail:
            embed["thumbnail"] = {"url": thumbnail}
        
        if image:
            embed["image"] = {"url": image}
        
        if author:
            embed["author"] = author
        
        if timestamp:
            embed["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to Discord
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Discord notification: {e}")
            return False
    
    @classmethod
    def send_simple(cls, channel: str, message: str, color: Optional[int] = None) -> bool:
        """Send a simple text message to Discord"""
        return cls.send(channel, message, color=color)
    
    @classmethod
    def send_error(cls, channel: str, error: str, details: Optional[str] = None) -> bool:
        """Send an error notification"""
        fields = []
        if details:
            fields.append({
                "name": "Details",
                "value": f"```{details[:1000]}```",
                "inline": False
            })
        
        return cls.send(
            channel,
            error,
            title="❌ Error",
            color=DiscordColors.ERROR,
            fields=fields if fields else None
        )
    
    @classmethod
    def send_success(cls, channel: str, message: str, details: Optional[Dict[str, str]] = None) -> bool:
        """Send a success notification"""
        fields = []
        if details:
            for key, value in details.items():
                fields.append({
                    "name": key,
                    "value": str(value),
                    "inline": True
                })
        
        return cls.send(
            channel,
            message,
            title="✅ Success",
            color=DiscordColors.SUCCESS,
            fields=fields if fields else None
        )
    
    @classmethod
    def send_warning(cls, channel: str, message: str, details: Optional[str] = None) -> bool:
        """Send a warning notification"""
        fields = []
        if details:
            fields.append({
                "name": "Details",
                "value": details,
                "inline": False
            })
        
        return cls.send(
            channel,
            message,
            title="⚠️ Warning",
            color=DiscordColors.WARNING,
            fields=fields if fields else None
        )


# Create singleton instance
discord = Discord()

# Export colors for easy access
colors = DiscordColors()

__all__ = ['discord', 'colors', 'Discord', 'DiscordColors']
