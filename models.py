from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "Users"

    username = Column(String)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    blogs = relationship("Blog", back_populates="user", cascade="delete")
    likes = relationship("Like", back_populates="user", cascade="delete")
    comments = relationship("Comment", back_populates="user", cascade="delete")
    images = relationship("Image", back_populates="user", cascade="delete")  # New relationship

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="blogs")
    images = relationship("Image", back_populates="blog", cascade="delete")
    likes = relationship("Like", back_populates="blog", cascade="delete")
    comments = relationship("Comment", back_populates="blog", cascade="delete")

    @property
    def like_count(self):
        return len(self.likes)

    @property
    def comment_count(self):
        return len(self.comments)

    @property
    def comments_on_blog(self):
        return [
            {
                "comment": comment.comment,
                "reply_of_comment": comment.reply_of_comment,
                "user": {
                    "name": comment.user.name,
                    "email": comment.user.email
                }
            }
            for comment in self.comments
        ]


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"))
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="likes")
    blog = relationship("Blog", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"))
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"))
    comment = Column(String)
    reply_of_comment = Column(String)

    user = relationship("User", back_populates="comments")
    blog = relationship("Blog", back_populates="comments")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"))
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="images")
    blog = relationship("Blog", back_populates="images")

