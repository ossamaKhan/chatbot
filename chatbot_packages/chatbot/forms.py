# chatbot/forms.py

from django import forms

class ChatForm(forms.Form):
    query = forms.CharField(max_length=200, label="Ask about Zong packages")