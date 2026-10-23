import sys
import json
import math
import random
import time
import urllib.request
from pathlib import Path

import yt_dlp
import vlc

from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QSlider, QMessageBox,
    QProgressBar, QFrame, QComboBox
)

APP_DIR = Path.home() / "MusicPlayer"
CACHE_DIR = APP_DIR / "cache"
COVERS_DIR = APP_DIR / "covers"
DATA_FILE = APP_DIR / "data.json"

for folder in (APP_DIR, CACHE_DIR, COVERS_DIR):
    folder.mkdir(parents=True, exist_ok=True)

GREEN = "#1ed760"
BG = "#121212"
PANEL = "#181818"
CARD = "#242424"
MUTED = "#a7a7a7"


LANGUAGE_NAMES = {
    "pl": "Polski",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

TRANSLATIONS = {
    "en": {
        "Szukaj": "Search", "Kolejka": "Queue", "Biblioteka": "Library",
        "Ulubione": "Favorites", "Playlisty": "Playlists",
        "Czego chcesz posłuchać?": "What do you want to listen to?",
        "Odkrywaj muzykę": "Discover music", "Wyszukaj utwór, aby rozpocząć.": "Search for a track to get started.",
        "Szukaj utworu, aby rozpocząć.": "Search for a track to get started.",
        "LOKALNY CACHE": "LOCAL CACHE", "utworów": "tracks", "Play": "Play",
        "+ Kolejka": "+ Queue", "♡ Ulubione": "♡ Favorites",
        "Usuń z kolejki": "Remove from queue", "Usuń z biblioteki": "Remove from library",
        "+ Do playlisty": "+ Add to playlist", "+ Nowa playlista": "+ New playlist",
        "Usuń playlistę": "Delete playlist", "Usuń z playlisty": "Remove from playlist",
        "Nic nie jest odtwarzane": "Nothing is playing", "Wybierz utwór": "Choose a track",
        "Losowe odtwarzanie": "Shuffle", "Tryb zapętlania": "Repeat mode",
        "Głośność": "Volume", "Kolejka odtwarzania": "Playback queue",
        "Twoja biblioteka": "Your library", "Ulubione utwory": "Favorite tracks",
        "Twoje playlisty": "Your playlists", "Playlista": "Playlist",
        "Wpisz tytuł utworu.": "Enter a track title.", "Wyszukiwanie w YouTube...": "Searching YouTube...",
        "Odtwarzanie muzyki": "Playing music", "Pauza": "Paused",
        "Błąd odtwarzania.": "Playback error.", "Wystąpił błąd.": "An error occurred.",
        "Pobieranie audio...": "Downloading audio...", "Uruchamianie utworu...": "Starting track...",
        "Koniec kolejki.": "End of queue.", "Kolejka jest pusta.": "The queue is empty.",
        "Losowanie włączone.": "Shuffle enabled.", "Losowanie wyłączone.": "Shuffle disabled.",
        "Znaleziono: ": "Found: ", " utworów": " tracks", "Nieznany tytuł": "Unknown title",
        "Nieznany wykonawca": "Unknown artist", "Nieznany utwór": "Unknown track",
        "Najpierw zaznacz utwór.": "Select a track first.", "Zaznacz utwór na liście.": "Select a track from the list.",
        "Dodano do kolejki.": "Added to queue.", "Usunięto utwór z kolejki.": "Removed track from queue.",
        "Dodano do ulubionych ♥": "Added to favorites ♥", "Usunięto z ulubionych.": "Removed from favorites.",
        "Nie masz jeszcze playlisty. Czy chcesz ją teraz utworzyć?": "You don't have a playlist yet. Create one now?",
        "Nazwa playlisty:": "Playlist name:", "Nowa playlista": "New playlist",
        "Playlista o tej nazwie już istnieje.": "A playlist with this name already exists.",
        "Zaznacz playlistę do usunięcia.": "Select a playlist to delete.",
        "Czy na pewno usunąć playlistę „{name}”? Utwory pozostaną w bibliotece.": "Delete playlist “{name}”? Tracks will remain in your library.",
        "Zaznacz utwór w bibliotece.": "Select a track in the library.",
        "Zaznacz utwór na playliście.": "Select a track in the playlist.",
        "Ten utwór już jest na tej playliście.": "This track is already in this playlist.",
        "Wybierz playlistę:": "Choose a playlist:", "Dodaj do playlisty": "Add to playlist",
        "Usuń z biblioteki": "Remove from library", "Plik MP3 i utwór w playlistach pozostaną bez zmian.": "The MP3 file and playlist entries will remain unchanged.",
        "Pobieranie już trwa. Poczekaj chwilę.": "A download is already in progress. Please wait.",
    },
    "es": {
        "Szukaj": "Buscar", "Kolejka": "Cola", "Biblioteka": "Biblioteca", "Ulubione": "Favoritos", "Playlisty": "Listas",
        "Czego chcesz posłuchać?": "¿Qué quieres escuchar?", "Odkrywaj muzykę": "Descubrir música",
        "Wyszukaj utwór, aby rozpocząć.": "Busca una canción para empezar.", "Szukaj utworu, aby rozpocząć.": "Busca una canción para empezar.",
        "LOKALNY CACHE": "CACHÉ LOCAL", "utworów": "canciones", "Play": "Reproducir", "+ Kolejka": "+ Cola",
        "♡ Ulubione": "♡ Favoritos", "Usuń z kolejki": "Quitar de la cola", "Usuń z biblioteki": "Quitar de la biblioteca",
        "+ Do playlisty": "+ Añadir a lista", "+ Nowa playlista": "+ Nueva lista", "Usuń playlistę": "Eliminar lista",
        "Usuń z playlisty": "Quitar de la lista", "Nic nie jest odtwarzane": "No se está reproduciendo nada", "Wybierz utwór": "Elige una canción",
        "Losowe odtwarzanie": "Aleatorio", "Tryb zapętlania": "Modo repetir", "Głośność": "Volumen",
        "Kolejka odtwarzania": "Cola de reproducción", "Twoja biblioteka": "Tu biblioteca", "Ulubione utwory": "Canciones favoritas",
        "Twoje playlisty": "Tus listas", "Playlista": "Lista", "Wpisz tytuł utworu.": "Escribe el título de una canción.",
        "Wyszukiwanie w YouTube...": "Buscando en YouTube...", "Odtwarzanie muzyki": "Reproduciendo música", "Pauza": "Pausa",
        "Błąd odtwarzania.": "Error de reproducción.", "Wystąpił błąd.": "Se ha producido un error.", "Pobieranie audio...": "Descargando audio...",
        "Uruchamianie utworu...": "Iniciando canción...", "Koniec kolejki.": "Fin de la cola.", "Kolejka jest pusta.": "La cola está vacía.",
        "Losowanie włączone.": "Reproducción aleatoria activada.", "Losowanie wyłączone.": "Reproducción aleatoria desactivada.",
        "Znaleziono: ": "Encontradas: ", " utworów": " canciones", "Nieznany tytuł": "Título desconocido", "Nieznany wykonawca": "Artista desconocido",
        "Nieznany utwór": "Canción desconocida", "Najpierw zaznacz utwór.": "Primero selecciona una canción.", "Zaznacz utwór na liście.": "Selecciona una canción de la lista.",
        "Dodano do kolejki.": "Añadida a la cola.", "Usunięto utwór z kolejki.": "Canción eliminada de la cola.", "Dodano do ulubionych ♥": "Añadida a favoritos ♥", "Usunięto z ulubionych.": "Eliminada de favoritos.",
    },
    "fr": {
        "Szukaj": "Rechercher", "Kolejka": "File d’attente", "Biblioteka": "Bibliothèque", "Ulubione": "Favoris", "Playlisty": "Playlists",
        "Czego chcesz posłuchać?": "Que voulez-vous écouter ?", "Odkrywaj muzykę": "Découvrir la musique", "Wyszukaj utwór, aby rozpocząć.": "Recherchez un morceau pour commencer.",
        "Szukaj utworu, aby rozpocząć.": "Recherchez un morceau pour commencer.", "LOKALNY CACHE": "CACHE LOCAL", "utworów": "morceaux",
        "Play": "Lire", "+ Kolejka": "+ File", "♡ Ulubione": "♡ Favoris", "Usuń z kolejki": "Retirer de la file", "Usuń z biblioteki": "Retirer de la bibliothèque",
        "+ Do playlisty": "+ Ajouter à une playlist", "+ Nowa playlista": "+ Nouvelle playlist", "Usuń playlistę": "Supprimer la playlist", "Usuń z playlisty": "Retirer de la playlist",
        "Nic nie jest odtwarzane": "Aucune lecture en cours", "Wybierz utwór": "Choisissez un morceau", "Losowe odtwarzanie": "Lecture aléatoire", "Tryb zapętlania": "Mode répétition",
        "Głośność": "Volume", "Kolejka odtwarzania": "File de lecture", "Twoja biblioteka": "Votre bibliothèque", "Ulubione utwory": "Morceaux favoris", "Twoje playlisty": "Vos playlists",
        "Playlista": "Playlist", "Wpisz tytuł utworu.": "Saisissez le titre d’un morceau.", "Wyszukiwanie w YouTube...": "Recherche sur YouTube...", "Odtwarzanie muzyki": "Lecture de musique",
        "Pauza": "Pause", "Błąd odtwarzania.": "Erreur de lecture.", "Wystąpił błąd.": "Une erreur est survenue.", "Pobieranie audio...": "Téléchargement audio...", "Uruchamianie utworu...": "Démarrage du morceau...",
        "Koniec kolejki.": "Fin de la file.", "Kolejka jest pusta.": "La file est vide.", "Losowanie włączone.": "Lecture aléatoire activée.", "Losowanie wyłączone.": "Lecture aléatoire désactivée.",
        "Znaleziono: ": "Trouvé : ", " utworów": " morceaux", "Nieznany tytuł": "Titre inconnu", "Nieznany wykonawca": "Artiste inconnu", "Nieznany utwór": "Morceau inconnu",
        "Najpierw zaznacz utwór.": "Sélectionnez d’abord un morceau.", "Zaznacz utwór na liście.": "Sélectionnez un morceau dans la liste.", "Dodano do kolejki.": "Ajouté à la file.", "Usunięto utwór z kolejki.": "Morceau retiré de la file.",
    },
    "de": {
        "Szukaj": "Suchen", "Kolejka": "Warteschlange", "Biblioteka": "Bibliothek", "Ulubione": "Favoriten", "Playlisty": "Playlists",
        "Czego chcesz posłuchać?": "Was möchtest du hören?", "Odkrywaj muzykę": "Musik entdecken", "Wyszukaj utwór, aby rozpocząć.": "Suche einen Titel, um loszulegen.",
        "Szukaj utworu, aby rozpocząć.": "Suche einen Titel, um loszulegen.", "LOKALNY CACHE": "LOKALER CACHE", "utworów": "Titel", "Play": "Abspielen",
        "+ Kolejka": "+ Warteschlange", "♡ Ulubione": "♡ Favoriten", "Usuń z kolejki": "Aus Warteschlange entfernen", "Usuń z biblioteki": "Aus Bibliothek entfernen",
        "+ Do playlisty": "+ Zur Playlist", "+ Nowa playlista": "+ Neue Playlist", "Usuń playlistę": "Playlist löschen", "Usuń z playlisty": "Aus Playlist entfernen",
        "Nic nie jest odtwarzane": "Keine Wiedergabe", "Wybierz utwór": "Titel auswählen", "Losowe odtwarzanie": "Zufallswiedergabe", "Tryb zapętlania": "Wiederholungsmodus",
        "Głośność": "Lautstärke", "Kolejka odtwarzania": "Wiedergabewarteschlange", "Twoja biblioteka": "Deine Bibliothek", "Ulubione utwory": "Lieblingstitel", "Twoje playlisty": "Deine Playlists",
        "Playlista": "Playlist", "Wpisz tytuł utworu.": "Gib einen Titel ein.", "Wyszukiwanie w YouTube...": "Suche auf YouTube...", "Odtwarzanie muzyki": "Musikwiedergabe", "Pauza": "Pause",
        "Błąd odtwarzania.": "Wiedergabefehler.", "Wystąpił błąd.": "Ein Fehler ist aufgetreten.", "Pobieranie audio...": "Audio wird heruntergeladen...", "Uruchamianie utworu...": "Titel wird gestartet...",
        "Koniec kolejki.": "Ende der Warteschlange.", "Kolejka jest pusta.": "Die Warteschlange ist leer.", "Losowanie włączone.": "Zufallswiedergabe aktiviert.", "Losowanie wyłączone.": "Zufallswiedergabe deaktiviert.",
        "Znaleziono: ": "Gefunden: ", " utworów": " Titel", "Nieznany tytuł": "Unbekannter Titel", "Nieznany wykonawca": "Unbekannter Künstler", "Nieznany utwór": "Unbekannter Titel",
        "Najpierw zaznacz utwór.": "Wähle zuerst einen Titel aus.", "Zaznacz utwór na liście.": "Wähle einen Titel aus der Liste aus.", "Dodano do kolejki.": "Zur Warteschlange hinzugefügt.", "Usunięto utwór z kolejki.": "Titel aus Warteschlange entfernt.",
    },
}

def load_data():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "library": data.get("library", []),
            "favorites": data.get("favorites", []),
            "queue": data.get("queue", []),
            "playlists": data.get("playlists", []),
            "language": data.get("language", "pl"),
        }
    except (OSError, ValueError):
        return {"library": [], "favorites": [], "queue": [], "playlists": [], "language": "pl"}


def save_data(data):
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp.replace(DATA_FILE)


def format_time(ms):
    if ms is None or ms < 0:
        return "0:00"
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    if minutes >= 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


class SearchWorker(QThread):
    results_ready = Signal(list)
    error = Signal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "skip_download": True,
                "ignoreerrors": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(
                    f"ytsearch10:{self.query}",
                    download=False,
                )

            tracks = []
            for item in (data or {}).get("entries", []):
                if not item or not item.get("id"):
                    continue

                video_id = str(item["id"])
                tracks.append({
                    "id": video_id,
                    "title": item.get("title") or "Nieznany tytuł",
                    "channel": (
                        item.get("channel")
                        or item.get("uploader")
                        or "Nieznany wykonawca"
                    ),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": item.get("thumbnail") or "",
                })

            self.results_ready.emit(tracks)
        except Exception as exc:
            self.error.emit(str(exc))


class DownloadWorker(QThread):
    completed = Signal(str)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, track):
        super().__init__()
        self.track = track

    def run(self):
        target = CACHE_DIR / f"{self.track['id']}.mp3"

        if target.exists() and target.stat().st_size > 0:
            self.completed.emit(str(target))
            return

        def hook(data):
            if data.get("status") == "downloading":
                percent = data.get("_percent_str", "").strip()
                self.progress.emit(f"Pobieranie: {percent}")
            elif data.get("status") == "finished":
                self.progress.emit("Konwertowanie audio...")

        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(CACHE_DIR / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.track["url"]])

            if target.exists() and target.stat().st_size > 0:
                self.completed.emit(str(target))
            else:
                self.error.emit(
                    "Nie znaleziono MP3. Sprawdź instalację FFmpeg."
                )
        except Exception as exc:
            self.error.emit(str(exc))


class CoverWorker(QThread):
    completed = Signal(str, str)

    def __init__(self, track):
        super().__init__()
        self.track_id = track["id"]
        self.url = track.get("thumbnail", "")

    def run(self):
        target = COVERS_DIR / f"{self.track_id}.jpg"

        if target.exists() and target.stat().st_size > 0:
            self.completed.emit(self.track_id, str(target))
            return

        if not self.url.startswith("https://"):
            return

        try:
            request = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                if not response.headers.get(
                    "Content-Type", ""
                ).startswith("image/"):
                    return
                content = response.read(8 * 1024 * 1024 + 1)

            if len(content) > 8 * 1024 * 1024:
                return

            temp = target.with_suffix(".tmp")
            temp.write_bytes(content)
            temp.replace(target)
            self.completed.emit(self.track_id, str(target))
        except Exception:
            pass


class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(40)
        self.active = False
        self.started = time.monotonic()

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def set_active(self, active):
        self.active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        count = 42
        gap = 4
        bar_width = max(2, (self.width() - gap * (count - 1)) / count)
        elapsed = time.monotonic() - self.started

        for i in range(count):
            if self.active:
                wave = (
                    math.sin(elapsed * 4 + i * 0.45)
                    + math.sin(elapsed * 2.5 + i * 0.2)
                )
                ratio = 0.15 + 0.4 * abs(wave) / 2
            else:
                ratio = 0.1

            bar_height = max(3, int(self.height() * ratio))
            x = int(i * (bar_width + gap))
            y = int((self.height() - bar_height) / 2)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(GREEN))
            painter.drawRoundedRect(
                x, y, int(bar_width), bar_height, 2, 2
            )

        painter.end()

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
      
        self.setWindowTitle("Green Player 2.0")
        self.resize(1080, 740)
        self.setMinimumSize(800, 580)

        self.data = load_data()
        self.language = self.data.get("language", "pl")
        self.results = []
        self.visible_tracks = []
        self.view_mode = "search"
        self.active_playlist = None

        self.current_track = None
        self.current_path = None
        self.queue_index = -1

        self.shuffle = False
        self.repeat_mode = "off"
        self.handled_ended = False
        self.seeking = False

        self.search_worker = None
        self.download_worker = None
        self.cover_workers = []

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        self.build_ui()
        self.refresh_view("search")

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_player)
        self.timer.start()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        body = QHBoxLayout()
        body.setSpacing(10)
        root.addLayout(body, 1)

        # Boczny panel
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 18, 14, 14)
        side.setSpacing(10)

        logo = QLabel("● GREEN PLAYER")
        logo.setStyleSheet(
            f"color: {GREEN}; font-size: 17px; font-weight: bold;"
        )
        side.addWidget(logo)
        self.language_label = QLabel("Język / Language")
        self.language_label.setStyleSheet(f"color: {MUTED};")
        side.addWidget(self.language_label)
        self.language_combo = QComboBox()
        for code, label in LANGUAGE_NAMES.items():
            self.language_combo.addItem(label, code)
        language_index = self.language_combo.findData(self.language)
        self.language_combo.setCurrentIndex(max(0, language_index))
        self.language_combo.currentIndexChanged.connect(self.change_language)
        side.addWidget(self.language_combo)
        side.addSpacing(10)

        self.nav_search = self.nav_button(
            "⌕   Szukaj", lambda: self.refresh_view("search")
        )
        self.nav_queue = self.nav_button(
            "☷   Kolejka", lambda: self.refresh_view("queue")
        )
        self.nav_library = self.nav_button(
            "♫   Biblioteka", lambda: self.refresh_view("library")
        )
        self.nav_favorites = self.nav_button(
            "♥   Ulubione", lambda: self.refresh_view("favorites")
        )
        self.nav_playlists = self.nav_button(
            "▤   Playlisty", lambda: self.refresh_view("playlists")
        )

        for button in (
            self.nav_search,
            self.nav_queue,
            self.nav_library,
            self.nav_favorites,
            self.nav_playlists,
        ):
            side.addWidget(button)

        side.addStretch()

        self.cache_heading = QLabel("LOKALNY CACHE")
        side.addWidget(self.cache_heading)
        self.cache_count = QLabel("0 utworów")
        self.cache_count.setStyleSheet(f"color: {MUTED};")
        side.addWidget(self.cache_count)

        body.addWidget(sidebar)

        # Główna część
        main = QFrame()
        main.setObjectName("main")
        content = QVBoxLayout(main)
        content.setContentsMargins(20, 18, 20, 16)
        content.setSpacing(12)

        search_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Czego chcesz posłuchać?"
        )
        self.search_input.returnPressed.connect(self.search)
        search_row.addWidget(self.search_input, 1)

        self.search_button = QPushButton("Szukaj")
        self.search_button.clicked.connect(self.search)
        search_row.addWidget(self.search_button)

        content.addLayout(search_row)

        self.page_title = QLabel("Odkrywaj muzykę")
        self.page_title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )
        content.addWidget(self.page_title)

        self.status = QLabel("Wyszukaj utwór, aby rozpocząć.")
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {MUTED};")
        content.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(5)
        self.progress.hide()
        content.addWidget(self.progress)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        self.list_widget.itemDoubleClicked.connect(self._item_double_clicked)
        content.addWidget(self.list_widget, 1)

        actions = QHBoxLayout()

        self.play_button = QPushButton("▶  Play")
        self.play_button.clicked.connect(self.play_selected)
        actions.addWidget(self.play_button)

        self.add_queue_button = QPushButton("+ Kolejka")
        self.add_queue_button.clicked.connect(
            self.add_selected_to_queue
        )
        actions.addWidget(self.add_queue_button)

        self.favorite_button = QPushButton("♡ Ulubione")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        actions.addWidget(self.favorite_button)

        self.remove_button = QPushButton("Usuń z kolejki")
        self.remove_button.clicked.connect(
            self.remove_selected_from_queue
        )
        actions.addWidget(self.remove_button)

        self.remove_library_button = QPushButton("Usuń z biblioteki")
        self.remove_library_button.clicked.connect(
            self.remove_selected_from_library
        )
        actions.addWidget(self.remove_library_button)

        self.add_playlist_button = QPushButton("+ Do playlisty")
        self.add_playlist_button.clicked.connect(
            self.add_selected_to_playlist
        )
        actions.addWidget(self.add_playlist_button)

        self.create_playlist_button = QPushButton("+ Nowa playlista")
        self.create_playlist_button.clicked.connect(self.create_playlist)
        actions.addWidget(self.create_playlist_button)

        self.delete_playlist_button = QPushButton("Usuń playlistę")
        self.delete_playlist_button.clicked.connect(self.delete_selected_playlist)
        actions.addWidget(self.delete_playlist_button)

        self.remove_from_playlist_button = QPushButton("Usuń z playlisty")
        self.remove_from_playlist_button.clicked.connect(
            self.remove_selected_from_playlist
        )
        actions.addWidget(self.remove_from_playlist_button)

        content.addLayout(actions)
        body.addWidget(main, 1)

        # Dolny pasek odtwarzania
        bottom = QFrame()
        bottom.setObjectName("bottom")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(12, 10, 12, 10)
        bottom_layout.setSpacing(12)

        self.cover_label = QLabel("♫")
        self.cover_label.setFixedSize(76, 76)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet(
            f"background: {CARD}; color: {GREEN}; "
            "font-size: 32px; border-radius: 8px;"
        )
        bottom_layout.addWidget(self.cover_label)

        info = QVBoxLayout()
        self.now_title = QLabel("Nic nie jest odtwarzane")
        self.now_title.setWordWrap(True)
        self.now_title.setStyleSheet("font-weight: bold;")

        self.now_artist = QLabel("Wybierz utwór")
        self.now_artist.setStyleSheet(f"color: {MUTED};")

        info.addStretch()
        info.addWidget(self.now_title)
        info.addWidget(self.now_artist)
        info.addStretch()

        bottom_layout.addLayout(info, 2)

        playback = QVBoxLayout()
        buttons = QHBoxLayout()

        self.shuffle_button = QPushButton("🔀")
        self.shuffle_button.setToolTip("Losowe odtwarzanie")
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        buttons.addWidget(self.shuffle_button)

        self.previous_button = QPushButton("⏮")
        self.previous_button.clicked.connect(self.previous_track)
        buttons.addWidget(self.previous_button)

        self.pause_button = QPushButton("▶ / ⏸")
        self.pause_button.clicked.connect(self.toggle_pause)
        buttons.addWidget(self.pause_button)

        self.next_button = QPushButton("⏭")
        self.next_button.clicked.connect(self.next_track)
        buttons.addWidget(self.next_button)

        self.repeat_button = QPushButton("↻")
        self.repeat_button.setToolTip("Tryb zapętlania")
        self.repeat_button.clicked.connect(self.toggle_repeat)
        buttons.addWidget(self.repeat_button)

        playback.addLayout(buttons)

        time_row = QHBoxLayout()

        self.current_time = QLabel("0:00")
        self.total_time = QLabel("0:00")

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setEnabled(False)
        self.seek_slider.setTracking(False)
        self.seek_slider.sliderPressed.connect(self.begin_seek)
        self.seek_slider.sliderMoved.connect(self.preview_seek)
        self.seek_slider.sliderReleased.connect(self.finish_seek)

        time_row.addWidget(self.current_time)
        time_row.addWidget(self.seek_slider, 1)
        time_row.addWidget(self.total_time)

        playback.addLayout(time_row)
        bottom_layout.addLayout(playback, 4)

        volume = QVBoxLayout()
        self.volume_label = QLabel("Głośność")
        volume.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(
            self.set_volume
        )
        volume.addWidget(self.volume_slider)

        bottom_layout.addLayout(volume, 1)
        root.addWidget(bottom)

        self.visualizer = Visualizer()
        root.addWidget(self.visualizer)

        self.setStyleSheet(f"""
            QWidget {{
                background: {BG};
                color: white;
                font-size: 13px;
            }}
            QFrame#sidebar, QFrame#bottom, QFrame#main {{
                background: {PANEL};
                border-radius: 10px;
            }}
            QLineEdit, QListWidget {{
                background: {CARD};
                border: 1px solid #333;
                border-radius: 8px;
                padding: 9px;
                selection-background-color: #245d39;
            }}
            QPushButton {{
                background: #282828;
                border: none;
                border-radius: 7px;
                padding: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #383838;
            }}
            QProgressBar {{
                background: #333;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {GREEN};
            }}
            QSlider::groove:horizontal {{
                height: 5px;
                background: #444;
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {GREEN};
            }}
            QSlider::handle:horizontal {{
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
        """)
        self.apply_language()

    def tr(self, text):
        return TRANSLATIONS.get(self.language, {}).get(text, text)

    def change_language(self, _index):
        code = self.language_combo.currentData()
        if not code or code == self.language:
            return
        self.language = code
        self.data["language"] = code
        self.persist()
        self.apply_language()
        self.refresh_view(self.view_mode)

    def apply_language(self):
        self.setWindowTitle(f"Green Player 2.1 — {LANGUAGE_NAMES.get(self.language, 'Polski')}")
        self.language_label.setText(self.tr("Język / Language"))
        self.nav_search.setText("⌕   " + self.tr("Szukaj"))
        self.nav_queue.setText("☷   " + self.tr("Kolejka"))
        self.nav_library.setText("♫   " + self.tr("Biblioteka"))
        self.nav_favorites.setText("♥   " + self.tr("Ulubione"))
        self.nav_playlists.setText("▤   " + self.tr("Playlisty"))
        self.cache_heading.setText(self.tr("LOKALNY CACHE"))
        if not self.current_track:
            self.status.setText(self.tr("Wyszukaj utwór, aby rozpocząć."))
        self.search_input.setPlaceholderText(self.tr("Czego chcesz posłuchać?"))
        self.search_button.setText(self.tr("Szukaj"))
        self.add_queue_button.setText(self.tr("+ Kolejka"))
        self.favorite_button.setText(self.tr("♡ Ulubione"))
        self.remove_button.setText(self.tr("Usuń z kolejki"))
        self.remove_library_button.setText(self.tr("Usuń z biblioteki"))
        self.add_playlist_button.setText(self.tr("+ Do playlisty"))
        self.create_playlist_button.setText(self.tr("+ Nowa playlista"))
        self.delete_playlist_button.setText(self.tr("Usuń playlistę"))
        self.remove_from_playlist_button.setText(self.tr("Usuń z playlisty"))
        self.play_button.setText("▶  " + self.tr("Play"))
        self.now_title.setText(self.tr("Nic nie jest odtwarzane") if not self.current_track else self.current_track.get("title", self.tr("Nieznany utwór")))
        if not self.current_track:
            self.now_artist.setText(self.tr("Wybierz utwór"))
        self.shuffle_button.setToolTip(self.tr("Losowe odtwarzanie"))
        self.repeat_button.setToolTip(self.tr("Tryb zapętlania"))
        self.volume_label.setText(self.tr("Głośność"))
        self.refresh_view(self.view_mode)

    def nav_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet(
            "text-align: left; padding: 11px; background: transparent;"
        )
        button.clicked.connect(callback)
        return button

    def set_volume(self, value):
        self.player.audio_set_volume(value)

    def refresh_view(self, mode):
        self.view_mode = mode

        titles = {
            "search": "Odkrywaj muzykę",
            "queue": "Kolejka odtwarzania",
            "library": "Twoja biblioteka",
            "favorites": "Ulubione utwory",
            "playlists": "Twoje playlisty",
            "playlist_tracks": self.active_playlist or "Playlista",
        }
        self.page_title.setText(self.tr(titles[mode]))

        is_search = mode == "search"
        is_playlist_list = mode == "playlists"
        self.search_input.setVisible(is_search)
        self.search_button.setVisible(is_search)
        self.add_queue_button.setVisible(mode not in ("queue", "playlists"))
        self.remove_button.setVisible(mode == "queue")
        self.remove_library_button.setVisible(mode == "library")
        self.add_playlist_button.setVisible(
            mode in ("search", "library", "favorites", "queue", "playlist_tracks")
        )
        self.create_playlist_button.setVisible(is_playlist_list)
        self.delete_playlist_button.setVisible(is_playlist_list)
        self.remove_from_playlist_button.setVisible(mode == "playlist_tracks")

        if mode == "search":
            tracks = self.results
        elif mode == "queue":
            tracks = self.data["queue"]
        elif mode == "library":
            tracks = self.data["library"]
        elif mode == "favorites":
            tracks = self.data["favorites"]
        elif mode == "playlist_tracks":
            playlist = next((p for p in self.data["playlists"]
                             if p.get("name") == self.active_playlist), None)
            tracks = playlist.get("tracks", []) if playlist else []
        else:
            tracks = self.data["playlists"]

        self.visible_tracks = list(tracks)
        self.list_widget.clear()

        for entry in self.visible_tracks:
            if mode == "playlists":
                label = f"▤  {entry.get('name', 'Playlista')}  ·  {len(entry.get('tracks', []))} utw."
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, entry.get("name", ""))
            else:
                title = entry.get("title", "Nieznany utwór")
                artist = entry.get("channel", "")
                label = f"{title} — {artist}" if artist else title
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, entry.get("id", ""))
            self.list_widget.addItem(item)

        self.update_cache_count()

    def _item_double_clicked(self, _item):
        if self.view_mode == "playlists":
            self.open_selected_playlist()
        else:
            self.play_selected()

    def create_playlist(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Nowa playlista", "Nazwa playlisty:")
        name = name.strip()
        if not ok or not name:
            return
        if any(p.get("name", "").casefold() == name.casefold()
               for p in self.data["playlists"]):
            QMessageBox.information(self, "Playlisty", "Playlista o tej nazwie już istnieje.")
            return
        self.data["playlists"].append({"name": name, "tracks": []})
        self.persist()
        self.refresh_view("playlists")
        self.status.setText(f"Utworzono playlistę: {name}")

    def open_selected_playlist(self):
        index = self.list_widget.currentRow()
        if index < 0 or index >= len(self.visible_tracks):
            return
        playlist = self.visible_tracks[index]
        self.active_playlist = playlist.get("name", "")
        self.refresh_view("playlist_tracks")

    def delete_selected_playlist(self):
        index = self.list_widget.currentRow()
        if self.view_mode != "playlists" or index < 0:
            self.status.setText("Zaznacz playlistę do usunięcia.")
            return
        playlist = self.visible_tracks[index]
        name = playlist.get("name", "Playlista")
        answer = QMessageBox.question(
            self, "Usuń playlistę",
            f"Czy na pewno usunąć playlistę „{name}”? Utwory pozostaną w bibliotece.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.data["playlists"] = [p for p in self.data["playlists"]
                                  if p.get("name") != name]
        if self.active_playlist == name:
            self.active_playlist = None
        self.persist()
        self.refresh_view("playlists")
        self.status.setText(f"Usunięto playlistę „{name}”.")

    def add_selected_to_playlist(self):
        track = self.selected_track()
        if not track:
            self.status.setText(self.tr("Najpierw zaznacz utwór."))
            return
        playlists = self.data["playlists"]
        if not playlists:
            answer = QMessageBox.question(
                self, "Brak playlist",
                "Nie masz jeszcze playlisty. Czy chcesz ją teraz utworzyć?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.create_playlist()
            return
        from PySide6.QtWidgets import QInputDialog
        names = [p.get("name", "Playlista") for p in playlists]
        name, ok = QInputDialog.getItem(
            self, "Dodaj do playlisty", "Wybierz playlistę:", names, 0, False
        )
        if not ok:
            return
        playlist = next((p for p in playlists if p.get("name") == name), None)
        if playlist is None:
            return
        if any(t.get("id") == track.get("id") for t in playlist["tracks"]):
            self.status.setText("Ten utwór już jest na tej playliście.")
            return
        playlist["tracks"].append(track)
        self.persist()
        if self.view_mode == "playlists":
            self.refresh_view("playlists")
        elif self.view_mode == "playlist_tracks":
            self.refresh_view("playlist_tracks")
        self.status.setText(f"Dodano utwór do playlisty „{name}”.")

    def remove_selected_from_library(self):
        if self.view_mode != "library":
            return
        track = self.selected_track()
        if not track:
            self.status.setText("Zaznacz utwór w bibliotece.")
            return
        answer = QMessageBox.question(
            self, "Usuń z biblioteki",
            f"Usunąć „{track.get('title', 'utwór')}” z biblioteki? "
            "Plik MP3 i utwór w playlistach pozostaną bez zmian.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.data["library"] = [t for t in self.data["library"]
                                if t.get("id") != track.get("id")]
        self.persist()
        self.refresh_view("library")
        self.status.setText("Usunięto utwór z biblioteki.")

    def remove_selected_from_playlist(self):
        if self.view_mode != "playlist_tracks" or not self.active_playlist:
            return
        track = self.selected_track()
        if not track:
            self.status.setText("Zaznacz utwór na playliście.")
            return
        playlist = next((p for p in self.data["playlists"]
                         if p.get("name") == self.active_playlist), None)
        if playlist is None:
            self.refresh_view("playlists")
            return
        playlist["tracks"] = [t for t in playlist.get("tracks", [])
                              if t.get("id") != track.get("id")]
        self.persist()
        self.refresh_view("playlist_tracks")
        self.status.setText("Usunięto utwór z playlisty.")

    def update_cache_count(self):
        count = sum(
            1 for p in CACHE_DIR.glob("*.mp3")
            if p.is_file() and p.stat().st_size > 0
        )
        self.cache_count.setText(f"{count} {self.tr('utworów')}")

    def persist(self):
        save_data(self.data)
        self.update_cache_count()

    def search(self):
        query = self.search_input.text().strip()
        if not query:
            self.status.setText(self.tr("Wpisz tytuł utworu."))
            return

        if self.search_worker and self.search_worker.isRunning():
            return

        self.search_button.setEnabled(False)
        self.status.setText(self.tr("Wyszukiwanie w YouTube..."))

        self.search_worker = SearchWorker(query)
        self.search_worker.results_ready.connect(self.search_complete)
        self.search_worker.error.connect(self.show_error)
        self.search_worker.finished.connect(
            lambda: self.search_button.setEnabled(True)
        )
        self.search_worker.start()

    def search_complete(self, tracks):
        self.results = tracks
        self.refresh_view("search")
        self.status.setText(f"Znaleziono: {len(tracks)} utworów")

    def selected_track(self):
        index = self.list_widget.currentRow()
        if index < 0 or index >= len(self.visible_tracks):
            return None
        return self.visible_tracks[index]

    def add_selected_to_queue(self):
        track = self.selected_track()
        if not track:
            self.status.setText(self.tr("Najpierw zaznacz utwór."))
            return

        self.data["queue"].append(track)
        self.persist()

        if self.view_mode == "queue":
            self.refresh_view("queue")

        self.status.setText(self.tr("Dodano do kolejki."))

    def remove_selected_from_queue(self):
        if self.view_mode != "queue":
            return

        index = self.list_widget.currentRow()
        if index < 0:
            return

        self.data["queue"].pop(index)

        if index < self.queue_index:
            self.queue_index -= 1
        elif index == self.queue_index:
            self.queue_index = -1

        self.persist()
        self.refresh_view("queue")
        self.status.setText(self.tr("Usunięto utwór z kolejki."))

    def toggle_favorite(self):
        track = self.selected_track() or self.current_track
        if not track:
            self.status.setText("Najpierw wybierz utwór.")
            return

        favorites = self.data["favorites"]
        existing = next(
            (i for i, t in enumerate(favorites)
             if t["id"] == track["id"]),
            None,
        )

        if existing is None:
            favorites.append(track)
            self.status.setText(self.tr("Dodano do ulubionych ♥"))
        else:
            favorites.pop(existing)
            self.status.setText(self.tr("Usunięto z ulubionych."))

        self.persist()

        if self.view_mode == "favorites":
            self.refresh_view("favorites")

    def play_selected(self):
        track = self.selected_track()
        if not track:
            self.status.setText(self.tr("Zaznacz utwór na liście."))
            return

        queue = self.data["queue"]

        # Jeżeli utwór jest już w kolejce, wykorzystaj jego pozycję.
        found = next(
            (i for i, t in enumerate(queue)
             if t["id"] == track["id"]),
            None,
        )

        if found is None:
            queue.append(track)
            self.queue_index = len(queue) - 1
        else:
            self.queue_index = found

        self.persist()
        self.play_track(track)

    def play_track(self, track):
        if self.download_worker and self.download_worker.isRunning():
            self.status.setText("Pobieranie już trwa. Poczekaj chwilę.")
            return

        self.current_track = track
        self.handled_ended = False

        self.now_title.setText(track.get("title", "Nieznany utwór"))
        self.now_artist.setText(track.get("channel", ""))
        self.cover_label.setText("♫")
        self.cover_label.setPixmap(QPixmap())

        self.load_cover(track)

        cached = CACHE_DIR / f"{track['id']}.mp3"

        if cached.exists() and cached.stat().st_size > 0:
            self.start_audio(str(cached), track)
            return

        self.play_button.setEnabled(False)
        self.search_button.setEnabled(False)
        self.progress.show()
        self.status.setText(self.tr("Pobieranie audio..."))

        self.download_worker = DownloadWorker(track)
        self.download_worker.progress.connect(self.status.setText)
        self.download_worker.completed.connect(
            lambda path, t=track: self.download_complete(path, t)
        )
        self.download_worker.error.connect(self.show_error)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.start()

    def download_complete(self, path, track):
        # Nie odtwarzaj starego pobrania, jeśli użytkownik wybrał
        # już inny utwór.
        if self.current_track and self.current_track["id"] == track["id"]:
            self.start_audio(path, track)

    def download_finished(self):
        self.play_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.progress.hide()

    def start_audio(self, path, track):
        try:
            media = self.vlc_instance.media_new_path(path)
            self.player.set_media(media)
            self.player.audio_set_volume(self.volume_slider.value())

            self.current_path = path
            self.current_track = track
            self.handled_ended = False

            self.seek_slider.setValue(0)
            self.seek_slider.setEnabled(False)
            self.current_time.setText("0:00")
            self.total_time.setText("0:00")

            self.player.play()
            self.visualizer.set_active(True)
            self.status.setText(self.tr("Uruchamianie utworu..."))

            if not any(
                t["id"] == track["id"]
                for t in self.data["library"]
            ):
                self.data["library"].append(track)
                self.persist()

        except Exception as exc:
            self.show_error(str(exc))

    def toggle_pause(self):
        if self.player.get_media() is not None:
            self.player.pause()

    def next_track(self, automatic=False):
        queue = self.data["queue"]

        if not queue:
            self.status.setText(self.tr("Kolejka jest pusta."))
            return

        if self.repeat_mode == "one" and automatic and self.current_path:
            self.start_audio(self.current_path, self.current_track)
            return

        if self.shuffle and len(queue) > 1:
            choices = [
                i for i in range(len(queue))
                if i != self.queue_index
            ]
            self.queue_index = random.choice(choices)

        elif self.queue_index + 1 < len(queue):
            self.queue_index += 1

        elif self.repeat_mode == "all":
            self.queue_index = 0

        else:
            self.player.stop()
            self.visualizer.set_active(False)
            self.status.setText(self.tr("Koniec kolejki."))
            return

        self.play_track(queue[self.queue_index])

    def previous_track(self):
        if self.player.get_time() > 3000:
            self.player.set_time(0)
            return

        queue = self.data["queue"]
        if not queue:
            return

        if self.queue_index > 0:
            self.queue_index -= 1
        elif self.repeat_mode == "all":
            self.queue_index = len(queue) - 1
        else:
            self.player.set_time(0)
            return

        self.play_track(queue[self.queue_index])

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        color = GREEN if self.shuffle else "white"
        self.shuffle_button.setStyleSheet(f"color: {color};")
        self.status.setText(
            "Losowanie włączone." if self.shuffle
            else "Losowanie wyłączone."
        )

    def toggle_repeat(self):
        modes = ["off", "all", "one"]
        self.repeat_mode = modes[
            (modes.index(self.repeat_mode) + 1) % len(modes)
        ]

        labels = {"off": "↻", "all": "↻ All", "one": "↻ 1"}
        self.repeat_button.setText(labels[self.repeat_mode])
        color = GREEN if self.repeat_mode != "off" else "white"
        self.repeat_button.setStyleSheet(f"color: {color};")

    def load_cover(self, track):
        path = COVERS_DIR / f"{track['id']}.jpg"

        if path.exists() and path.stat().st_size > 0:
            self.set_cover(track["id"], str(path))
            return

        worker = CoverWorker(track)
        worker.completed.connect(self.set_cover)
        worker.finished.connect(
            lambda w=worker: self.cleanup_cover_worker(w)
        )
        self.cover_workers.append(worker)
        worker.start()

    def set_cover(self, track_id, path):
        if (
            not self.current_track
            or self.current_track["id"] != track_id
        ):
            return

        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.cover_label.setPixmap(
                pixmap.scaled(
                    76, 76,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.cover_label.setText("")

    def cleanup_cover_worker(self, worker):
        if worker in self.cover_workers:
            self.cover_workers.remove(worker)

    def update_player(self):
        if self.player.get_media() is None:
            return

        length = self.player.get_length()
        current = self.player.get_time()
        state = self.player.get_state()

        if length > 0:
            self.total_time.setText(format_time(length))

            if not self.seek_slider.isSliderDown() and current >= 0:
                self.current_time.setText(format_time(current))
                position = int(current / length * 1000)
                self.seek_slider.setValue(
                    max(0, min(1000, position))
                )

            self.seek_slider.setEnabled(True)

        if state == vlc.State.Playing:
            self.visualizer.set_active(True)
            self.status.setText(self.tr("Odtwarzanie muzyki"))

        elif state == vlc.State.Paused:
            self.visualizer.set_active(False)
            self.status.setText(self.tr("Pauza"))

        elif state == vlc.State.Ended and not self.handled_ended:
            self.handled_ended = True
            self.next_track(automatic=True)

        elif state == vlc.State.Error:
            self.visualizer.set_active(False)
            self.status.setText(self.tr("Błąd odtwarzania."))

    def begin_seek(self):
        self.seeking = True

    def preview_seek(self, position):
        length = self.player.get_length()
        if length > 0:
            self.current_time.setText(
                format_time(int(length * position / 1000))
            )

    def finish_seek(self):
        length = self.player.get_length()
        if length > 0:
            target = int(length * self.seek_slider.value() / 1000)
            self.player.set_time(target)
        self.seeking = False

    def show_error(self, message):
        self.status.setText(self.tr("Wystąpił błąd."))
        QMessageBox.warning(self, "Green Player", message)

    def closeEvent(self, event):
        self.timer.stop()
        self.player.stop()

        workers = []
        if self.search_worker:
            workers.append(self.search_worker)
        if self.download_worker:
            workers.append(self.download_worker)
        workers.extend(self.cover_workers)

        for worker in workers:
            if worker.isRunning():
                worker.wait()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec())

