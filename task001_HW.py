# Напишите RESTful API по желанию с методами GET, POST, PUT, DELETE
# Для отображения данных по GET-запросам использовать шаблоны Jinja2
# Вывод информации о песнях через шаблонизатор Jinja

import os
import json
from pathlib import Path
import aiofiles
import uvicorn
from pydantic import TypeAdapter
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from pydantic_models import video  # Предполагается, что у вас есть модуль video с определением класса video

BASE_DIR = Path(__file__).resolve().parent
json_file = os.path.join(BASE_DIR, 'data.json')

if not os.path.exists(json_file):
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

with open(json_file, encoding='utf-8') as f:
    json_data = json.load(f)

app = FastAPI()
templates = Jinja2Templates('./templates')
type_adapter = TypeAdapter(video)
films: list[video] = [type_adapter.validate_python(video) for video in json_data]


async def commit_changes():
    async with aiofiles.open(json_file, 'w', encoding='utf-8') as f:
        json_films = [film.model_dump(mode='json') for film in films]
        content = json.dumps(json_films, ensure_ascii=False, indent=2)
        await f.write(content)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        'index.html', {'request': request, 'films': films}
    )


@app.post('/films/')
async def add_video(new_video: video):
    films.append(new_video)
    await commit_changes()
    return new_video


@app.get('/films/{video_id}', response_class=HTMLResponse)
async def get_video(request: Request, video_id: int):
    filtered_videos = [film for film in films if film.id == video_id]

    if not filtered_videos:
        current_video = None
    else:
        current_video = filtered_videos[0]

    return templates.TemplateResponse(
        'video.html', {'request': request, 'current_video': current_video}
    )


@app.put('/films/{video_id}')
async def update_video(video_id: int, new_video: video):
    filtered_videos = [film for film in films if film.id == video_id]

    if not filtered_videos:
        return {'updated': False}

    current_video = filtered_videos[0]

    current_video.name = new_video.name
    current_video.author = new_video.author
    current_video.description = new_video.description
    current_video.genre = new_video.genre

    await commit_changes()

    return {'updated': True, 'video': new_video}


@app.delete('/films/{video_id}')
async def delete_video(video_id: int):
    filtered_videos = [film for film in films if film.id == video_id]

    if not filtered_videos:
        return {'deleted': False}

    current_video = filtered_videos[0]
    films.remove(current_video)

    await commit_changes()

    return {'deleted': True, 'video': current_video}

if __name__ == "__main__":
    uvicorn.run("task001_HW:app", port=8080, reload=True)
