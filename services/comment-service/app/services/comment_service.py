import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from app.models import Comment
from app.schemas import CommentCreate, CommentUpdate
from app.config import settings
import httpx


class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_author_info(self, user_id: uuid.UUID) -> dict:
        try:
            result = self.db.execute(
                text(
                    "SELECT username, display_name, avatar_url FROM users.profiles WHERE user_id = :user_id"
                ),
                {"user_id": str(user_id)},
            ).fetchone()
            if result:
                return {
                    "username": result[0],
                    "display_name": result[1],
                    "avatar_url": result[2],
                }
        except Exception:
            pass
        return {"username": None, "display_name": None, "avatar_url": None}

    def get_by_id(self, comment_id: uuid.UUID) -> Optional[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.id == comment_id, Comment.is_deleted == False)
            .first()
        )

    def get_by_post(self, post_id: uuid.UUID, page: int = 1, page_size: int = None):
        page_size = page_size or settings.DEFAULT_PAGE_SIZE

        query = (
            self.db.query(Comment)
            .filter(
                Comment.post_id == post_id,
                Comment.parent_id == None,
                Comment.is_deleted == False,
            )
            .order_by(desc(Comment.created_at))
        )

        total = query.count()
        comments = query.offset((page - 1) * page_size).limit(page_size).all()

        return {"items": comments, "total": total, "page": page, "page_size": page_size}

    def get_replies(self, comment_id: uuid.UUID) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.parent_id == comment_id, Comment.is_deleted == False)
            .order_by(Comment.created_at)
            .all()
        )

    def build_comment_tree(
        self, comment: Comment, depth: int = 0, max_depth: int = 5
    ) -> dict:
        if depth >= max_depth:
            return self._comment_to_dict(comment)

        replies = self.get_replies(comment.id)
        reply_trees = [
            self.build_comment_tree(reply, depth + 1, max_depth) for reply in replies
        ]

        result = self._comment_to_dict(comment)
        result["replies"] = reply_trees
        return result

    def _comment_to_dict(self, comment: Comment) -> dict:
        return {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author_id": str(comment.author_id),
            "author_username": comment.author_username,
            "author_display_name": comment.author_display_name,
            "author_avatar": comment.author_avatar_url,
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "content": comment.content if not comment.is_deleted else "[deleted]",
            "is_deleted": comment.is_deleted,
            "created_at": comment.created_at.isoformat()
            if comment.created_at
            else None,
            "updated_at": comment.updated_at.isoformat()
            if comment.updated_at
            else None,
            "edited_at": comment.edited_at.isoformat() if comment.edited_at else None,
            "edited": comment.edited_at is not None,
        }

    def create(self, obj_in: CommentCreate, author_id: uuid.UUID) -> Comment:
        if obj_in.parent_id:
            parent = self.get_by_id(obj_in.parent_id)
            if not parent or parent.post_id != obj_in.post_id:
                raise ValueError("Invalid parent comment")

        author_info = self._fetch_author_info(author_id)

        db_obj = Comment(
            post_id=obj_in.post_id,
            author_id=author_id,
            parent_id=obj_in.parent_id,
            content=obj_in.content,
            is_deleted=False,
            author_username=author_info.get("username"),
            author_display_name=author_info.get("display_name"),
            author_avatar_url=author_info.get("avatar_url"),
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Comment, obj_in: CommentUpdate) -> Comment:
        from datetime import datetime

        if obj_in.content is not None:
            db_obj.content = obj_in.content
            db_obj.edited_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, comment_id: uuid.UUID, author_id: uuid.UUID) -> bool:
        comment = (
            self.db.query(Comment)
            .filter(
                Comment.id == comment_id,
                Comment.author_id == author_id,
                Comment.is_deleted == False,
            )
            .first()
        )

        if not comment:
            return False

        comment.is_deleted = True
        self.db.commit()
        return True

    def get_comment_count_by_post(self, post_id: uuid.UUID) -> int:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.is_deleted == False)
            .count()
        )

    def get_all_comments_by_post(self, post_id: uuid.UUID) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.is_deleted == False)
            .order_by(Comment.created_at)
            .all()
        )
