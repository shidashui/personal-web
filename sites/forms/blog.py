from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

from sites.models.blog import Category


class CategoryForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(1,30)])
    submit = SubmitField()

    def validate_name(self, field):
        #current_user.category.query.filter_by(name=field.data)这样也行吧
        if Category.query.filter_by(name=field.data, author_id=current_user.id).first():
            raise ValidationError('类别已存在')



# class PostForm(FlaskForm):
#     title = StringField('标题', validators=[DataRequired(), Length(1,60)])
#     category = SelectField('分类', coerce=int, default=1)
#     body = CKEditorField('主体', validators=[DataRequired()])
#     submit = SubmitField()
#
#     def __init__(self, *args, **kwargs):
#         super(PostForm, self).__init__(*args,**kwargs)
#         self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]