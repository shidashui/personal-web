from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import Optional, Length, DataRequired


class DescriptionForm(FlaskForm):
    description = TextAreaField('描述', validators=[Optional(), Length(0,500)])
    submit = SubmitField()


class TagForm(FlaskForm):
    tag = StringField('添加标签(用空格隔开)', validators=[Optional(), Length(0,64)])
    submit = SubmitField()

class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField()


# class PostForm(FlaskForm):
#     title = StringField('标题', validators=[DataRequired(), Length(1,60)])
#     category = SelectField('分类', coerce=int, default=1)
#     body = CKEditorField('主体', validators=[DataRequired()])
#     submit = SubmitField()
#
#     def __init__(self, *args, **kwargs):
#         super(PostForm, self).__init__(*args,**kwargs)
#         self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]
