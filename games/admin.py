from django.contrib import admin
from .models import Game, Platform, Tag, UserProfile, FavoritedGame, Friendship, RAWGCache

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display  = ['title', 'user', 'platform', 'status', 'rating', 'created_at']
    list_filter   = ['status', 'platform', 'user']
    search_fields = ['title', 'developer']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at', 'ai_generated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'is_public', 'created_at']

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter  = ['status']

@admin.register(RAWGCache)
class RAWGCacheAdmin(admin.ModelAdmin):
    list_display  = ['title', 'rawg_id', 'cached_at']
    search_fields = ['title']
    readonly_fields = ['cached_at']

@admin.register(FavoritedGame)
class FavoritedGameAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'order']
