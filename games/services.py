import re
import json
import requests
from django.conf import settings
from django.utils import timezone


# ── RAWG com cache ────────────────────────────────────────────────────────────

def search_games_rawg(query: str, page_size: int = 8) -> list:
    """Busca jogos na RAWG. Resultados de busca não são cacheados (lista dinâmica)."""
    try:
        resp = requests.get(
            'https://api.rawg.io/api/games',
            params={'key': settings.RAWG_API_KEY, 'search': query,
                    'page_size': page_size, 'ordering': '-rating'},
            timeout=8
        )
        resp.raise_for_status()
        results = []
        for g in resp.json().get('results', []):
            results.append({
                'rawg_id':          g.get('id'),
                'title':            g.get('name', ''),
                'cover_url':        g.get('background_image', ''),
                'release_year':     _year(g.get('released')),
                'metacritic_score': g.get('metacritic'),
                'genre':            ', '.join(x['name'] for x in g.get('genres', [])),
                'platforms':        [p['platform']['name'] for p in g.get('platforms', [])],
                'rating':           g.get('rating', 0),
            })
        return results
    except Exception as e:
        print(f'[RAWG] search error: {e}')
        return []


def get_game_details_rawg(rawg_id: int) -> dict:
    """
    Busca detalhes de um jogo pelo ID.
    Primeiro verifica o cache local (válido por 7 dias).
    Só chama a API se não houver cache ou se estiver expirado.
    """
    from .models import RAWGCache

    # Tenta pegar do cache
    try:
        cached = RAWGCache.objects.get(rawg_id=rawg_id)
        if cached.is_fresh(days=7):
            print(f'[RAWG Cache] HIT — {cached.title}')
            return {
                'rawg_id':          cached.rawg_id,
                'title':            cached.title,
                'cover_url':        cached.cover_url,
                'release_year':     cached.release_year,
                'metacritic_score': cached.metacritic_score,
                'genre':            cached.genre,
                'developer':        cached.developer,
                'description':      cached.description,
            }
    except RAWGCache.DoesNotExist:
        pass

    # Cache miss ou expirado — chama a API
    print(f'[RAWG Cache] MISS — buscando id={rawg_id}')
    try:
        resp = requests.get(
            f'https://api.rawg.io/api/games/{rawg_id}',
            params={'key': settings.RAWG_API_KEY},
            timeout=8
        )
        resp.raise_for_status()
        g = resp.json()
        data = {
            'rawg_id':          g.get('id'),
            'title':            g.get('name', ''),
            'cover_url':        g.get('background_image', ''),
            'release_year':     _year(g.get('released')),
            'metacritic_score': g.get('metacritic'),
            'genre':            ', '.join(x['name'] for x in g.get('genres', [])),
            'developer':        ', '.join(d['name'] for d in g.get('developers', [])),
            'description':      _strip(g.get('description', '')),
        }

        # Salva/atualiza no cache
        RAWGCache.objects.update_or_create(
            rawg_id=rawg_id,
            defaults={
                'title':            data['title'],
                'cover_url':        data['cover_url'] or '',
                'release_year':     data['release_year'],
                'metacritic_score': data['metacritic_score'],
                'genre':            data['genre'],
                'developer':        data['developer'],
                'description':      data['description'],
                'platforms_json':   json.dumps([p['platform']['name'] for p in g.get('platforms', [])]),
            }
        )
        return data
    except Exception as e:
        print(f'[RAWG] detail error: {e}')
        return {}


def _year(s):
    try:
        return int(str(s)[:4])
    except Exception:
        return None


def _strip(text):
    return re.sub(r'<[^>]+>', '', text).strip()


# ── AI (Groq first, OpenAI fallback) ──────────────────────────────────────────

def generate_ai_insights(game) -> str:
    prompt = _build_prompt(game)

    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    if groq_key and groq_key != 'SUA_GROQ_API_KEY_AQUI':
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            resp = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600, temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except ImportError:
            return '⚠️ Instale o Groq: pip install groq'
        except Exception as e:
            print(f'[Groq] {e}')

    oai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if oai_key and oai_key != 'SUA_OPENAI_API_KEY_AQUI':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=oai_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600, temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f'⚠️ Erro OpenAI: {e}'

    return '⚠️ Configure GROQ_API_KEY ou OPENAI_API_KEY no settings.py.'


def _build_prompt(game) -> str:
    ctx = ''
    if game.rating:     ctx += f'Nota: {game.rating}/10. '
    if game.status:     ctx += f'Status: {dict(game._meta.get_field("status").choices).get(game.status, game.status)}. '
    if game.hours_played: ctx += f'Horas: {game.hours_played}h. '
    if game.review:     ctx += f'Review: "{game.review[:300]}". '
    meta = ''
    if game.genre:           meta += f'Gênero: {game.genre}. '
    if game.developer:       meta += f'Dev: {game.developer}. '
    if game.release_year:    meta += f'Ano: {game.release_year}. '
    if game.metacritic_score: meta += f'Metacritic: {game.metacritic_score}. '
    return f"""Você é um especialista em games. Analise "{game.title}" e forneça insights em português.

{meta}{ctx}

Responda com:
1. **Por que vale jogar** (2-3 pontos únicos)
2. **Curiosidades** (fatos sobre desenvolvimento ou impacto cultural)
3. **Jogos similares** (3 recomendações com breve justificativa)
4. **Dica personalizada** (baseada no status/nota)

Máximo 400 palavras."""
