import sqlite3
import datetime

DB_FILE = "otomotiv_chat_history.db"

def init_db():
    """
    Veritabanı dosyasını ve 'messages' tablosunu oluşturur (eğer yoksa).
    Bu fonksiyon uygulama ilk açıldığında SADECE BİR KEZ çalıştırılmalıdır.
    """
    try:
        # 'with' bloğu, bağlantının otomatik olarak açılmasını ve kapanmasını sağlar
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Konuşmaları saklayacağımız tabloyu oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    text_content TEXT,
                    image_path TEXT
                )
            """)
            conn.commit()
            print(f"Veritabanı '{DB_FILE}' başarıyla başlatıldı.")
            
    except sqlite3.Error as e:
        print(f"Veritabanı hatası (init_db): {e}")

def save_message(sender, text_content, image_path=None):
    """
    Veritabanına yeni bir mesaj kaydeder.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (timestamp, sender, text_content, image_path) VALUES (?, ?, ?, ?)",
                (timestamp, sender, text_content, image_path)
            )
            conn.commit()
            
    except sqlite3.Error as e:
        print(f"Veritabanı kaydetme hatası (save_message): {e}")