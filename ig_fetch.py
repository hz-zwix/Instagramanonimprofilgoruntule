# --- ig_fetch.py ---
import instaloader
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileResult:
    username: str
    full_name: str
    followers: int
    followees: int
    post_count: int
    bio: str
    bio_url: str
    profile_pic_url: str
    is_private: bool
    is_verified: bool
    is_business: bool
    error: Optional[str] = None


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def clean_username(raw: str) -> str:
    raw = raw.strip().lstrip("@")
    if "/" in raw:
        raw = raw.rstrip("/").split("/")[-1]
    return raw.split("?")[0]


def fetch_profile(raw_input: str) -> ProfileResult:
    username = clean_username(raw_input)

    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        return ProfileResult(
            username=username, full_name="", followers=0, followees=0,
            post_count=0, bio="", bio_url="", profile_pic_url="",
            is_private=False, is_verified=False, is_business=False,
            error=f"@{username} bulunamadı."
        )
    except instaloader.exceptions.ConnectionException as e:
        return ProfileResult(
            username=username, full_name="", followers=0, followees=0,
            post_count=0, bio="", bio_url="", profile_pic_url="",
            is_private=False, is_verified=False, is_business=False,
            error=f"Bağlantı hatası: {str(e)}"
        )
    except instaloader.exceptions.InstaloaderException as e:
        return ProfileResult(
            username=username, full_name="", followers=0, followees=0,
            post_count=0, bio="", bio_url="", profile_pic_url="",
            is_private=False, is_verified=False, is_business=False,
            error=f"Hata: {str(e)}"
        )

    return ProfileResult(
        username=profile.username,
        full_name=profile.full_name or profile.username,
        followers=profile.followers,
        followees=profile.followees,
        post_count=profile.mediacount,
        bio=profile.biography.strip() if profile.biography else "—",
        bio_url=profile.external_url or "—",
        profile_pic_url=profile.profile_pic_url,
        is_private=profile.is_private,
        is_verified=profile.is_verified,
        is_business=profile.is_business_account,
        error=None,
    )
