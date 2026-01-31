from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, Table, Column, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from slugify import slugify
from app.models import Post, Tag
from app.database import Base
from app.schemas import PostCreate, PostUpdate
import uuid
from datetime import datetime

# Reference to users.profiles table for cross-schema queries
users_profiles = Table(
    "profiles",
    Base.metadata,
    Column("user_id", PGUUID(as_uuid=True), primary_key=True),
    Column("username", String(50)),
    schema="users",
)


def get_post_by_id(db: Session, post_id: uuid.UUID) -> Optional[Post]:
    return (
        db.query(Post).options(joinedload(Post.tags)).filter(Post.id == post_id).first()
    )


def get_post_by_slug(db: Session, slug: str) -> Optional[Post]:
    return (
        db.query(Post).options(joinedload(Post.tags)).filter(Post.slug == slug).first()
    )


def generate_unique_slug(
    db: Session, title: str, exclude_post_id: Optional[uuid.UUID] = None
) -> str:
    base_slug = slugify(title, max_length=50)
    slug = base_slug
    counter = 1

    while True:
        query = db.query(Post).filter(Post.slug == slug)
        if exclude_post_id:
            query = query.filter(Post.id != exclude_post_id)

        if not query.first():
            break

        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    tags = []
    for name in tag_names:
        tag_slug = slugify(name, max_length=50)
        tag = db.query(Tag).filter(func.lower(Tag.name) == func.lower(name)).first()
        if not tag:
            tag = Tag(name=name, slug=tag_slug)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags


def create_post(db: Session, author_id: uuid.UUID, post_data: PostCreate) -> Post:
    slug = generate_unique_slug(db, post_data.title)
    tags = get_or_create_tags(db, post_data.tags or [])

    published_at = None
    if post_data.status == "published":
        published_at = datetime.utcnow()

    post = Post(
        author_id=author_id,
        title=post_data.title,
        slug=slug,
        content=post_data.content,
        summary=post_data.summary,
        status=post_data.status,
        published_at=published_at,
        tags=tags,
    )

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(
    db: Session, post_id: uuid.UUID, author_id: uuid.UUID, post_data: PostUpdate
) -> Optional[Post]:
    post = get_post_by_id(db, post_id)
    if not post or post.author_id != author_id:
        return None

    update_data = post_data.dict(exclude_unset=True)

    # Handle tags separately
    if "tags" in update_data:
        tags = get_or_create_tags(db, update_data.pop("tags") or [])
        post.tags = tags

    # Generate new slug if title changed
    if "title" in update_data and update_data["title"] != post.title:
        update_data["slug"] = generate_unique_slug(db, update_data["title"], post_id)

    # Handle publish date
    if "status" in update_data:
        if update_data["status"] == "published" and post.status != "published":
            update_data["published_at"] = datetime.utcnow()
        elif update_data["status"] != "published":
            update_data["published_at"] = None

    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: uuid.UUID, author_id: uuid.UUID) -> bool:
    post = get_post_by_id(db, post_id)
    if not post or post.author_id != author_id:
        return False

    db.delete(post)
    db.commit()
    return True


def list_posts(
    db: Session,
    status: Optional[str] = None,
    author_id: Optional[uuid.UUID] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple:
    # Join with users.profiles to get username
    # Note: Don't use joinedload here as it conflicts with explicit joins and column selection
    query = db.query(
        Post, users_profiles.c.username.label("author_username")
    ).outerjoin(users_profiles, Post.author_id == users_profiles.c.user_id)

    if status:
        query = query.filter(Post.status == status)
    else:
        query = query.filter(Post.status == "published")

    if author_id:
        query = query.filter(Post.author_id == author_id)

    if tag:
        query = query.join(Post.tags).filter(func.lower(Tag.name) == func.lower(tag))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_pattern)) | (Post.content.ilike(search_pattern))
        )

    total = query.count()
    results = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()

    # Return list of tuples (post, username)
    return results, total


def increment_view_count(db: Session, post_id: uuid.UUID) -> bool:
    post = get_post_by_id(db, post_id)
    if not post:
        return False

    post.view_count += 1
    db.commit()
    return True


def get_all_tags(db: Session) -> List[Tag]:
    return db.query(Tag).order_by(Tag.name).all()


def get_posts_by_author(
    db: Session, author_id: uuid.UUID, skip: int = 0, limit: int = 20
) -> tuple:
    query = (
        db.query(Post, users_profiles.c.username.label("author_username"))
        .outerjoin(users_profiles, Post.author_id == users_profiles.c.user_id)
        .filter(Post.author_id == author_id, Post.status == "published")
    )
    total = query.count()
    results = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    return results, total
