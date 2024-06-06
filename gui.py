import base64
import tkinter as tk
from tkinter.messagebox import showwarning, showerror
from PIL import ImageTk, Image
from io import BytesIO
from webbrowser import open_new_tab
import requests

bg_color = "#74fcdb"
over_search = "#9a9b9c"
font = ("Arial", 14)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Студентська бібліотека  v.1.0")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.welcome_l = tk.Label(self, text="ВІТАЄМО У СТУДЕНТСЬКІЙ БІБЛІОТЕЦІ!", font=("Comic Sans MS", 20, "bold"))
        self.proposition_l = tk.Label(self, text="""Якщо є пропозиції щодо покращення додатку або хочете зробити запит на додавання підручника - 
        відправляйте заявку на ел. пошту lutsenko.dmytro@lll.kpi.ua""", font=("Comic Sans MS", 11))
        self.welcome_l.pack(pady=5)
        self.proposition_l.pack(pady=15)

        self.search_fr = tk.Frame(self)
        self.search_fr.pack(pady=5)
        self.search_fr.configure(background=over_search)

        self.search_e = tk.Entry(self.search_fr, width=150)
        self.search_e.pack(side=tk.LEFT)

        self.search_b = tk.Button(self.search_fr, text="Пошук", command=self.process_search)
        self.search_b.pack(side=tk.RIGHT)

        self.results_canvas = tk.Canvas(self, bg=bg_color)
        self.results_frame = tk.Frame(self.results_canvas)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor=tk.NW)

        self.results_frame.bind("<Configure>", lambda event, canvas=self.results_canvas: App.on_frame_configure(canvas))

        self.bind('<Return>', self.search_event)

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    @staticmethod
    def on_frame_configure(canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def book_window(self, textbook):
        details_window = tk.Toplevel(self)
        details_window.title(textbook['title'])
        details_window.resizable(False, False)
        details_window.configure(background='#f3cef5')
        width, height = 1380, 780
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        details_window.geometry(f"{width}x{height}+{x}+{y}")

        image_data = base64.b64decode(textbook['image'])
        image = Image.open(BytesIO(image_data))
        img = ImageTk.PhotoImage(image)
        image_l = tk.Label(details_window, image=img)
        image_l.image = img
        image_l.pack(side=tk.LEFT, pady=10, padx=5)

        text_frame = tk.Frame(details_window)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        text_frame.configure(background='#f3cef5')
        tk.Label(text_frame, text=f"Назва: {textbook['title']}", bg="#fffae6", font=("Comic Sans MS", 9)).pack(padx=5, pady=17, anchor=tk.W)
        tk.Label(text_frame, text=f"Дисципліна: {textbook['discipline']}", bg="#fffae6", font=("Comic Sans MS", 9)).pack(padx=5, pady=17, anchor=tk.W)
        tk.Label(text_frame, text=f"Автор: {textbook['author']}", bg="#fffae6", font=("Comic Sans MS", 9)).pack(padx=5, pady=17, anchor=tk.W)
        tk.Label(text_frame, text=f"Опис: {textbook['description']}", bg="#fffae6", font=("Comic Sans MS", 9)).pack(padx=5, pady=17, anchor=tk.W)
        url_label = tk.Label(text_frame, text=f"Посилання на завантаження підручника:\n{textbook['link']}", bg="#fffae6", font=("Comic Sans MS", 9))
        url_label.pack(padx=5, pady=17, anchor=tk.W)
        url_label.bind("<Button-1>", lambda e: open_new_tab(textbook['link']))

    def process_search(self):
        query = self.search_e.get()
        if not query:
            showwarning("Input Error", "Будь ласка, введіть запит перед тим як щось шукати")
            return

        response = requests.get(f"http://127.0.0.1:5000/search_textbooks?query={query}")
        if response.status_code != 200:
            showerror("Error", f"Не вдалось опрацювати введені дані: {response.text}")
            return

        results = response.json()
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        if results:
            for result in results:
                result_frame = tk.Frame(self.results_frame)
                result_frame.pack(fill=tk.X, pady=5, padx=5)
                result_frame.configure(background=bg_color)

                if len(result["title"]) > 60:
                    title = (result["title"][:57] + "...")
                else:
                    title = result["title"]
                if len(result["discipline"]) > 40:
                    discipline = (result["discipline"][:37] + "...")
                else:
                    discipline = result["discipline"]
                if len(result["author"]) > 40:
                    author = (result["author"][:37] + "...")
                else:
                    author = result["author"]

                tk.Label(result_frame, text=title, width=65, anchor="w", bg="light yellow").pack(side=tk.LEFT)
                tk.Label(result_frame, text=discipline, width=42, anchor="w", bg="light yellow").pack(side=tk.LEFT)
                tk.Label(result_frame, text=author, width=35, anchor="w", bg="light yellow").pack(side=tk.LEFT)
                detail_b = tk.Button(result_frame, text="Детальніше", command=lambda x=result: self.book_window(x))
                detail_b.pack(side=tk.RIGHT)
        else:
            tk.Label(self.results_frame, text="За вашим запитом нічого не знайдено.", bg="light yellow").pack()

    def search_event(self, event):
        self.process_search()

    def close_app(self):
        self.destroy()