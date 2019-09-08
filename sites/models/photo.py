import os
from datetime import datetime

from flask import current_app

from sites.extensions import whooshee, db
from sites.models import *


# class Item(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     item_key = db.Column(db.Integer)   #[(0,Photo),(1,Post)]
#     item_id = db.Column(db.Integer)


tagging = db.Table('tagging',
                   db.Column('photo_id',db.Integer, db.ForeignKey('photo.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                   )


@whooshee.register_model('description')
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(64))
    filename_s = db.Column(db.String(64)) #小图
    filename_m = db.Column(db.String(64)) #中图
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='photos')

    flag = db.Column(db.Integer, default=0)  #被举报次数
    can_comment = db.Column(db.Boolean, default=True)
    comments = db.relationship('PhotoComment', back_populates='photo', cascade='all')
    tags = db.relationship('Tag', secondary=tagging, back_populates='photos')
    collectors = db.relationship('Collect', back_populates='collected', cascade='all')


@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    photos = db.relationship('Photo', secondary=tagging, back_populates='tags')


class PhotoComment(db.Model):
    __tablename__ = 'photo_comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)  #举报次数

    replied_id = db.Column(db.Integer, db.ForeignKey('photo_comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))

    photo = db.relationship('Photo', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('PhotoComment', back_populates='replied', cascade='all')
    replied = db.relationship('PhotoComment', back_populates='replies', remote_side=[id])



#消息提醒
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', back_populates='notifications')


#图片删除事件监听函数
@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photos(**kwargs):
    target = kwargs['target']
    for filename in [target.filename, target.filename_s, target.filename_m]:
        path = os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename)
        if os.path.exists(path):
            os.remove(path)

