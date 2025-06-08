import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,
                            QMessageBox)
from PyQt5.QtGui import QColor, QPixmap, QDrag, QPainter
from PyQt5.QtCore import Qt, QTimer, QMimeData, QPoint, pyqtSignal
import os

class BlockPuzzleGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Block Puzzle")
        self.setFixedSize(800, 900)
        
        # Установка фиолетового цвета фона
        self.setStyleSheet("""
            QMainWindow {
                background-color: #8B00FF;
            }
            QWidget {
                background-color: #8B00FF;
            }
        """)
        
        # Игровые переменные
        self.score = 0
        self.time_elapsed = 0
        self.selected_piece = None
        self.board = [[None for _ in range(10)] for _ in range(10)]
        self.board_cells = [[None for _ in range(10)] for _ in range(10)]  # Хранение ячеек игрового поля
        
        # Инициализация интерфейса
        self.init_ui()
        
        # Запуск игрового таймера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        # Генерация начальных фигур
        self.generate_pieces()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Верхняя панель с очками и управлением
        top_panel = QHBoxLayout()
        
        self.score_label = QLabel(f"Очки: {self.score}")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        top_panel.addWidget(self.score_label)
        
        self.time_label = QLabel("Время: 00:00")
        self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        top_panel.addWidget(self.time_label)
        
        restart_btn = QPushButton("Начать сначала")
        restart_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(254, 254, 254, 50);
            }
        """)
        restart_btn.clicked.connect(self.restart_game)
        top_panel.addWidget(restart_btn)
        
        main_layout.addLayout(top_panel)
        
        # Область для фигур
        self.pieces_frame = QFrame()
        self.pieces_frame.setFixedHeight(200)
        self.pieces_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        self.pieces_layout = QHBoxLayout(self.pieces_frame)
        self.pieces_layout.setSpacing(15)
        self.pieces_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(self.pieces_frame)
        
        # Игровое поле
        self.board_frame = QFrame()
        self.board_frame.setFixedSize(500, 500)
        self.board_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #333;
            }
        """)
        
        self.board_grid = QGridLayout(self.board_frame)
        self.board_grid.setSpacing(0)
        self.board_grid.setContentsMargins(0, 0, 0, 0)
        
        # Создание ячеек игрового поля
        for row in range(10):
            for col in range(10):
                cell = ClickableCell(row, col, self)
                cell.clicked.connect(self.cell_clicked)
                cell.setFixedSize(50, 50)
                cell.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #ddd;
                    }
                    QFrame:hover {
                        background-color: #f0f0f0;
                    }
                """)
                self.board_grid.addWidget(cell, row, col)
                self.board_cells[row][col] = cell
        
        main_layout.addWidget(self.board_frame, alignment=Qt.AlignCenter)
        
        # Help button
        help_btn = QPushButton("Правила игры")
        help_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        main_layout.addWidget(help_btn, alignment=Qt.AlignRight)

    def generate_pieces(self):
        """Генерация новых фигур для игрока"""
        # Очистка существующих фигур
        for i in reversed(range(self.pieces_layout.count())): 
            self.pieces_layout.itemAt(i).widget().setParent(None)
        
        # Определение возможных фигур (матрицы форм)
        pieces = [
            [[1]],                          # Одиночный блок
            [[1, 1]],                       # 2 блока горизонтально
            [[1], [1]],                     # 2 блока вертикально
            [[1, 1], [1, 1]],              # Квадрат 2x2
            [[1, 1, 1]],                    # 3 блока горизонтально
            [[1], [1], [1]],               # 3 блока вертикально
            [[1, 1, 0], [0, 1, 1]],        # Z-форма
            [[0, 1, 1], [1, 1, 0]],        # S-форма
            [[1, 0], [1, 1]],              # L-форма
            [[0, 1], [1, 1]],              # Обратная L-форма
            [[1, 1, 1], [0, 1, 0]],        # T-форма
        ]
        
        # Генерация 3 случайных фигур
        for _ in range(3):
            shape = random.choice(pieces)
            color = QColor(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            piece = PieceWidget(shape, color, self)
            piece.clicked.connect(self.piece_selected)
            self.pieces_layout.addWidget(piece)

    def piece_selected(self, piece):
        """Обработка выбора фигуры"""
        if self.selected_piece:
            self.selected_piece.set_selected(False)
        
        self.selected_piece = piece
        piece.set_selected(True)

    def update_timer(self):
        """Обновление игрового таймера"""
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.time_label.setText(f"Время: {minutes:02d}:{seconds:02d}")

    def restart_game(self):
        """Перезапуск игры"""
        self.score = 0
        self.time_elapsed = 0
        self.score_label.setText(f"Очки: {self.score}")
        self.time_label.setText("Время: 00:00")
        
        # Очистка поля
        for row in range(10):
            for col in range(10):
                cell = self.board_grid.itemAtPosition(row, col).widget()
                cell.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #ddd;
                    }
                    QFrame:hover {
                        background-color: #f0f0f0;
                    }
                """)
                self.board[row][col] = None
        
        # Генерация новых фигур
        self.generate_pieces()

    def show_help(self):
        """Show game instructions"""
        QMessageBox.information(self, "Правила игры",
            "Правила игры Block Puzzle:\n\n"
            "1. Нажмите на фигуру, чтобы выбрать её\n"
            "2. Нажмите на клетку поля, куда хотите поместить фигуру\n"
            "3. При заполнении всей горизонтальной или вертикальной линии, она очищается\n"
            "4. За каждую очищенную линию получаете 100 очков\n"
            "5. Когда все фигуры использованы, появятся новые\n\n"
            "Подсказка: Старайтесь заполнять несколько линий одной фигурой для получения больше очков!")

    def cell_clicked(self, row, col):
        """Обработка клика по ячейке игрового поля"""
        if not self.selected_piece:
            return
            
        # Проверка возможности размещения фигуры
        if self.can_place_piece(row, col, self.selected_piece.shape):
            self.place_piece(row, col, self.selected_piece)
            self.selected_piece.setParent(None)  # Удаление фигуры из области фигур
            self.selected_piece = None
            
            # Проверка, все ли фигуры использованы
            if self.pieces_layout.count() == 0:
                self.generate_pieces()
    
    def can_place_piece(self, start_row, start_col, shape):
        """Проверка возможности размещения фигуры в указанной позиции"""
        rows = len(shape)
        cols = len(shape[0])
        
        # Проверка выхода за границы поля
        if start_row + rows > 10 or start_col + cols > 10:
            return False
            
        # Проверка, свободны ли все необходимые ячейки
        for row in range(rows):
            for col in range(cols):
                if shape[row][col]:
                    if self.board[start_row + row][start_col + col] is not None:
                        return False
        return True
    
    def place_piece(self, start_row, start_col, piece):
        """Размещение фигуры на поле"""
        shape = piece.shape
        rows = len(shape)
        cols = len(shape[0])
        
        # Размещение фигуры на поле
        for row in range(rows):
            for col in range(cols):
                if shape[row][col]:
                    board_row = start_row + row
                    board_col = start_col + col
                    self.board[board_row][board_col] = piece.color
                    self.board_cells[board_row][board_col].setStyleSheet(f"""
                        QFrame {{
                            background-color: {piece.color.name()};
                            border: 1px solid {piece.color.darker().name()};
                        }}
                    """)
        
        # Проверка и очистка заполненных линий
        self.check_and_clear_lines()
        
        # Обновление отображения очков
        self.score_label.setText(f"Очки: {self.score}")

    def check_and_clear_lines(self):
        """Проверка и очистка заполненных рядов и столбцов"""
        # Проверка рядов
        rows_to_clear = []
        for row in range(10):
            if all(self.board[row][col] is not None for col in range(10)):
                rows_to_clear.append(row)
        
        # Проверка столбцов
        cols_to_clear = []
        for col in range(10):
            if all(self.board[row][col] is not None for row in range(10)):
                cols_to_clear.append(col)
        
        # Очистка рядов и начисление очков
        for row in rows_to_clear:
            self.clear_row(row)
            self.score += 100  # 100 очков за каждый очищенный ряд
        
        # Очистка столбцов и начисление очков
        for col in cols_to_clear:
            self.clear_column(col)
            self.score += 100  # 100 очков за каждый очищенный столбец

    def clear_row(self, row):
        """Очистка заполненного ряда"""
        # Очистка ряда в массиве поля
        for col in range(10):
            self.board[row][col] = None
            self.board_cells[row][col].setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                }
                QFrame:hover {
                    background-color: #f0f0f0;
                }
            """)

    def clear_column(self, col):
        """Очистка заполненного столбца"""
        # Очистка столбца в массиве поля
        for row in range(10):
            self.board[row][col] = None
            self.board_cells[row][col].setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                }
                QFrame:hover {
                    background-color: #f0f0f0;
                }
            """)

class ClickableCell(QFrame):
    """Кастомный QFrame, который испускает сигналы о строке и столбце при клике"""
    clicked = pyqtSignal(int, int)
    
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)

class PieceWidget(QFrame):
    """Виджет, представляющий игровую фигуру"""
    clicked = pyqtSignal(object)
    
    def __init__(self, shape, color, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.color = color
        self.is_selected = False
        
        # Вычисление размеров фигуры
        rows = len(shape)
        cols = len(shape[0]) if rows > 0 else 0
        self.setFixedSize(cols * 50 + 2, rows * 50 + 2)
        
        # Создание layout и блоков
        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for row in range(rows):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    block = QFrame()
                    block.setFixedSize(50, 50)
                    block.setStyleSheet(f"""
                        QFrame {{
                            background-color: {self.color.name()};
                            border: 1px solid {self.color.darker().name()};
                        }}
                    """)
                    layout.addWidget(block, row, col)
        
        self.setStyleSheet("""
            PieceWidget {
                background: transparent;
                border: 2px solid transparent;
            }
            PieceWidget:hover {
                border: 2px dashed #666;
            }
        """)

    def set_selected(self, selected):
        """Установка состояния выбора фигуры"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                PieceWidget {
                    background: rgba(255, 255, 255, 0.2);
                    border: 2px solid #2196F3;
                }
            """)
        else:
            self.setStyleSheet("""
                PieceWidget {
                    background: transparent;
                    border: 2px solid transparent;
                }
                PieceWidget:hover {
                    border: 2px dashed #666;
                }
            """)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)

class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 600)
        
        # Загружаем фоновое изображение
        background_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block.jpg")
        if os.path.exists(background_path):
            pixmap = QPixmap(background_path)
            background_label = QLabel(self)
            background_label.setPixmap(pixmap.scaled(600, 600, Qt.KeepAspectRatio))
            background_label.setGeometry(0, 0, 600, 600)
            background_label.lower()
        
        # Создаем центральный виджет с прозрачным фоном
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        # Создаем вертикальный layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignRight | Qt.AlignTop)  # Выравнивание по правому верхнему краю
        layout.setSpacing(20)
        layout.addSpacing(270) 

        # Создаем кнопки меню
        buttons = [
            ("Начать игру", self.start_game),
            ("Правила игры", self.show_rules),
            ("Выход", self.close)
        ]
        
        for text, handler in buttons:
            button = QPushButton(text)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    padding: 10px;
                    background-color: rgba(255, 255, 255, 0.9);
                    color: purple;
                    border: 3px solid purple;
                    border-radius: 10px;
                    min-width: 250px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: purple;
                    color: white;
                }
            """)
            button.clicked.connect(handler)
            layout.addWidget(button)

    def start_game(self):
        self.window2 = BlockPuzzleGame()
        self.window2.show()
        self.close()

    def show_rules(self):
        rules = QMessageBox()
        rules.setWindowTitle("Правила игры")
        rules.setText(
            "Правила игры Block Puzzle:\n\n"
            "1. Игровое поле поле представляет собой сетку 10х10 клеток\n"
            "2. В верхней части экрана расположено поле, на котором появляются три случайные фигуры\n"
            "3. Фугуры необходимо перетаскивать на игровое поле. Для этого необходимо нажать на фигуру, затем на место на поле.\n"
            "4. Когда горизонтальная или вертикальная линии полностью заполнены они удаляются.\n"
            "5. За каждую линию начисляется 100 очков.\n"
            "6. Игра продолжается до тех пор, пока есть возможность размещать фигуры.\n"
            "7. Игра заканчивается, когда нет возможности разместить ни одну фигуру.\n"
        )
        rules.exec_()

class Window2(QMainWindow):
    def init(self):
        super().init()
        self.game = BlockPuzzleGame()
        self.game.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    sys.exit(app.exec_())