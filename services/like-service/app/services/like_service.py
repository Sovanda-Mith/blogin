from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Like, Post
import uuid


def get_post_id_by_slug(db: Session, slug: str) -> uuid.UUID:
    """Look up post ID by slug. Returns None if not found."""
    post = db.query(Post).filter(Post.slug == slug).first()
    if post:
        return post.id
    return None


def create_like(db: Session, user_id: uuid.UUID, post_id: uuid.UUID) -> Like:
    """Create a new like. Returns None if user already liked the post."""
    # Check if like already exists
    existing = (
        db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    )
    if existing:
        return None

    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def delete_like(db: Session, user_id: uuid.UUID, post_id: uuid.UUID) -> bool:
    """Delete a like (unlike). Returns True if deleted, False if not found."""
    like = (
        db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    )
    if not like:
        return False

    db.delete(like)
    db.commit()
    return True


def get_like_count(db: Session, post_id: uuid.UUID) -> int:
    """Get total likes count for a post."""
    return db.query(Like).filter(Like.post_id == post_id).count()


def has_user_liked(db: Session, user_id: uuid.UUID, post_id: uuid.UUID) -> bool:
    """Check if a user has liked a post."""
    return (
        db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
        is not None
    )


def get_user_likes_for_post(db: Session, post_id: uuid.UUID) -> list:
    """Get all likes for a specific post."""
    return db.query(Like).filter(Like.post_id == post_id).all()
