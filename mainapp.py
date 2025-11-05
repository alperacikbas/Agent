import customtkinter as ctk
import threading
import geminiagent

USER_COLOR = ("#3a7ebf", "#1f538d")
AGENT_COLOR = ("#5c5c5c", "#333333")

class OtomotivAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Otomotiv Agent")
        self.geometry("600x700")
        
        # Bu değişken, "Düşünüyor..." baloncuğunu takip etmek için kullanılacak
        self.thinking_bubble = None
        
        self.create_widgets()

    def create_widgets(self):
        # --- ÜST BÖLÜM: Logo ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=10)

        self.logo_label = ctk.CTkLabel(self.header_frame, text="Otomotiv Agent 🚗", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack()

        # --- ORTA BÖLÜM: Mesaj Ekranı ---
        # ÖNEMLİ DEĞİŞİKLİK: CTkTextbox yerine CTkScrollableFrame kullanıyoruz.
        self.chat_log = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_log.pack(fill="both", expand=True, padx=10, pady=5)

        # --- ALT BÖLÜM: Giriş Kutusu ve Gönder Butonu ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", pady=10, padx=10)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.user_input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Bir otomotiv sorusu sorun...", height=30)
        self.user_input_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.user_input_entry.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(self.input_frame, text="Gönder", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

    def append_message(self, sender, message):
        """
        Mesajları ekrandaki kaydırılabilir çerçeveye baloncuk olarak ekler.
        """
        # Baloncukların hizalanacağı taraf (sol/sağ)
        if sender == "Sen":
            align_side = "e"  # East (Doğu -> Sağ)
            bubble_color = USER_COLOR
        else:
            align_side = "w"  # West (Batı -> Sol)
            bubble_color = AGENT_COLOR

        # Mesaj baloncuğu (Label) oluştur
        bubble = ctk.CTkLabel(
            self.chat_log,
            text=message,
            fg_color=bubble_color,
            text_color="white",
            corner_radius=10,  # Köşeleri yuvarlat
            wraplength=500,     # Metin uzunsa alt satıra indir (çok önemli)
            justify="left",     # Alt satıra inen metin sola dayalı olsun
            padx=10,
            pady=5
        )
        
        # Baloncuğu çerçeveye paketle (hizalamayı ayarla)
        bubble.pack(anchor=align_side, pady=5, padx=10)
        
        # Eğer bu bir "Düşünüyor..." baloncuğuysa, referansını sakla
        if message == "Düşünüyor...":
            self.thinking_bubble = bubble
            
        # En alta kaydır
        self.scroll_to_bottom()

    def send_message_event(self, event=None):
        self.send_message()

    def send_message(self):
        user_message = self.user_input_entry.get()
        if not user_message.strip():
            return

        self.append_message("Sen", user_message)
        self.user_input_entry.delete(0, ctk.END)

        # "Düşünüyor..." baloncuğunu ekle
        self.append_message("Agent", "Düşünüyor...")
        self.send_button.configure(state="disabled")
        
        # Cevabı almak için agent_core'u kullanan thread'i başlat
        thread = threading.Thread(target=self.get_agent_response_thread, args=(user_message,))
        thread.start()

    def get_agent_response_thread(self, user_message):
        # Cevabı agent_core modülünden al
        agent_response = geminiagent.get_agent_response(user_message)
        
        # UI'ı ana thread'de güncelle
        self.after(0, self.update_chat_with_agent_response, agent_response)
        self.after(0, lambda: self.send_button.configure(state="normal"))

    def update_chat_with_agent_response(self, response):
        # ÖNEMLİ DEĞİŞİKLİK: "Düşünüyor..." baloncuğunu kaldır
        if self.thinking_bubble:
            self.thinking_bubble.destroy()  # "Düşünüyor..." baloncuğunu sil
            self.thinking_bubble = None

        # Gerçek cevabı içeren yeni Agent baloncuğunu ekle
        self.append_message("Agent", response)
        
        # En alta kaydır
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # Mesaj eklendikten sonra kaydırma çubuğunu en alta çeker
        self.chat_log._parent_canvas.yview_moveto(1.0)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = OtomotivAgentApp()
    app.mainloop()