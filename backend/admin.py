from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
import json
from datetime import datetime

app = FastAPI(title="Admin Panel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(current_dir, "data.json")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profiles": [], "chats": [], "messages": []}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except:
        return {"profiles": [], "chats": [], "messages": []}


def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


@app.get("/")
async def admin_dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel - Ashoo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial; }
            body { background: #1a1a1a; color: white; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            header { text-align: center; margin-bottom: 30px; padding: 20px; background: #2a2a2a; border-radius: 10px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #2a2a2a; padding: 20px; border-radius: 10px; text-align: center; }
            .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
            .tab { padding: 12px 20px; background: #333; border: none; color: white; border-radius: 8px; cursor: pointer; }
            .tab.active { background: #ff6b9d; }
            .content { display: none; background: #2a2a2a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .content.active { display: block; }
            .profile-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
            .profile-card { background: #333; padding: 15px; border-radius: 10px; }
            .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; margin: 5px 2px; font-size: 14px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-danger { background: #dc3545; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-warning { background: #ffc107; color: black; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #ccc; }
            .form-group input, .form-group textarea, .form-group select { 
                width: 100%; padding: 10px; background: #333; border: 1px solid #555; 
                border-radius: 5px; color: white; font-size: 14px;
            }
            .form-group textarea { min-height: 80px; resize: vertical; }
            .chat-message { padding: 10px; margin: 5px 0; border-radius: 5px; }
            .user-message { background: #2d2d2d; margin-left: 20px; border-left: 3px solid #007bff; }
            .admin-message { background: #1e3a5c; margin-right: 20px; border-right: 3px solid #ff6b9d; }
            .message-sender { font-weight: bold; margin-bottom: 5px; }
            .back-btn { background: #6c757d; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 15px; }
            .photo-preview { display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }
            .photo-preview img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🛠️ Admin Panel - Ashoo</h1>
                <p>Полная версия с управлением анкетами</p>
            </header>

            <div class="stats">
                <div class="stat-card">
                    <h3>📊 Анкет</h3>
                    <p id="profiles-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>💬 Чатов</h3>
                    <p id="chats-count">0</p>
                </div>
                <div class="stat-card">
                    <h3>📨 Сообщений</h3>
                    <p id="messages-count">0</p>
                </div>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="showTab('profiles')">👥 Анкеты</button>
                <button class="tab" onclick="showTab('chats')">💬 Чаты</button>
                <button class="tab" onclick="showTab('add-profile')">➕ Добавить анкету</button>
            </div>

            <div id="profiles" class="content active">
                <h3>Управление анкетами</h3>
                <div id="profiles-list" class="profile-grid"></div>
            </div>

            <div id="chats" class="content">
                <h3>Управление чатами</h3>
                <div id="chats-list"></div>
            </div>

            <div id="add-profile" class="content">
                <h3>Добавить новую анкету</h3>
                <form id="add-profile-form">
                    <div class="form-group">
                        <label>Имя:</label>
                        <input type="text" id="name" required>
                    </div>
                    <div class="form-group">
                        <label>Возраст:</label>
                        <input type="number" id="age" required>
                    </div>
                    <div class="form-group">
                        <label>Город:</label>
                        <input type="text" id="city" required>
                    </div>
                    <div class="form-group">
                        <label>Описание:</label>
                        <textarea id="description" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Фото (URL через запятую):</label>
                        <textarea id="photos" required placeholder="https://picsum.photos/400/300?100, https://picsum.photos/400/300?101"></textarea>
                        <small style="color: #888;">Предпросмотр фото:</small>
                        <div class="photo-preview" id="photo-preview"></div>
                    </div>
                    <button type="submit" class="btn btn-success">➕ Добавить анкету</button>
                </form>
            </div>
        </div>

        <script>
            // Функции для переключения вкладок
            function showTab(tabName) {
                document.querySelectorAll('.content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');

                if (tabName === 'profiles') loadProfiles();
                if (tabName === 'chats') loadChats();
            }

            // Загрузка статистики
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    document.getElementById('profiles-count').textContent = stats.profiles_count;
                    document.getElementById('chats-count').textContent = stats.chats_count;
                    document.getElementById('messages-count').textContent = stats.messages_count;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            // Загрузка анкет
            async function loadProfiles() {
                try {
                    const response = await fetch('/api/admin/profiles');
                    const data = await response.json();
                    const list = document.getElementById('profiles-list');
                    list.innerHTML = '';

                    data.profiles.forEach(profile => {
                        const profileDiv = document.createElement('div');
                        profileDiv.className = 'profile-card';
                        profileDiv.innerHTML = `
                            <h4>${profile.name}, ${profile.age}</h4>
                            <p><strong>Город:</strong> ${profile.city}</p>
                            <p><strong>Описание:</strong> ${profile.description}</p>
                            <p><strong>Статус:</strong> ${profile.visible ? '✅ Видима' : '❌ Скрыта'}</p>
                            <p><strong>Фото:</strong> ${profile.photos.length} шт</p>
                            <div style="margin-top: 10px;">
                                <button class="btn btn-warning" onclick="toggleProfile(${profile.id}, ${!profile.visible})">
                                    ${profile.visible ? '👁️ Скрыть' : '👁️ Показать'}
                                </button>
                                <button class="btn btn-danger" onclick="deleteProfile(${profile.id})">
                                    🗑️ Удалить
                                </button>
                            </div>
                        `;
                        list.appendChild(profileDiv);
                    });

                    loadStats();
                } catch (error) {
                    console.error('Error loading profiles:', error);
                }
            }

            // Загрузка чатов
            async function loadChats() {
                try {
                    const response = await fetch('/api/admin/chats');
                    const data = await response.json();
                    const list = document.getElementById('chats-list');
                    list.innerHTML = '';

                    if (data.chats.length === 0) {
                        list.innerHTML = '<p>Нет активных чатов</p>';
                        return;
                    }

                    data.chats.forEach(chat => {
                        const chatDiv = document.createElement('div');
                        chatDiv.className = 'profile-card';
                        chatDiv.innerHTML = `
                            <h4>💬 Чат #${chat.id}</h4>
                            <p><strong>Анкета ID:</strong> ${chat.profile_id}</p>
                            <p><strong>Создан:</strong> ${new Date(chat.created_at).toLocaleString()}</p>
                            <button class="btn btn-primary" onclick="openChat(${chat.profile_id})">
                                💭 Открыть чат
                            </button>
                        `;
                        list.appendChild(chatDiv);
                    });
                } catch (error) {
                    console.error('Error loading chats:', error);
                }
            }

            // Переключение видимости анкеты
            async function toggleProfile(profileId, visible) {
                if (!confirm(visible ? 'Показать анкету?' : 'Скрыть анкету?')) return;

                try {
                    await fetch(`/api/admin/profiles/${profileId}/toggle`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ visible: visible })
                    });
                    loadProfiles();
                } catch (error) {
                    console.error('Error toggling profile:', error);
                    alert('Ошибка при изменении анкеты');
                }
            }

            // Удаление анкеты
            async function deleteProfile(profileId) {
                if (!confirm('❌ Удалить анкету? Это действие нельзя отменить!')) return;

                try {
                    const response = await fetch(`/api/admin/profiles/${profileId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        alert('✅ Анкета удалена!');
                        loadProfiles();
                    } else {
                        alert('❌ Ошибка при удалении анкеты');
                    }
                } catch (error) {
                    console.error('Error deleting profile:', error);
                    alert('❌ Ошибка при удалении анкеты');
                }
            }

            // Открытие чата
            async function openChat(profileId) {
                try {
                    const response = await fetch(`/api/admin/chats/${profileId}/messages`);
                    const messages = await response.json();

                    const list = document.getElementById('chats-list');
                    list.innerHTML = `
                        <button class="back-btn" onclick="loadChats()">← Назад к списку чатов</button>
                        <div class="profile-card">
                            <h3>💬 Чат с анкетой #${profileId}</h3>
                            <div id="chat-messages" style="max-height: 400px; overflow-y: auto; margin: 15px 0;">
                                ${messages.messages.map(msg => `
                                    <div class="chat-message ${msg.is_from_user ? 'user-message' : 'admin-message'}">
                                        <div class="message-sender">
                                            ${msg.is_from_user ? '👤 Пользователь' : '🛠️ Админ'}:
                                        </div>
                                        <div>${msg.text}</div>
                                        <small style="color: #888; font-size: 12px;">
                                            ${new Date(msg.created_at).toLocaleString()}
                                        </small>
                                    </div>
                                `).join('')}
                            </div>
                            <div>
                                <h4>✍️ Ответить от имени анкеты:</h4>
                                <textarea id="reply-text" rows="3" style="width: 100%; margin-bottom: 10px; padding: 10px; background: #333; color: white; border: 1px solid #555; border-radius: 5px;"></textarea>
                                <button class="btn btn-primary" onclick="sendReply(${profileId})">
                                    📤 Отправить ответ
                                </button>
                            </div>
                        </div>
                    `;

                    // Прокрутка вниз
                    const chatMessages = document.getElementById('chat-messages');
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                } catch (error) {
                    console.error('Error opening chat:', error);
                }
            }

            // Отправка ответа
            async function sendReply(profileId) {
                const text = document.getElementById('reply-text').value.trim();
                if (!text) {
                    alert('Введите текст сообщения');
                    return;
                }

                try {
                    await fetch(`/api/admin/chats/${profileId}/reply`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: text })
                    });

                    document.getElementById('reply-text').value = '';
                    openChat(profileId); // Перезагружаем чат
                } catch (error) {
                    console.error('Error sending reply:', error);
                    alert('Ошибка при отправке сообщения');
                }
            }

            // Предпросмотр фото
            document.getElementById('photos').addEventListener('input', function() {
                const preview = document.getElementById('photo-preview');
                const urls = this.value.split(',').map(url => url.trim()).filter(url => url);

                preview.innerHTML = '';
                urls.forEach(url => {
                    if (url) {
                        const img = document.createElement('img');
                        img.src = url;
                        img.onerror = function() {
                            this.style.display = 'none';
                        };
                        preview.appendChild(img);
                    }
                });
            });

            // Обработчик формы добавления анкеты
            document.getElementById('add-profile-form').addEventListener('submit', async function(e) {
                e.preventDefault();

                const formData = {
                    name: document.getElementById('name').value,
                    age: parseInt(document.getElementById('age').value),
                    city: document.getElementById('city').value,
                    description: document.getElementById('description').value,
                    photos: document.getElementById('photos').value.split(',').map(url => url.trim()).filter(url => url)
                };

                // Валидация
                if (formData.photos.length === 0) {
                    alert('Добавьте хотя бы одно фото');
                    return;
                }

                if (formData.age < 18 || formData.age > 100) {
                    alert('Возраст должен быть от 18 до 100 лет');
                    return;
                }

                try {
                    const response = await fetch('/api/admin/profiles', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        alert('✅ Анкета успешно добавлена!');
                        this.reset();
                        document.getElementById('photo-preview').innerHTML = '';
                        showTab('profiles');
                    } else {
                        alert('❌ Ошибка при добавлении анкеты');
                    }
                } catch (error) {
                    console.error('Error adding profile:', error);
                    alert('❌ Ошибка при добавлении анкеты');
                }
            });

            // Загружаем анкеты при старте
            loadProfiles();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# API endpoints
@app.get("/api/admin/profiles")
async def get_admin_profiles():
    data = load_data()
    return {"profiles": data["profiles"]}


@app.post("/api/admin/profiles")
async def create_profile(profile: dict):
    data = load_data()

    # Находим максимальный ID
    max_id = max([p["id"] for p in data["profiles"]]) if data["profiles"] else 0

    new_profile = {
        "id": max_id + 1,
        "name": profile["name"],
        "age": profile["age"],
        "city": profile["city"],
        "description": profile["description"],
        "photos": profile["photos"],
        "visible": True,
        "created_at": datetime.now().isoformat()
    }

    data["profiles"].append(new_profile)
    save_data(data)
    return {"status": "created", "profile": new_profile}


@app.post("/api/admin/profiles/{profile_id}/toggle")
async def toggle_profile(profile_id: int, visible_data: dict):
    data = load_data()
    profile = next((p for p in data["profiles"] if p["id"] == profile_id), None)
    if profile:
        profile["visible"] = visible_data["visible"]
        save_data(data)
    return {"status": "updated"}


@app.delete("/api/admin/profiles/{profile_id}")
async def delete_profile(profile_id: int):
    data = load_data()

    # Удаляем анкету
    data["profiles"] = [p for p in data["profiles"] if p["id"] != profile_id]

    # Находим чаты связанные с этой анкетой
    profile_chats = [c for c in data["chats"] if c["profile_id"] == profile_id]
    chat_ids = [c["id"] for c in profile_chats]

    # Удаляем чаты
    data["chats"] = [c for c in data["chats"] if c["profile_id"] != profile_id]

    # Удаляем сообщения из этих чатов
    data["messages"] = [m for m in data["messages"] if m["chat_id"] not in chat_ids]

    save_data(data)
    return {"status": "deleted"}


@app.get("/api/admin/chats")
async def get_admin_chats():
    data = load_data()
    return {"chats": data["chats"]}


@app.get("/api/admin/chats/{profile_id}/messages")
async def get_chat_messages_admin(profile_id: int):
    data = load_data()
    chat = next((c for c in data["chats"] if c["profile_id"] == profile_id), None)
    if not chat:
        return {"messages": []}
    messages = [m for m in data["messages"] if m["chat_id"] == chat["id"]]
    return {"messages": messages}


@app.post("/api/admin/chats/{profile_id}/reply")
async def send_admin_reply(profile_id: int, message: dict):
    data = load_data()

    chat = next((c for c in data["chats"] if c["profile_id"] == profile_id), None)
    if not chat:
        chat = {"id": len(data["chats"]) + 1, "profile_id": profile_id}
        data["chats"].append(chat)

    new_message = {
        "id": len(data["messages"]) + 1,
        "chat_id": chat["id"],
        "text": message["text"],
        "is_from_user": False,
        "created_at": datetime.now().isoformat()
    }
    data["messages"].append(new_message)
    save_data(data)
    return {"status": "sent"}


if __name__ == "__main__":
    print("🛠️ Admin panel: http://localhost:8002")
    print("✅ Полная версия с добавлением и удалением анкет")
    uvicorn.run(app, host="0.0.0.0", port=8002, access_log=False)