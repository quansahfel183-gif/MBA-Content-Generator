from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, unique=True)
    handle = Column(String(150), nullable=False)
    account_name = Column(String(150), nullable=False)
    account_type = Column(String(50), nullable=False)   # Personal / Business / Page
    followers = Column(String(30), default="")
    avatar_url = Column(String(500), default="")
    access_token = Column(Text, default="")
    token_expires = Column(String(50), default="")
    connected = Column(Boolean, default=True)
    connected_at = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "handle": self.handle,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "followers": self.followers,
            "avatar_url": self.avatar_url,
            "has_token": bool(self.access_token),   # never expose the raw token
            "token_expires": self.token_expires,
            "connected": self.connected,
            "connected_at": self.connected_at,
        }


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    post_type = Column(String(100), nullable=False)
    caption = Column(Text, nullable=False)
    created_at = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "date": self.date,
            "time": self.time,
            "post_type": self.post_type,
            "caption": self.caption,
            "created_at": self.created_at,
        }
