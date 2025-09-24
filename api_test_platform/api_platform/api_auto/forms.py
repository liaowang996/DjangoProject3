from django import forms

class ExcelUploadForm(forms.Form):
    """Excel上传表单"""
    excel_file = forms.FileField(
        label="选择Excel文件",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xls,.xlsx'  # 仅允许xls/xlsx
        })
    )