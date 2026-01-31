import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Comment
from app.schemas import CommentCreate, CommentUpdate
from app.config import settings


class CommentService:
    def __init__(self, db: Session):
        self.db = db

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
            return {**comment.__dict__, "replies": []}

        replies = self.get_replies(comment.id)
        reply_trees = [
            self.build_comment_tree(reply, depth + 1, max_depth) for reply in replies
        ]

        result = {**comment.__dict__, "replies": reply_trees}
        return result

    def create(self, obj_in: CommentCreate, author_id: uuid.UUID) -> Comment:
        if obj_in.parent_id:
            parent = self.get_by_id(obj_in.parent_id)
            if not parent or parent.post_id != obj_in.post_id:
                raise ValueError("Invalid parent comment")

        db_obj = Comment(
            post_id=obj_in.post_id,
            author_id=author_id,
            parent_id=obj_in.parent_id,
            content=obj_in.content,
            is_deleted=False,
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
