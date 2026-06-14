from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Game, Platform, Tag, UserProfile

INPUT  = 'w-full bg-[var(--input-bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-[var(--text)] placeholder-[var(--text-muted)] focus:outline-none focus:border-violet-500 transition text-sm'
SELECT = 'w-full bg-[var(--input-bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-[var(--text)] focus:outline-none focus:border-violet-500 transition text-sm'


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT})


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='Nome',
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Seu nome'}))
    last_name  = forms.CharField(max_length=30, required=False, label='Sobrenome',
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Seu sobrenome'}))

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_url', 'location', 'favorite_genre', 'is_public']
        widgets = {
            'bio':            forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Conte um pouco sobre você e seus games favoritos...'}),
            'avatar_url':     forms.URLInput(attrs={'class': INPUT, 'placeholder': 'URL de uma imagem (ex: link do Gravatar)'}),
            'location':       forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: São Paulo, Brasil'}),
            'favorite_genre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: RPG, Aventura...'}),
            'is_public':      forms.CheckboxInput(attrs={'class': 'w-5 h-5 accent-violet-600'}),
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'title', 'platform', 'status', 'rating', 'review',
            'start_date', 'end_date', 'hours_played', 'tags',
            'cover_url', 'genre', 'developer', 'release_year',
        ]
        widgets = {
            'title':        forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nome do jogo...', 'id': 'id_title'}),
            'platform':     forms.Select(attrs={'class': SELECT}),
            'status':       forms.Select(attrs={'class': SELECT}),
            'rating':       forms.NumberInput(attrs={'class': INPUT, 'step': 'any', 'min': '0', 'max': '10', 'placeholder': '0.0 – 10.0'}),
            'review':       forms.Textarea(attrs={'class': INPUT, 'rows': 4, 'placeholder': 'Sua análise...'}),
            'start_date':   forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'end_date':     forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'hours_played': forms.NumberInput(attrs={'class': INPUT, 'step': '0.5', 'min': '0', 'placeholder': 'Horas jogadas'}),
            'tags':         forms.CheckboxSelectMultiple(),
            'cover_url':    forms.URLInput(attrs={'class': INPUT, 'placeholder': 'URL da capa (auto)'}),
            'genre':        forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Gênero'}),
            'developer':    forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Desenvolvedor'}),
            'release_year': forms.NumberInput(attrs={'class': INPUT, 'placeholder': 'Ano'}),
        }
