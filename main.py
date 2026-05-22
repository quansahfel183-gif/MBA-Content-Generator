import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import anthropic
from datetime import datetime

from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Edenbrook Villa AI Marketing OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are the AI marketing strategist for Edenbrook Villa by Qluxe Homes. You create sophisticated, luxury-register content for a boutique real estate development in Accra, Ghana.

PROPERTY DETAILS:
- Edenbrook Villa: 5-unit exclusive luxury development in Tse Addo, Accra, Ghana
- THE SIGNATURE: $420,000 | 4 ensuite bedrooms | 2,200 sqft | Premium finishes throughout
- THE HORIZON: $440,000 | 4 ensuite bedrooms + private rooftop terrace | 2,200 sqft
- THE GRAND ESTATE: $460,000 | 5 bedrooms | Rooftop penthouse office | Ultimate luxury
- Phase 1 is 100% self-financed by Qluxe Homes — buyer deposits secure units only, they do NOT fund construction
- Build completes Late 2026 regardless of sales performance
- Escrow option: Payments held by independent third party, released against verified construction milestones
- Website: edenbrookvilla.com

TARGET BUYER PROFILE:
- West African diaspora professionals aged 35–55 living in the US and UK
- Doctors, lawyers, engineers, entrepreneurs, senior executives
- Purchasing for: legacy building, homeland reconnection, investment returns
- Sophisticated, discerning, have been burned by off-plan risks before — they want assurance, not pressure

LOCATION ADVANTAGES:
- Tse Addo, Accra — adjacent to Cantonments and Airport Residential (Accra's prime addresses)
- Minutes from Labadi Beach and key commercial corridors
- Near embassies, international schools, and business hubs
- Emerging premium corridor with strong appreciation potential

MARKET DATA (cite when relevant):
- Prime Accra real estate appreciation: 20–25% since 2020
- Rental yields in premium Accra neighborhoods: 8–11%
- Ghana GDP growth: 5.7% in 2024
- Rising diaspora demand for quality, developer-backed properties

DEVELOPER: Qluxe Homes — boutique luxury developer committed to architectural distinction and curated exclusivity.

BRAND VOICE RULES:
1. Luxury register: unhurried, confident, never desperate or salesy
2. Speak to aspiration, legacy, and homecoming — not fear or urgency
3. Emphasize self-funded construction as the ultimate trust differentiator
4. NEVER use: "Don't miss out", "Limited time", "Act now", "Only X left", "Hurry"
5. USE instead: "curated", "considered", "legacy", "distinction", "crafted", "for those who..."
6. Quality over quantity — five exclusive units, not a mass development
7. The diaspora buyer is intelligent and skeptical — earn trust, don't push
8. Write in complete, polished sentences. No bullet spam for social content.
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 2048


class PostCreate(BaseModel):
    platform: str
    date: str
    time: str
    post_type: str
    caption: str


class AccountUpsert(BaseModel):
    platform: str
    handle: str
    account_name: str
    account_type: str
    followers: Optional[str] = ""
    avatar_url: Optional[str] = ""
    access_token: Optional[str] = ""
    token_expires: Optional[str] = ""


@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Frontend not found. Ensure static/index.html exists.</h1>",
            status_code=404,
        )


@app.post("/api/generate")
async def generate_content(request: GenerateRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY environment variable is not configured.",
        )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=request.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": request.prompt}],
        )
        return {"content": message.content[0].text}
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid Anthropic API key.")
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429, detail="Rate limit reached. Please try again shortly."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@app.get("/api/posts")
async def get_posts(db: Session = Depends(get_db)):
    posts = (
        db.query(models.ScheduledPost)
        .order_by(models.ScheduledPost.date, models.ScheduledPost.time)
        .all()
    )
    return [p.to_dict() for p in posts]


@app.post("/api/posts")
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = models.ScheduledPost(
        platform=post.platform,
        date=post.date,
        time=post.time,
        post_type=post.post_type,
        caption=post.caption,
        created_at=datetime.now().isoformat(),
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post.to_dict()


@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(models.ScheduledPost)
        .filter(models.ScheduledPost.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}


@app.get("/api/accounts")
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(models.SocialAccount).all()
    return [a.to_dict() for a in accounts]


@app.put("/api/accounts")
async def upsert_account(account: AccountUpsert, db: Session = Depends(get_db)):
    existing = (
        db.query(models.SocialAccount)
        .filter(models.SocialAccount.platform == account.platform)
        .first()
    )
    if existing:
        existing.handle = account.handle
        existing.account_name = account.account_name
        existing.account_type = account.account_type
        existing.followers = account.followers
        existing.avatar_url = account.avatar_url
        if account.access_token:          # only overwrite if a new token was provided
            existing.access_token = account.access_token
        existing.token_expires = account.token_expires
        existing.connected = True
        existing.connected_at = datetime.now().isoformat()
        db.commit()
        db.refresh(existing)
        return existing.to_dict()
    else:
        new_acct = models.SocialAccount(
            platform=account.platform,
            handle=account.handle,
            account_name=account.account_name,
            account_type=account.account_type,
            followers=account.followers,
            avatar_url=account.avatar_url,
            access_token=account.access_token,
            token_expires=account.token_expires,
            connected=True,
            connected_at=datetime.now().isoformat(),
        )
        db.add(new_acct)
        db.commit()
        db.refresh(new_acct)
        return new_acct.to_dict()


@app.delete("/api/accounts/{platform}")
async def disconnect_account(platform: str, db: Session = Depends(get_db)):
    account = (
        db.query(models.SocialAccount)
        .filter(models.SocialAccount.platform == platform)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"message": f"{platform} disconnected"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Edenbrook Villa AI Marketing OS"}
