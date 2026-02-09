from django import forms

class ColorPickerWidget(forms.TextInput):
    """Widget para selector de color HTML5"""
    input_type = 'color'
    
    def __init__(self, attrs=None):
        default_attrs = {'style': 'width: 100px; height: 40px; cursor: pointer;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
