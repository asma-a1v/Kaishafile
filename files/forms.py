from django import forms
from .models import FileRecord
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class FileUploadForm(forms.ModelForm):
    """ファイルアップロードフォーム"""
    employee_code = forms.CharField(
        label="社員コード",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "社員コードを入力してください"})
    )
    
    class Meta:
        model = FileRecord
        fields = ['employee_code']  # ファイルはJavaScriptで処理
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'upload-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.layout = Layout(
            'employee_code',
            Submit('submit', '準備完了', css_class='btn-primary mt-3')
        ) 