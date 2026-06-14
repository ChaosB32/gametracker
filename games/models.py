from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Platform(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name  = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6366f1')

    def __str__(self):
        return self.name


# ── Cache RAWG ────────────────────────────────────────────────────────────────

class RAWGCache(models.Model):
    """Armazena resultados da RAWG para evitar chamadas repetidas."""
    rawg_id         = models.IntegerField(unique=True)
    title           = models.CharField(max_length=200)
    cover_url       = models.URLField(max_length=500, blank=True)
    genre           = models.CharField(max_length=200, blank=True)
    developer       = models.CharField(max_length=200, blank=True)
    release_year    = models.IntegerField(null=True, blank=True)
    metacritic_score= models.IntegerField(null=True, blank=True)
    description     = models.TextField(blank=True)
    platforms_json  = models.TextField(blank=True)   # JSON list
    cached_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RAWG Cache'

    def __str__(self):
        return f"[Cache] {self.title}"

    def is_fresh(self, days=7):
        """Retorna True se o cache tem menos de `days` dias."""
        return (timezone.now() - self.cached_at).days < days


# ── Perfil de usuário ─────────────────────────────────────────────────────────

class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio        = models.TextField(blank=True, max_length=300)
    avatar_url = models.URLField(max_length=500, blank=True)
    location   = models.CharField(max_length=100, blank=True)
    favorite_genre = models.CharField(max_length=100, blank=True)
    is_public  = models.BooleanField(default=True, help_text='Perfil visível para outros usuários')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_stats(self):
        games = self.user.games.all()
        from django.db.models import Avg, Sum, Count
        avg = games.filter(rating__isnull=False).aggregate(a=Avg('rating'))['a']
        return {
            'total':      games.count(),
            'completed':  games.filter(status='completed').count(),
            'playing':    games.filter(status='playing').count(),
            'wishlist':   games.filter(status='wishlist').count(),
            'avg_rating': round(float(avg), 1) if avg else None,
            'total_hours':games.filter(hours_played__isnull=False).aggregate(s=Sum('hours_played'))['s'] or 0,
        }


class FavoritedGame(models.Model):
    """Jogos fixados no perfil público do usuário."""
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorited_games')
    game  = models.ForeignKey('Game', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['user', 'game']

    def __str__(self):
        return f"{self.user.username} ♥ {self.game.title}"


# ── Social: seguir amigos ─────────────────────────────────────────────────────

class Friendship(models.Model):
    """Relação de seguir entre usuários."""
    STATUS_CHOICES = [
        ('pending',  'Pendente'),
        ('accepted', 'Aceito'),
        ('blocked',  'Bloqueado'),
    ]
    from_user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    to_user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


# ── Game ──────────────────────────────────────────────────────────────────────

class Game(models.Model):
    STATUS_CHOICES = [
        ('playing',   '🎮 Jogando'),
        ('completed', '✅ Zerado'),
        ('abandoned', '❌ Abandonado'),
        ('queued',    '⏳ Na Fila'),
        ('wishlist',  '🌟 Wishlist'),
        ('paused',    '⏸️ Pausado'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    title        = models.CharField(max_length=200)
    platform     = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    rating       = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,
                       validators=[MinValueValidator(0), MaxValueValidator(10)])
    review       = models.TextField(blank=True)
    start_date   = models.DateField(null=True, blank=True)
    end_date     = models.DateField(null=True, blank=True)
    hours_played = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    tags         = models.ManyToManyField(Tag, blank=True)

    # RAWG metadata
    rawg_id          = models.IntegerField(null=True, blank=True)
    cover_url        = models.URLField(max_length=500, blank=True)
    genre            = models.CharField(max_length=200, blank=True)
    developer        = models.CharField(max_length=200, blank=True)
    release_year     = models.IntegerField(null=True, blank=True)
    metacritic_score = models.IntegerField(null=True, blank=True)
    description      = models.TextField(blank=True)

    # AI
    ai_insights     = models.TextField(blank=True)
    ai_generated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def get_status_color(self):
        return {
            'playing': 'emerald', 'completed': 'blue', 'abandoned': 'red',
            'queued': 'yellow', 'wishlist': 'purple', 'paused': 'orange',
        }.get(self.status, 'gray')

    def rating_stars(self):
        if self.rating is None:
            return 0
        return round(float(self.rating) / 2)
