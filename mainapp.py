import customtkinter as ctk
import threading
from tkinter import filedialog
from PIL import Image, ImageTk
import geminiagent
import database

USER_COLOR = ("#3a7ebf", "#1f538d")
AGENT_COLOR = ("#5c5c5c", "#333333")
INPUT_BG_COLOR = ("#F9F9FA", "#343638")

class OtomotivAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Otomotiv Agent")
        self.geometry("750x800")
        
        self.thinking_bubble = None
        self.selected_image_path = None
        
        self.create_widgets()

    def create_widgets(self):
        #Logo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=10)
        self.logo_label = ctk.CTkLabel(self.header_frame, text="Otomotiv Agent 🚗", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack()

        #Mesaj Ekranı
        self.chat_log = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #Giriş Alanı Ana Çerçevesi
        self.input_area_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_area_main_frame.pack(fill="x", padx=10, pady=(0, 20))
        self.input_area_main_frame.grid_columnconfigure(0, weight=1)
        self.input_area_main_frame.grid_columnconfigure(1, weight=0)

        #GİRİŞ ALANI KONTEYNERİ
        self.input_container = ctk.CTkFrame(self.input_area_main_frame, fg_color=INPUT_BG_COLOR, 
                                            border_width=2, border_color=("#979DA2", "#565B5E"))
        self.input_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        #Resim Önizleme Etiketi
        self.preview_image_label = ctk.CTkLabel(self.input_container, text="", fg_color="transparent")

        #Silme Butonu
        self.delete_image_button = ctk.CTkButton(
            self.input_container,
            text="✕",
            width=20, height=20,
            corner_radius=5,
            fg_color="#CC0000",
            hover_color="#A00000",
            bg_color=INPUT_BG_COLOR, # Arkasındaki gri kutunun rengini alacak
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.clear_selected_image
        )

        #Metin Kutusu
        self.user_input_textbox = ctk.CTkTextbox(self.input_container, height=80, fg_color="transparent", 
                                                 font=ctk.CTkFont(size=14), border_width=0, wrap="word")
        self.user_input_textbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.user_input_textbox.insert("0.0", "Buraya yazın...")
        self.user_input_textbox.bind("<FocusIn>", self.clear_placeholder)

        #BUTON GRUBU
        self.button_frame = ctk.CTkFrame(self.input_area_main_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="ns")

        self.select_image_button = ctk.CTkButton(self.button_frame, text="Resim\nYükle", width=80, height=38, command=self.select_image)
        self.select_image_button.pack(side="top", pady=(0, 4))

        self.send_button = ctk.CTkButton(self.button_frame, text="Gönder", width=80, height=38, command=self.send_message, 
                                         fg_color="#2CC985", hover_color="#26AD73")
        self.send_button.pack(side="bottom")

    def clear_placeholder(self, event):
        if self.user_input_textbox.get("0.0", "end-1c") == "Buraya yazın...":
            self.user_input_textbox.delete("0.0", "end")

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Bir resim dosyası seçin",
            filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            
            original_image = Image.open(self.selected_image_path)
            
            # Resmi orantılı olarak yeniden boyutlandır
            max_width = 100
            max_height = 80
            original_width, original_height = original_image.size
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            # LANCZOS ile kaliteli küçültme
            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            ctk_image = ImageTk.PhotoImage(resized_image)
            
            # Etiketi resim boyutuna göre ayarla ve resmi göster
            self.preview_image_label.configure(image=ctk_image, text="", width=new_width, height=new_height)
            self.preview_image_label.image = ctk_image
            self.preview_image_label.pack(side="left", padx=(5, 0), pady=5, before=self.user_input_textbox)

            # Silme butonunu yerleştir
            self.delete_image_button.place(in_=self.preview_image_label, relx=1.0, rely=0.0, anchor="ne", x=5, y=-5)
            self.delete_image_button.lift()

    def clear_selected_image(self):
        self.selected_image_path = None
        self.preview_image_label.configure(image=None, width=0, height=0)
        self.preview_image_label.pack_forget()
        self.delete_image_button.place_forget()

    def append_message(self, sender, message, image_path=None):
        if sender == "Sen":
            align_side = "e"
            bubble_color = USER_COLOR
        else:
            align_side = "w"
            bubble_color = AGENT_COLOR

        message_master_frame = ctk.CTkFrame(self.chat_log, fg_color="transparent")
        message_master_frame.pack(anchor=align_side, pady=5, padx=10)

        if image_path:
            try:
                original_image = Image.open(image_path)
                original_image.thumbnail((250, 250))
                ctk_image = ImageTk.PhotoImage(original_image)
                image_label = ctk.CTkLabel(message_master_frame, image=ctk_image, text="")
                image_label.image = ctk_image
                bottom_padding = 5 if message.strip() else 0
                image_label.pack(pady=(0, bottom_padding))
            except Exception as e:
                print(f"Resim yükleme hatası: {e}")

        if message.strip() or (not image_path and message.strip() == ""):
            bubble = ctk.CTkLabel(message_master_frame, text=message, fg_color=bubble_color, text_color="white",
                                  corner_radius=10, wraplength=500, justify="left", padx=10, pady=5)
            bubble.pack(anchor=align_side)

        if message == "Düşünüyor...":
            self.thinking_bubble = message_master_frame
        self.scroll_to_bottom()

    def send_message(self):
        user_message = self.user_input_textbox.get("0.0", "end-1c").strip()
        if user_message == "Buraya yazın...": user_message = ""

        if not user_message and not self.selected_image_path:
            return

        #Seçili resmin yolunu önce bir yedeğe alıyoruz!
        current_image_path = self.selected_image_path

        # Ekrana mesajı eklerken yedeği kullanıyoruz
        self.append_message("Sen", user_message, current_image_path)

        database.save_message(sender="Sen", text_content=user_message, image_path=current_image_path)
        
        self.user_input_textbox.delete("0.0", "end")
        self.clear_selected_image() # Şimdi temizleyebiliriz, çünkü yedeğimiz var.

        self.append_message("Agent", "Düşünüyor...")
        self.send_button.configure(state="disabled")
        if hasattr(self, 'select_image_button'):
             self.select_image_button.configure(state="disabled")
        
        # Thread'e yedeği (current_image_path) gönder
        thread = threading.Thread(target=self.get_agent_response_thread, args=(user_message, current_image_path))
        thread.start()

    def get_agent_response_thread(self, user_message, image_path):
        agent_response = geminiagent.get_agent_response(user_message, image_path)
        self.after(0, self.update_chat_with_agent_response, agent_response)
        self.after(0, lambda: self.send_button.configure(state="normal"))
        self.after(0, lambda: self.select_image_button.configure(state="normal"))

    def update_chat_with_agent_response(self, response):
        if self.thinking_bubble:
            self.thinking_bubble.destroy()
            self.thinking_bubble = None
        self.append_message("Agent", response)

        database.save_message(sender="Agent", text_content=response, image_path=None)

        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.after(10, lambda: self.chat_log._parent_canvas.yview_moveto(1.0))

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    database.init_db()
    app = OtomotivAgentApp()
    app.mainloop()