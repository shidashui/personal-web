
from sites.models import *



#分类
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), primary_key=True)
    posts = db.relationship('Post', back_populates='category')

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    author = db.relationship('User', back_populates='categories')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

#文章
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)
    # slug = db.Column(db.String(60))

    flag = db.Column(db.Integer, default=0)  #被举报次数

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='posts')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('PostComment', back_populates='post', cascade='all, delete-orphan')


#评论
class PostComment(db.Model):
    __tablename__ = 'post_comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)  # 举报次数

    replied_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='post_comments')
    replies = db.relationship('PostComment', back_populates='replied', cascade='all')
    replied = db.relationship('PostComment', back_populates='replies', remote_side=[id])


#链接
# class Link(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30))
#     url = db.Column(db.String(255))