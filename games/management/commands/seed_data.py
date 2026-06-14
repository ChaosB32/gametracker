from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Platform, Tag, Game
from datetime import date


class Command(BaseCommand):
    help = 'Popula plataformas, tags, usuário de teste e 10 jogos de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('\n🎮 Iniciando seed do GameTracker v2...\n')

        # ── Plataformas ──────────────────────────────────────────────────────
        platforms_data = [
            ('PC', 'monitor'), ('PlayStation 5', 'ps'), ('PlayStation 4', 'ps'),
            ('Xbox Series X/S', 'xbox'), ('Xbox One', 'xbox'),
            ('Nintendo Switch', 'gamepad'), ('Mobile', 'mobile'),
            ('PlayStation 3', 'ps'), ('Xbox 360', 'xbox'), ('Nintendo 3DS', 'gamepad'),
        ]
        platforms = {}
        for name, icon in platforms_data:
            p, created = Platform.objects.get_or_create(name=name, defaults={'icon': icon})
            platforms[name] = p
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Plataforma: {name}'))

        # ── Tags ─────────────────────────────────────────────────────────────
        tags_data = [
            ('Multiplayer', '#06b6d4'), ('Single Player', '#8b5cf6'),
            ('História Épica', '#f59e0b'), ('Mundo Aberto', '#10b981'),
            ('Difícil', '#ef4444'), ('Relaxante', '#84cc16'),
            ('Curto', '#f97316'), ('Longo', '#6366f1'),
            ('Indie', '#14b8a6'), ('Cooperativo', '#3b82f6'),
            ('Roguelike', '#a855f7'), ('Remasterizado', '#ec4899'),
        ]
        tags = {}
        for name, color in tags_data:
            t, created = Tag.objects.get_or_create(name=name, defaults={'color': color})
            tags[name] = t
            if created:
                self.stdout.write(self.style.SUCCESS(f'  🏷️  Tag: {name}'))

        # ── Usuário de teste ─────────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username='jogador',
            defaults={'email': 'jogador@gametracker.com', 'first_name': 'Jogador', 'last_name': 'Teste'}
        )
        if created:
            user.set_password('gametracker123')
            user.save()
            self.stdout.write(self.style.SUCCESS('\n  👤 Usuário criado: jogador / gametracker123'))
        else:
            self.stdout.write(self.style.WARNING('\n  👤 Usuário "jogador" já existe'))

        # ── 10 Jogos de exemplo ──────────────────────────────────────────────
        games_data = [
            {
                'title': 'The Last of Us Part I',
                'platform': 'PC',
                'status': 'completed',
                'rating': 9.5,
                'genre': 'Ação, Aventura, Survival',
                'developer': 'Naughty Dog',
                'release_year': 2022,
                'metacritic_score': 89,
                'hours_played': 16.0,
                'start_date': date(2024, 1, 5),
                'end_date': date(2024, 1, 18),
                'review': 'Uma obra-prima emocional. A história de Joel e Ellie é simplesmente inesquecível. Gráficos e atuações impecáveis.',
                'cover_url': 'https://media.rawg.io/media/games/a5a/a5abaa1b5cc1567b026f3605da52fae6.jpg',
                'tags': ['Single Player', 'História Épica'],
            },
            {
                'title': 'Elden Ring',
                'platform': 'PC',
                'status': 'completed',
                'rating': 9.8,
                'genre': 'RPG, Ação, Mundo Aberto',
                'developer': 'FromSoftware',
                'release_year': 2022,
                'metacritic_score': 96,
                'hours_played': 87.5,
                'start_date': date(2023, 3, 10),
                'end_date': date(2023, 5, 2),
                'review': 'O melhor jogo que já joguei. Mundo vasto, lore profundo e desafio justo. George R.R. Martin e Miyazaki fizeram história.',
                'cover_url': 'https://media.rawg.io/media/games/b29/b294fdd866dcdb643e7bab370a552855.jpg',
                'tags': ['Single Player', 'Difícil', 'Mundo Aberto', 'Longo'],
            },
            {
                'title': 'Red Dead Redemption 2',
                'platform': 'PC',
                'status': 'completed',
                'rating': 10.0,
                'genre': 'Ação, Aventura, Mundo Aberto',
                'developer': 'Rockstar Games',
                'release_year': 2018,
                'metacritic_score': 97,
                'hours_played': 110.0,
                'start_date': date(2022, 8, 1),
                'end_date': date(2022, 11, 20),
                'review': 'Narrativa e imersão sem igual. Arthur Morgan é o melhor personagem da história dos games.',
                'cover_url': 'https://media.rawg.io/media/games/511/5118aff5091cb3efec399c808f8c598f.jpg',
                'tags': ['Single Player', 'História Épica', 'Mundo Aberto', 'Longo'],
            },
            {
                'title': 'Hollow Knight',
                'platform': 'PC',
                'status': 'completed',
                'rating': 9.2,
                'genre': 'Metroidvania, Plataforma, Indie',
                'developer': 'Team Cherry',
                'release_year': 2017,
                'metacritic_score': 87,
                'hours_played': 42.0,
                'start_date': date(2023, 6, 15),
                'end_date': date(2023, 7, 28),
                'review': 'Indie perfeito. Atmosfera sombria e única, exploração excelente e boss fights memoráveis.',
                'cover_url': 'https://media.rawg.io/media/games/4cf/4cfc6b7f1850590a4634b08bfab308ab.jpg',
                'tags': ['Single Player', 'Indie', 'Difícil'],
            },
            {
                'title': 'God of War (2018)',
                'platform': 'PC',
                'status': 'completed',
                'rating': 9.6,
                'genre': 'Ação, Aventura, RPG',
                'developer': 'Santa Monica Studio',
                'release_year': 2018,
                'metacritic_score': 94,
                'hours_played': 28.0,
                'start_date': date(2023, 9, 1),
                'end_date': date(2023, 9, 20),
                'review': 'A reinvenção de Kratos foi magistral. A relação pai e filho comove e a gameplay é impecável.',
                'cover_url': 'https://media.rawg.io/media/games/4be/4be6a6ad0364751a96229c56bf69be73.jpg',
                'tags': ['Single Player', 'História Épica'],
            },
            {
                'title': 'Cyberpunk 2077',
                'platform': 'PC',
                'status': 'playing',
                'rating': 8.5,
                'genre': 'RPG, Ação, Mundo Aberto',
                'developer': 'CD Projekt Red',
                'release_year': 2020,
                'metacritic_score': 86,
                'hours_played': 35.0,
                'start_date': date(2024, 10, 3),
                'review': 'Após os patches está excelente. Night City é incrível de explorar. A DLC Phantom Liberty é obrigatória.',
                'cover_url': 'https://media.rawg.io/media/games/26d/26d4437715bee60138dab4a7c8c59c92.jpg',
                'tags': ['Single Player', 'Mundo Aberto', 'Longo'],
            },
            {
                'title': 'Stardew Valley',
                'platform': 'PC',
                'status': 'paused',
                'rating': 8.8,
                'genre': 'Simulação, RPG, Indie',
                'developer': 'ConcernedApe',
                'release_year': 2016,
                'metacritic_score': 89,
                'hours_played': 55.0,
                'start_date': date(2024, 2, 10),
                'review': 'Relaxante e viciante. Perfeito para jogar sem estresse. Feito por uma única pessoa — inacreditável.',
                'cover_url': 'https://media.rawg.io/media/games/713/713269608dc8f2f40f5a670a14b2de94.jpg',
                'tags': ['Relaxante', 'Indie', 'Cooperativo'],
            },
            {
                'title': 'Hades',
                'platform': 'Nintendo Switch',
                'status': 'completed',
                'rating': 9.3,
                'genre': 'Roguelike, Ação, Indie',
                'developer': 'Supergiant Games',
                'release_year': 2020,
                'metacritic_score': 93,
                'hours_played': 60.0,
                'start_date': date(2023, 12, 26),
                'end_date': date(2024, 1, 22),
                'review': 'Melhor roguelike já feito. Narrativa integrada ao gameplay é genial. Impossível parar de jogar.',
                'cover_url': 'https://media.rawg.io/media/games/1f4/1f47a270b8f241f1b97ef82571bf6e36.jpg',
                'tags': ['Roguelike', 'Indie', 'Single Player'],
            },
            {
                'title': 'Zelda: Breath of the Wild',
                'platform': 'Nintendo Switch',
                'status': 'completed',
                'rating': 9.7,
                'genre': 'Aventura, Mundo Aberto, RPG',
                'developer': 'Nintendo',
                'release_year': 2017,
                'metacritic_score': 97,
                'hours_played': 72.0,
                'start_date': date(2022, 6, 1),
                'end_date': date(2022, 9, 14),
                'review': 'Redefiniu o gênero de mundo aberto. Liberdade de exploração sem igual. Um dos maiores jogos de todos os tempos.',
                'cover_url': 'https://media.rawg.io/media/games/cc6/cc65f577ec07c80c28bb7e41ebb4dc7e.jpg',
                'tags': ['Mundo Aberto', 'Single Player', 'Longo'],
            },
            {
                'title': 'Baldur\'s Gate 3',
                'platform': 'PC',
                'status': 'queued',
                'rating': None,
                'genre': 'RPG, Estratégia, Aventura',
                'developer': 'Larian Studios',
                'release_year': 2023,
                'metacritic_score': 96,
                'hours_played': None,
                'review': '',
                'cover_url': 'https://media.rawg.io/media/games/699/69907ecf13f172e9e144069769c3be73.jpg',
                'tags': ['Multiplayer', 'Cooperativo', 'Longo'],
            },
        ]

        created_count = 0
        for data in games_data:
            if Game.objects.filter(user=user, title=data['title']).exists():
                continue
            game_tags = data.pop('tags', [])
            platform_name = data.pop('platform')

            game = Game(user=user, platform=platforms.get(platform_name), **data)
            game.save()
            for tag_name in game_tags:
                if tag_name in tags:
                    game.tags.add(tags[tag_name])
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  🎮 Jogo: {game.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Seed concluído! {created_count} jogos criados.'))
        self.stdout.write(self.style.WARNING('\n📋 Login de teste:'))
        self.stdout.write(self.style.WARNING('   Usuário : jogador'))
        self.stdout.write(self.style.WARNING('   Senha   : gametracker123'))
        self.stdout.write('')


# Importar ao final do handle() — perfis para usuários criados
        from games.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': 'Jogador ávido de RPGs e aventuras. Sempre em busca do próximo grande jogo!',
                'location': 'São Paulo, Brasil',
                'favorite_genre': 'RPG, Aventura',
                'is_public': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('  👤 Perfil criado para: jogador'))

        # Segundo usuário para demonstrar comparação
        user2, created2 = User.objects.get_or_create(
            username='gamer2',
            defaults={'email': 'gamer2@gametracker.com'}
        )
        if created2:
            user2.set_password('gametracker123')
            user2.save()
            UserProfile.objects.get_or_create(
                user=user2,
                defaults={
                    'bio': 'Speedrunner nas horas vagas. Fã de jogos difíceis!',
                    'location': 'Rio de Janeiro, Brasil',
                    'favorite_genre': 'Roguelike, Ação',
                    'is_public': True,
                }
            )
            # Alguns jogos para o gamer2
            for title, status, rating in [
                ('Elden Ring', 'completed', 9.0),
                ('Hades', 'completed', 9.5),
                ('Hollow Knight', 'playing', None),
                ('Cyberpunk 2077', 'queued', None),
            ]:
                if not Game.objects.filter(user=user2, title=title).exists():
                    Game.objects.create(
                        user=user2, title=title,
                        status=status, rating=rating,
                        platform=platforms.get('PC'),
                    )
            self.stdout.write(self.style.SUCCESS('  👤 Usuário criado: gamer2 / gametracker123'))
