import csv
import json
from datetime import datetime, timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Sum, Q
from django.views.decorators.http import require_GET, require_POST

from .models import Game, Platform, Tag, UserProfile, FavoritedGame, Friendship, RAWGCache
from .forms import GameForm, RegisterForm, UserProfileForm
from .services import search_games_rawg, get_game_details_rawg, generate_ai_insights


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# ── AUTH ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            _get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}! 🎮')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'games/register.html', {'form': form})


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    games        = Game.objects.filter(user=request.user)
    total        = games.count()
    completed    = games.filter(status='completed').count()
    playing      = games.filter(status='playing').count()
    avg_rating   = games.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg']
    total_hours  = round(float(games.filter(hours_played__isnull=False).aggregate(s=Sum('hours_played'))['s'] or 0), 1)

    platform_stats = list(
        games.filter(platform__isnull=False)
        .values('platform__name').annotate(count=Count('id')).order_by('-count')[:6]
    )
    status_stats   = list(games.values('status').annotate(count=Count('id')).order_by('-count'))
    status_display = dict(Game.STATUS_CHOICES)
    status_data    = [{'label': status_display.get(s['status'], s['status']), 'count': s['count']} for s in status_stats]

    recent_games = games.select_related('platform')[:6]
    top_games    = games.filter(rating__isnull=False).order_by('-rating')[:5]

    genre_counts = {}
    for g in games.exclude(genre=''):
        for genre in g.genre.split(','):
            genre = genre.strip()
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    top_genres = sorted(genre_counts.items(), key=lambda x: -x[1])[:6]

    # Amigos jogando agora
    friend_ids = Friendship.objects.filter(
        from_user=request.user, status='accepted'
    ).values_list('to_user_id', flat=True)
    friends_playing = Game.objects.filter(
        user__in=friend_ids, status='playing'
    ).select_related('user', 'platform')[:5]

    return render(request, 'games/dashboard.html', {
        'total': total, 'completed': completed, 'playing': playing,
        'avg_rating': round(float(avg_rating), 1) if avg_rating else None,
        'total_hours': total_hours,
        'platform_stats': platform_stats, 'status_data': status_data,
        'recent_games': recent_games, 'top_games': top_games,
        'top_genres': top_genres, 'friends_playing': friends_playing,
    })


# ── GAME LIST ─────────────────────────────────────────────────────────────────

@login_required
def game_list(request):
    games    = Game.objects.filter(user=request.user).select_related('platform').prefetch_related('tags')
    status   = request.GET.get('status', '')
    platform = request.GET.get('platform', '')
    tag      = request.GET.get('tag', '')
    search   = request.GET.get('q', '')
    sort     = request.GET.get('sort', '-updated_at')

    if status:   games = games.filter(status=status)
    if platform: games = games.filter(platform__id=platform)
    if tag:      games = games.filter(tags__id=tag)
    if search:   games = games.filter(Q(title__icontains=search) | Q(genre__icontains=search) | Q(developer__icontains=search))
    if sort in ['title', '-title', '-rating', 'rating', '-created_at', 'created_at', '-hours_played']:
        games = games.order_by(sort)

    return render(request, 'games/game_list.html', {
        'games': games,
        'platforms': Platform.objects.all(),
        'tags': Tag.objects.all(),
        'status_choices': Game.STATUS_CHOICES,
        'current_filters': {'status': status, 'platform': platform, 'tag': tag, 'q': search, 'sort': sort},
    })


# ── GAME DETAIL ───────────────────────────────────────────────────────────────

@login_required
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    is_favorited = FavoritedGame.objects.filter(user=request.user, game=game).exists()
    return render(request, 'games/game_detail.html', {'game': game, 'is_favorited': is_favorited})


# ── CREATE / EDIT / DELETE ────────────────────────────────────────────────────

@login_required
def game_create(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.user = request.user
            rawg_id = request.POST.get('rawg_id')
            if rawg_id:
                details = get_game_details_rawg(int(rawg_id))
                if details:
                    game.rawg_id          = details.get('rawg_id')
                    game.cover_url        = game.cover_url or details.get('cover_url', '')
                    game.genre            = game.genre or details.get('genre', '')
                    game.developer        = game.developer or details.get('developer', '')
                    game.release_year     = game.release_year or details.get('release_year')
                    game.metacritic_score = details.get('metacritic_score')
                    game.description      = details.get('description', '')
            game.save()
            form.save_m2m()
            messages.success(request, f'"{game.title}" adicionado! 🎮')
            return redirect('game_detail', pk=game.pk)
    else:
        form = GameForm()
    return render(request, 'games/game_form.html', {'form': form, 'action': 'Adicionar Jogo'})


@login_required
def game_edit(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{game.title}" atualizado! ✅')
            return redirect('game_detail', pk=game.pk)
    else:
        form = GameForm(instance=game)
    return render(request, 'games/game_form.html', {'form': form, 'game': game, 'action': 'Editar Jogo'})


@login_required
def game_delete(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    if request.method == 'POST':
        title = game.title
        game.delete()
        messages.success(request, f'"{title}" removido.')
        return redirect('game_list')
    return render(request, 'games/game_confirm_delete.html', {'game': game})


# ── FAVORITAR JOGO NO PERFIL ──────────────────────────────────────────────────

@login_required
@require_POST
def toggle_favorite(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    fav, created = FavoritedGame.objects.get_or_create(user=request.user, game=game)
    if not created:
        fav.delete()
        return JsonResponse({'favorited': False})
    return JsonResponse({'favorited': True})


# ── PERFIL PRÓPRIO ────────────────────────────────────────────────────────────

@login_required
def my_profile(request):
    profile = _get_or_create_profile(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        # Atualiza first_name / last_name no User
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.save()
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado! ✅')
            return redirect('my_profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name':  request.user.last_name,
        })

    stats          = profile.get_stats()
    favorited      = FavoritedGame.objects.filter(user=request.user).select_related('game')[:6]
    following_count = Friendship.objects.filter(from_user=request.user, status='accepted').count()
    followers_count = Friendship.objects.filter(to_user=request.user, status='accepted').count()
    pending_requests = Friendship.objects.filter(to_user=request.user, status='pending').select_related('from_user')

    return render(request, 'games/profile.html', {
        'profile': profile, 'form': form, 'stats': stats,
        'favorited': favorited,
        'following_count': following_count,
        'followers_count': followers_count,
        'pending_requests': pending_requests,
        'is_own': True,
    })


# ── PERFIL PÚBLICO DE OUTRO USUÁRIO ──────────────────────────────────────────

@login_required
def user_profile(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return redirect('my_profile')

    profile = _get_or_create_profile(target_user)

    if not profile.is_public:
        messages.warning(request, 'Este perfil é privado.')
        return redirect('friends_list')

    # Status de amizade
    friendship = Friendship.objects.filter(
        from_user=request.user, to_user=target_user
    ).first()

    stats     = profile.get_stats()
    favorited = FavoritedGame.objects.filter(user=target_user).select_related('game')[:6]
    following_count = Friendship.objects.filter(from_user=target_user, status='accepted').count()
    followers_count = Friendship.objects.filter(to_user=target_user, status='accepted').count()

    # Jogos públicos para comparação
    their_games = Game.objects.filter(user=target_user).select_related('platform').order_by('-updated_at')

    return render(request, 'games/profile.html', {
        'profile': profile,
        'target_user': target_user,
        'stats': stats,
        'favorited': favorited,
        'following_count': following_count,
        'followers_count': followers_count,
        'friendship': friendship,
        'their_games': their_games,
        'is_own': False,
    })


# ── COMPARAR COM AMIGO ────────────────────────────────────────────────────────

@login_required
def compare_with(request, username):
    other = get_object_or_404(User, username=username)

    my_games    = {g.title: g for g in Game.objects.filter(user=request.user)}
    their_games = {g.title: g for g in Game.objects.filter(user=other)}

    all_titles = sorted(set(list(my_games.keys()) + list(their_games.keys())))

    comparison = []
    for title in all_titles:
        mine   = my_games.get(title)
        theirs = their_games.get(title)
        comparison.append({
            'title':  title,
            'mine':   mine,
            'theirs': theirs,
            'cover':  (mine or theirs).cover_url if (mine or theirs) else '',
        })

    both_played = [c for c in comparison if c['mine'] and c['theirs'] and c['mine'].rating and c['theirs'].rating]

    return render(request, 'games/compare.html', {
        'other': other,
        'comparison': comparison,
        'both_played': both_played,
        'my_count': len(my_games),
        'their_count': len(their_games),
        'shared_count': sum(1 for c in comparison if c['mine'] and c['theirs']),
    })


# ── AMIGOS ────────────────────────────────────────────────────────────────────

@login_required
def friends_list(request):
    search = request.GET.get('q', '').strip()

    friends = Friendship.objects.filter(
        from_user=request.user, status='accepted'
    ).select_related('to_user__profile')

    pending_sent = Friendship.objects.filter(
        from_user=request.user, status='pending'
    ).select_related('to_user')

    pending_received = Friendship.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('from_user__profile')

    # Busca de usuários
    search_results = []
    if search and len(search) >= 2:
        friend_ids  = list(friends.values_list('to_user_id', flat=True))
        pending_ids = list(pending_sent.values_list('to_user_id', flat=True))
        exclude_ids = friend_ids + pending_ids + [request.user.id]
        search_results = User.objects.filter(
            username__icontains=search
        ).exclude(id__in=exclude_ids).select_related('profile')[:10]

    return render(request, 'games/friends.html', {
        'friends': friends,
        'pending_sent': pending_sent,
        'pending_received': pending_received,
        'search_results': search_results,
        'search': search,
    })


@login_required
@require_POST
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user == request.user:
        messages.error(request, 'Você não pode se adicionar.')
        return redirect('friends_list')
    _, created = Friendship.objects.get_or_create(
        from_user=request.user, to_user=to_user,
        defaults={'status': 'pending'}
    )
    if created:
        messages.success(request, f'Solicitação enviada para {to_user.username}!')
    else:
        messages.info(request, 'Solicitação já enviada.')
    return redirect('friends_list')


@login_required
@require_POST
def accept_friend(request, username):
    from_user = get_object_or_404(User, username=username)
    friendship = get_object_or_404(Friendship, from_user=from_user, to_user=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    # Cria o inverso
    Friendship.objects.get_or_create(
        from_user=request.user, to_user=from_user,
        defaults={'status': 'accepted'}
    )
    messages.success(request, f'{from_user.username} agora é seu amigo! 🎮')
    return redirect('friends_list')


@login_required
@require_POST
def remove_friend(request, username):
    other = get_object_or_404(User, username=username)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=other) |
        Q(from_user=other, to_user=request.user)
    ).delete()
    messages.success(request, f'{other.username} removido dos amigos.')
    return redirect('friends_list')


# ── AI INSIGHTS ───────────────────────────────────────────────────────────────

@login_required
@require_POST
def generate_insights(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    insights = generate_ai_insights(game)
    game.ai_insights     = insights
    game.ai_generated_at = datetime.now(timezone.utc)
    game.save(update_fields=['ai_insights', 'ai_generated_at'])
    return JsonResponse({'insights': insights, 'success': True})


# ── RAWG API ──────────────────────────────────────────────────────────────────

@login_required
@require_GET
def rawg_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    return JsonResponse({'results': search_games_rawg(q)})


@login_required
@require_GET
def rawg_details(request):
    rawg_id = request.GET.get('id')
    if not rawg_id:
        return JsonResponse({'error': 'ID não informado'}, status=400)
    return JsonResponse(get_game_details_rawg(int(rawg_id)))


# ── CACHE STATS (admin helper) ────────────────────────────────────────────────

@login_required
def cache_stats(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    total   = RAWGCache.objects.count()
    fresh   = sum(1 for c in RAWGCache.objects.all() if c.is_fresh())
    expired = total - fresh
    return JsonResponse({'total': total, 'fresh': fresh, 'expired': expired})


# ── EXPORT ────────────────────────────────────────────────────────────────────

@login_required
def export_csv(request):
    games    = Game.objects.filter(user=request.user).select_related('platform')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="meus_jogos.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Título','Plataforma','Status','Nota','Horas','Início','Fim','Gênero','Dev','Ano','Metacritic','Review'])
    for g in games:
        writer.writerow([g.title, g.platform.name if g.platform else '', g.get_status_display(),
            g.rating or '', g.hours_played or '', g.start_date or '', g.end_date or '',
            g.genre, g.developer, g.release_year or '', g.metacritic_score or '', g.review])
    return response


@login_required
def export_pdf(request):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from io import BytesIO

        games  = Game.objects.filter(user=request.user).select_related('platform').order_by('title')
        buffer = BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []
        ts = ParagraphStyle('T', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#7c3aed'), spaceAfter=4)
        story.append(Paragraph(f'GameTracker — {request.user.username}', ts))
        story.append(Paragraph(f'Exportado em {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
        story.append(Spacer(1, 0.4*cm))
        data = [['Título','Plataforma','Status','Nota','Horas','Gênero']]
        for g in games:
            data.append([g.title[:38], g.platform.name if g.platform else '-',
                g.get_status_display(), str(g.rating) if g.rating else '-',
                str(g.hours_played) if g.hours_played else '-', g.genre[:22] if g.genre else '-'])
        table = Table(data, colWidths=[5.5*cm,2.8*cm,3*cm,1.8*cm,1.8*cm,2.8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#7c3aed')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,0),9),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#1f2937'),colors.HexColor('#111827')]),
            ('TEXTCOLOR',(0,1),(-1,-1),colors.white),
            ('FONTSIZE',(0,1),(-1,-1),8),
            ('PADDING',(0,0),(-1,-1),5),
            ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#374151')),
        ]))
        story.append(table)
        doc.build(story)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="meus_jogos.pdf"'
        return response
    except ImportError:
        messages.error(request, 'ReportLab não instalado: pip install reportlab')
        return redirect('game_list')
