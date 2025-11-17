import os
import sys

# По хорошему отдельно каждому файлу указывать, с какой директорией работать, 
# но здесь это применимо, так как все файлы работают в директории с запускаемым скриптом
def setup_dir(): 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

setup_dir()

import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QMessageBox, QFrame,
    QTextBrowser, QStackedWidget, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from dotenv import load_dotenv


class PipelineWorker(QThread):
    finished = pyqtSignal(bool)
    progress = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            self.progress.emit("Запуск обработки pipeline.py. Ожидайте...")
            subprocess.run([sys.executable, "pipeline.py", self.prompt], check=True)
            self.progress.emit("Генерация завершена!")
            self.finished.emit(True)
        except subprocess.CalledProcessError as e:
            self.progress.emit(f"Ошибка: {e}")
            self.finished.emit(False)
        except Exception as e:
            self.progress.emit(f"Ошибка выполнения: {e}")
            self.finished.emit(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор доказательств")
        self.setGeometry(100, 100, 1000, 720)
        self.setWindowIcon(QIcon("images/icon.png") if Path("images/icon.png").exists() else QIcon())

        self.green_dark = "#0d1b2a"
        self.green_med = "#1b4965"
        self.green_menu = "#0a2540"
        self.front_purple = "#162447"

        self.setup_palette()
        self.app_dialog_stylesheet = f"""
            QMenu, QMenu::item {{
                background-color: {self.green_dark};
                color: white;
            }}
        """

        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        self.setCentralWidget(outer)

        self.margin_frame = QFrame()
        self.margin_frame.setStyleSheet(f"background-color: {self.front_purple}; border-radius: 10px;")
        outer_layout.addWidget(self.margin_frame)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(18)
        self.main_layout.setContentsMargins(20, 20, 20, 16)
        self.margin_frame_layout = QVBoxLayout(self.margin_frame)
        self.margin_frame_layout.setContentsMargins(8, 8, 8, 8)
        self.margin_frame_layout.addWidget(self.main_widget)

        self.header = QLabel("")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Arial", 18, QFont.Bold))
        self.header.setStyleSheet("color: white;")
        self.main_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #DFFFE5;")
        self.main_layout.addItem(QSpacerItem(20, 6))
        self.main_layout.addWidget(self.status_label)

        self.current_state = "connect" if not self.check_api_key() else "assert"
        self.last_assertion = ""
        self.logs_visible = False

        self._build_connect_page()
        self._build_assert_page()
        self._build_result_page()

        self._show_state(self.current_state, initial=True)

    def setup_palette(self):
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(self.green_dark))
        pal.setColor(QPalette.WindowText, Qt.white)
        pal.setColor(QPalette.Base, QColor("#0f1a27"))
        pal.setColor(QPalette.Text, Qt.white)
        pal.setColor(QPalette.Button, QColor(self.green_med))
        pal.setColor(QPalette.ButtonText, Qt.white)
        pal.setColor(QPalette.Highlight, QColor("#4FC3F7"))
        self.setPalette(pal)

    def check_api_key(self):
        load_dotenv(override=True)
        return "OPENROUTER_API_KEY" in os.environ and os.environ.get("OPENROUTER_API_KEY").strip() != ""

    def green_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.green_med};
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:disabled {{
                background-color: #3a3a3a;
                color: #9a9a9a;
            }}
        """

    def _build_connect_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(6, 6, 6, 6)

        self.explanation_browser = QTextBrowser()
        self.explanation_browser.setOpenExternalLinks(True)
        self.explanation_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.explanation_browser.setFont(QFont("Arial", 14))  # крупный текст в explanations
        self.explanation_browser.setStyleSheet(
            "QTextBrowser{background:#141414; color:white; border:1px solid #3b3b3b; border-radius:8px; padding:10px; font-size:14px;}"
        )
        self.explanation_browser.setHtml(
            "<h3>Инструкция:</h3>"
            "<p>Регистрируемся на сайте <a href='https://openrouter.ai/'>OpenRouter</a></p>"
            "<p>Создаем API-ключ здесь <a href='https://openrouter.ai/settings/keys'>OpenRouterAPI</a></p>"
            "<p>Вводим ключ в поле ниже ↓↓↓</p>"
        )
        layout.addWidget(self.explanation_browser, stretch=1)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("sk-...")
        self.api_input.setFont(QFont("Arial", 14))
        self.api_input.setStyleSheet("QLineEdit{padding:10px; border-radius:8px; border:1px solid #3b3b3b; background:#0f0f0f; color:white;}")
        self.api_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_layout.addWidget(self.api_input)

        self.save_api_btn = QPushButton()
        if Path("images/save.png").exists():
            self.save_api_btn.setIcon(QIcon("images/save.png"))
            self.save_api_btn.setText("")
        else:
            self.save_api_btn.setText("Сохранить")
        self.save_api_btn.setStyleSheet(self.green_button_style())
        self.save_api_btn.clicked.connect(self._on_save_api)
        row_layout.addWidget(self.save_api_btn)

        layout.addWidget(row)

        self.connect_hint = QLabel("")
        self.connect_hint.setFont(QFont("Arial", 13))
        self.connect_hint.setStyleSheet("color: #DFFFE5;")
        self.connect_hint.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.connect_hint)

        self.stack.addWidget(page)
        self.page_connect_index = self.stack.count() - 1
        

    def _build_assert_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(6, 6, 6, 6)

        self.assert_text = QTextEdit()
        self.assert_text.setPlaceholderText("Например: Все кошки являются животными. Мурка — кошка. Докажите, что Мурка — животное.")
        self.assert_text.setFont(QFont("Arial", 16))
        self.assert_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.assert_text.setStyleSheet("QTextEdit{background:#141414; color:white; border:1px solid #3b3b3b; border-radius:8px; padding:10px; font-size:16px;}")
        layout.addWidget(self.assert_text, stretch=1)

        self.generate_btn = QPushButton("Сгенерировать доказательство")
        self.generate_btn.setStyleSheet(self.green_button_style())
        self.generate_btn.setFont(QFont("Arial", 16))
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 6, 0, 6)
        self.generate_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_layout.addWidget(self.generate_btn, alignment=Qt.AlignCenter)
        self.generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(btn_container)

        self.stack.addWidget(page)
        self.page_assert_index = self.stack.count() - 1

    def _build_result_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(6, 6, 6, 6)

        combined_block = QFrame()
        combined_block.setStyleSheet("QFrame{background:transparent; border-radius:6px;}")
        combined_layout = QVBoxLayout(combined_block)
        combined_layout.setSpacing(8)
        combined_layout.setContentsMargins(0, 0, 0, 0)

        self.shown_assert_label = QLabel("")
        self.shown_assert_label.setWordWrap(True)
        self.shown_assert_label.setFont(QFont("Arial", 14))
        self.shown_assert_label.setStyleSheet("color: #EDEDED;")
        combined_layout.addWidget(self.shown_assert_label)

        self.result_browser = QTextBrowser()
        self.result_browser.setFont(QFont("Arial", 14))
        self.result_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_browser.setStyleSheet("QTextBrowser{background:#141414; color:white; border:1px solid #3b3b3b; border-radius:8px; padding:10px; font-size:14px;}")
        self.result_browser.setOpenExternalLinks(True)
        combined_layout.addWidget(self.result_browser, stretch=1)

        layout.addWidget(combined_block)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        self.show_logs_btn = QPushButton("Показать логи")
        self.show_logs_btn.setStyleSheet(self.green_button_style())
        self.show_logs_btn.setFont(QFont("Arial", 14))
        self.show_logs_btn.clicked.connect(self._toggle_logs)
        self.show_logs_btn.setEnabled(False)
        row_layout.addWidget(self.show_logs_btn, alignment=Qt.AlignLeft)

        self.restart_btn = QPushButton("Доказать новое")
        self.restart_btn.setStyleSheet(self.green_button_style())
        self.restart_btn.setFont(QFont("Arial", 14))
        self.restart_btn.clicked.connect(self._on_restart)
        row_layout.addWidget(self.restart_btn, alignment=Qt.AlignRight)

        layout.addWidget(row)

        self.stack.addWidget(page)
        self.page_result_index = self.stack.count() - 1

    def _show_state(self, state, initial=False):
        self.current_state = state
        header_map = {
            "connect": "Подключение к ИИ",
            "assert": "Введите утверждение",
            "result": "Доказательство",
        }
        self.header.setText(header_map.get(state, ""))

        if state == "connect":
            self.stack.setCurrentIndex(self.page_connect_index)
            self.connect_hint.setText("Ожидаем добавления ключа в переменные среды")
            self.status_label.setText("")
        elif state == "assert":
            self.stack.setCurrentIndex(self.page_assert_index)
            if self.check_api_key():
                self.status_label.setText("Ключ к ИИ успешно загружен из переменного окружения")
            else:
                self.status_label.setText("")
        elif state == "result":
            self.stack.setCurrentIndex(self.page_result_index)
            self.show_logs_btn.setEnabled(True)
            self.status_label.setText("")
            self.logs_visible = False
            self.show_logs_btn.setText("Показать логи")

    def _on_save_api(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите API ключ")
            return
        try:
            with open('.env', 'a', encoding='utf-8') as f:
                f.write(f'OPENROUTER_API_KEY={api_key}\n')
            os.environ['OPENROUTER_API_KEY'] = api_key
            QMessageBox.information(self, "Успех", "API ключ сохранён в .env")
            self._show_state("assert")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить ключ: {e}")

    def _on_generate(self):
        text = self.assert_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите утверждение")
            return
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Запущена обработка, ожидайте...")
        self.last_assertion = text

        self.worker = PipelineWorker(text)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_progress(self, msg):
        self.status_label.setText(msg)

    def _on_worker_finished(self, success):
        self.generate_btn.setEnabled(True)
        if success:
            try:
                if Path("explanation.md").exists():
                    content = Path("explanation.md").read_text(encoding='utf-8')
                    try:
                        self.result_browser.setMarkdown(content)
                    except Exception:
                        self.result_browser.setPlainText(content)
                    displayed = self.last_assertion.replace('\n', ' ')
                    self.shown_assert_label.setText(f"<b>Утверждение:</b> {displayed}")
                    self._show_state("result")
                    self.status_label.setText("Генерация завершена успешно. Результаты и логи сохранены в explanation.md и output.txt")
                    self.show_logs_btn.setEnabled(True)
                else:
                    self.status_label.setText("Ошибка: explanation.md не найден")
                    QMessageBox.warning(self, "Ошибка", "Файл explanation.md не найден")
            except Exception as e:
                self.status_label.setText(f"Ошибка чтения explanation.md: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать explanation.md: {e}")
        else:
            self.status_label.setText("Ошибка генерации (см. логи)")
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при генерации — см. логи.")

    def _toggle_logs(self):
        if not self.logs_visible:
            if Path("output.txt").exists():
                logs = Path("output.txt").read_text(encoding='utf-8')
                display = logs if len(logs) <= 9000 else logs[:9000] + "\n\n... (логи обрезаны)"
                self.result_browser.setPlainText(display)
            else:
                self.result_browser.setPlainText("Файл output.txt не найден")
            self.result_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.show_logs_btn.setText("Скрыть логи")
            self.logs_visible = True
        else:
            if Path("explanation.md").exists():
                try:
                    content = Path("explanation.md").read_text(encoding='utf-8')
                    try:
                        self.result_browser.setMarkdown(content)
                    except Exception:
                        self.result_browser.setPlainText(content)
                except Exception:
                    self.result_browser.setPlainText("")
            else:
                self.result_browser.setPlainText("")
            self.result_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.show_logs_btn.setText("Показать логи")
            self.logs_visible = False

    def _on_restart(self):
        self.assert_text.clear()
        self.result_browser.clear()
        self.shown_assert_label.setText("")
        self.status_label.setText("")
        self.show_logs_btn.setEnabled(False)
        self.logs_visible = False
        self.show_logs_btn.setText("Показать логи")
        self.last_assertion = ""
        if not self.check_api_key():
            self._show_state("connect")
        else:
            self._show_state("assert")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(window.app_dialog_stylesheet)
    app.setStyle('Fusion')
    window.show()
    sys.exit(app.exec_())
