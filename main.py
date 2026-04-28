import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("950x600")
        self.root.resizable(True, True)

        self.books = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table_frame()
        self.create_stats_frame()

        self.refresh_table()

    def create_input_frame(self):
        """Форма добавления книги"""
        frame = tk.LabelFrame(self.root, text="Добавить книгу", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame.pack(fill="x", padx=10, pady=5)

        # Название книги
        tk.Label(frame, text="Название книги:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(frame, width=25, font=("Arial", 9))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        tk.Label(frame, text="Автор:", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=(10,0), pady=5)
        self.author_entry = tk.Entry(frame, width=20, font=("Arial", 9))
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        tk.Label(frame, text="Жанр:", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.genre_var = tk.StringVar()
        genres = ["Роман", "Детектив", "Фантастика", "Научная литература", "Поэзия", "Драма", "Приключения", "Другое"]
        self.genre_combo = ttk.Combobox(frame, textvariable=self.genre_var, values=genres, width=18, font=("Arial", 9))
        self.genre_combo.grid(row=1, column=1, padx=5, pady=5)
        self.genre_combo.set("Выберите жанр")

        # Количество страниц
        tk.Label(frame, text="Количество страниц:", font=("Arial", 9)).grid(row=1, column=2, sticky="w", padx=(10,0), pady=5)
        self.pages_entry = tk.Entry(frame, width=10, font=("Arial", 9))
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        tk.Button(frame, text="Добавить книгу", command=self.add_book, bg="#4CAF50", fg="white", 
                  font=("Arial", 9, "bold"), padx=20).grid(row=0, column=4, rowspan=2, padx=20, pady=5)

    def create_filter_frame(self):
        """Фильтрация книг"""
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(frame, text="Жанр:", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.filter_genre_var = tk.StringVar(value="Все")
        genres = ["Все", "Роман", "Детектив", "Фантастика", "Научная литература", "Поэзия", "Драма", "Приключения", "Другое"]
        self.filter_genre_combo = ttk.Combobox(frame, textvariable=self.filter_genre_var, values=genres, width=15, font=("Arial", 9))
        self.filter_genre_combo.grid(row=0, column=1, padx=5)
        self.filter_genre_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Фильтр по количеству страниц (больше N)
        tk.Label(frame, text="Страниц больше:", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=(15,0))
        self.pages_filter_entry = tk.Entry(frame, width=8, font=("Arial", 9))
        self.pages_filter_entry.grid(row=0, column=3, padx=5)
        tk.Label(frame, text="(например, 200)", font=("Arial", 8), fg="gray").grid(row=0, column=4, sticky="w")

        tk.Button(frame, text="Применить фильтр", command=self.apply_filters, bg="#2196F3", fg="white",
                  font=("Arial", 9)).grid(row=0, column=5, padx=10)
        tk.Button(frame, text="Сбросить фильтры", command=self.reset_filters, bg="#FF9800", fg="white",
                  font=("Arial", 9)).grid(row=0, column=6, padx=5)

    def create_table_frame(self):
        """Таблица с книгами"""
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание scrollbar
        scrollbar_y = tk.Scrollbar(frame)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = tk.Scrollbar(frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        # Таблица
        self.tree = ttk.Treeview(frame, columns=("ID", "Название", "Автор", "Жанр", "Страницы"), 
                                  show="headings", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название книги")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Название", width=300, anchor="w")
        self.tree.column("Автор", width=200, anchor="w")
        self.tree.column("Жанр", width=150, anchor="center")
        self.tree.column("Страницы", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # Кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Удалить выбранную книгу", command=self.delete_book, bg="#f44336", fg="white",
                  font=("Arial", 9), padx=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать книгу", command=self.edit_book, bg="#FF9800", fg="white",
                  font=("Arial", 9), padx=10).pack(side="left", padx=5)

    def create_stats_frame(self):
        """Статистика"""
        frame = tk.LabelFrame(self.root, text="Статистика", padx=10, pady=5, font=("Arial", 10, "bold"))
        frame.pack(fill="x", padx=10, pady=5)

        self.stats_label = tk.Label(frame, text="Всего книг: 0 | Всего страниц: 0", font=("Arial", 10))
        self.stats_label.pack()

    def validate_inputs(self, title, author, genre, pages):
        """Проверка корректности ввода"""
        if not title or not title.strip():
            messagebox.showerror("Ошибка", "Название книги не может быть пустым")
            return False
        
        if not author or not author.strip():
            messagebox.showerror("Ошибка", "Имя автора не может быть пустым")
            return False
        
        if not genre or genre == "Выберите жанр":
            messagebox.showerror("Ошибка", "Выберите жанр книги")
            return False
        
        try:
            pages_num = int(pages)
            if pages_num <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом")
            return False
        
        return True

    def add_book(self):
        """Добавление книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_var.get()
        pages = self.pages_entry.get().strip()

        if not self.validate_inputs(title, author, genre, pages):
            return

        pages_num = int(pages)
        
        new_id = max([book["id"] for book in self.books], default=0) + 1
        self.books.append({
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages_num
        })
        
        self.save_data()
        self.refresh_table()
        self.update_stats()
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("Выберите жанр")
        self.pages_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return

        item = self.tree.item(selected[0])
        book_id = int(item["values"][0])
        
        book_title = next((book["title"] for book in self.books if book["id"] == book_id), "")
        
        if messagebox.askyesno("Подтверждение", f"Удалить книгу '{book_title}'?"):
            self.books = [book for book in self.books if book["id"] != book_id]
            self.save_data()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Книга удалена")

    def edit_book(self):
        """Редактирование книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для редактирования")
            return

        item = self.tree.item(selected[0])
        book_id = int(item["values"][0])
        book = next((b for b in self.books if b["id"] == book_id), None)
        
        if book:
            self.open_edit_window(book)

    def open_edit_window(self, book):
        """Окно редактирования книги"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование книги")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)

        tk.Label(edit_window, text="Редактирование книги", font=("Arial", 12, "bold")).pack(pady=10)

        frame = tk.Frame(edit_window)
        frame.pack(pady=10)

        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", pady=5)
        title_entry = tk.Entry(frame, width=30)
        title_entry.insert(0, book["title"])
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Автор:").grid(row=1, column=0, sticky="w", pady=5)
        author_entry = tk.Entry(frame, width=30)
        author_entry.insert(0, book["author"])
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Жанр:").grid(row=2, column=0, sticky="w", pady=5)
        genre_var = tk.StringVar(value=book["genre"])
        genres = ["Роман", "Детектив", "Фантастика", "Научная литература", "Поэзия", "Драма", "Приключения", "Другое"]
        genre_combo = ttk.Combobox(frame, textvariable=genre_var, values=genres, width=27)
        genre_combo.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Страницы:").grid(row=3, column=0, sticky="w", pady=5)
        pages_entry = tk.Entry(frame, width=30)
        pages_entry.insert(0, str(book["pages"]))
        pages_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_edit():
            new_title = title_entry.get().strip()
            new_author = author_entry.get().strip()
            new_genre = genre_var.get()
            new_pages = pages_entry.get().strip()

            if not new_title or not new_author:
                messagebox.showerror("Ошибка", "Название и автор не могут быть пустыми")
                return
            
            try:
                new_pages_num = int(new_pages)
                if new_pages_num <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом")
                return

            book["title"] = new_title
            book["author"] = new_author
            book["genre"] = new_genre
            book["pages"] = new_pages_num
            
            self.save_data()
            self.refresh_table()
            self.update_stats()
            edit_window.destroy()
            messagebox.showinfo("Успех", "Книга обновлена")

        tk.Button(edit_window, text="Сохранить", command=save_edit, bg="#4CAF50", fg="white", 
                  font=("Arial", 9, "bold"), padx=20).pack(pady=20)

    def apply_filters(self):
        """Применение фильтров"""
        self.refresh_table()

    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_genre_var.set("Все")
        self.pages_filter_entry.delete(0, tk.END)
        self.refresh_table()

    def get_filtered_books(self):
        """Возвращает отфильтрованные книги"""
        filtered = self.books[:]
        
        # Фильтр по жанру
        genre_filter = self.filter_genre_var.get()
        if genre_filter != "Все":
            filtered = [book for book in filtered if book["genre"] == genre_filter]
        
        # Фильтр по количеству страниц (> N)
        pages_filter = self.pages_filter_entry.get().strip()
        if pages_filter:
            try:
                min_pages = int(pages_filter)
                if min_pages >= 0:
                    filtered = [book for book in filtered if book["pages"] > min_pages]
            except ValueError:
                pass  # Игнорируем некорректный ввод
        
        return filtered

    def refresh_table(self):
        """Обновление таблицы"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        filtered = self.get_filtered_books()
        for book in filtered:
            self.tree.insert("", "end", values=(book["id"], book["title"], book["author"], book["genre"], book["pages"]))

    def update_stats(self):
        """Обновление статистики"""
        total_books = len(self.books)
        total_pages = sum(book["pages"] for book in self.books)
        self.stats_label.config(text=f"Всего книг: {total_books} | Всего страниц: {total_pages}")

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except:
                self.books = []
        else:
            # Добавляем примеры книг для демонстрации
            self.books = [
                {"id": 1, "title": "Война и мир", "author": "Лев Толстой", "genre": "Роман", "pages": 1225},
                {"id": 2, "title": "Преступление и наказание", "author": "Фёдор Достоевский", "genre": "Роман", "pages": 671},
                {"id": 3, "title": "Мастер и Маргарита", "author": "Михаил Булгаков", "genre": "Роман", "pages": 480},
                {"id": 4, "title": "1984", "author": "Джордж Оруэлл", "genre": "Фантастика", "pages": 328}
            ]

    def save_data(self):
        """Сохранение данных в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()