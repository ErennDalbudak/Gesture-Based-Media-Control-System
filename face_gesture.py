import cv2  # OpenCV kütüphanesini içe aktarır (görüntü işleme için)
import mediapipe as mp  # MediaPipe kütüphanesini içe aktarır (yüz ve el algılama için)
import pyautogui  # PyAutoGUI kütüphanesini içe aktarır (fare ve klavye simülasyonu için)
import math  # Matematiksel işlemler için math kütüphanesini içe aktarır
import time  # Zamanla ilgili işlemler için time kütüphanesini içe aktarır
import osascript  # MacOS için AppleScript çalıştırmak için osascript kütüphanesini içe aktarır
import subprocess  # Sistem komutları çalıştırmak için subprocess kütüphanesini içe aktarır

# MediaPipe yüz ve el algılama modellerini başlat
mp_face_mesh = mp.solutions.face_mesh  # MediaPipe yüz algılama çözümü
mp_hands = mp.solutions.hands  # MediaPipe el algılama çözümü

# Yüz mesh modeli başlatılıyor
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,  # Maksimum 1 yüz algılanacak
    min_detection_confidence=0.5,  # Yüz algılama için minimum güven seviyesini belirler
    min_tracking_confidence=0.5  # Yüz izleme için minimum güven seviyesini belirler
)

# El algılama modeli başlatılıyor
hands = mp_hands.Hands(
    static_image_mode=False,  # Hareketli görüntü için
    max_num_hands=2,  # Maksimum 2 el algılanacak
    min_detection_confidence=0.7,  # El algılama için minimum güven seviyesi
    min_tracking_confidence=0.7  # El izleme için minimum güven seviyesi
)

# PyAutoGUI ayarları
pyautogui.FAILSAFE = False  # Ekran köşesine yaklaşınca otomatik durmayı engeller
pyautogui.PAUSE = 0.1  # Her PyAutoGUI komutundan sonra 0.1 saniye bekleme

# Kamerayı başlat
print("Kamera başlatılıyor...")
cap = cv2.VideoCapture(0)  # Webcam'den görüntü almak için video capture başlatılır

if not cap.isOpened():  # Eğer kamera açılamazsa
    print("Kamera açılamadı!")  # Hata mesajı yazdır
    exit()  # Programı sonlandır

def set_volume(volume_percentage):  # Ses düzeyini ayarlamak için fonksiyon
    """Sistem ses seviyesini ayarlar"""
    volume = float(volume_percentage)  # Ses düzeyini float türüne dönüştür
    osascript.osascript(f"set volume output volume {volume}")  # AppleScript komutuyla sesi ayarlama

def calculate_distance(x1, y1, x2, y2):  # İki nokta arasındaki mesafeyi hesaplamak için fonksiyon
    """İki nokta arasındaki mesafeyi hesaplar"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  # Öklidyen mesafe formülü

def calculate_face_rotation(face_landmarks):  # Yüzün dönüş açısını hesaplamak için fonksiyon
    """Yüz rotasyonunu ve eğimini hesaplar"""
    left_face = face_landmarks.landmark[234]  # Yüzün sol tarafındaki nokta
    right_face = face_landmarks.landmark[454]  # Yüzün sağ tarafındaki nokta
    nose = face_landmarks.landmark[4]  # Burnun noktası
    
    face_center_x = (left_face.x + right_face.x) / 2  # Yüzün ortalama noktası
    rotation = nose.x - face_center_x  # Yüzün sağa/sola dönüşünü hesaplar
    
    forehead = face_landmarks.landmark[151]  # Alın noktası
    nose_tip = face_landmarks.landmark[4]  # Burun ucu
    chin = face_landmarks.landmark[152]  # Çene noktası
    
    tilt = (nose_tip.y - forehead.y) / (chin.y - forehead.y)  # Yüzün yukarı/aşağı eğimi
    
    return rotation, tilt  # Yüz dönüşü ve eğimi döndürür

def control_music():  # Müzik kontrolü için fonksiyon
    """Müzik kontrolü için MacOS medya tuşlarını kullanır"""
    try:
        osascript.osascript('''
            tell application "Spotify"
                if player state is playing then
                    pause  # Eğer müzik çalıyorsa durdur
                else
                    play  # Eğer müzik duruyorsa başlat
                end if
            end tell
        ''')
    except Exception as e:
        print(f"Müzik kontrol hatası: {e}")  # Hata mesajı

def lock_screen():  # Ekranı kilitlemek için fonksiyon
    """Ekranı kilitler"""
    try:
        subprocess.run(['pmset', 'displaysleepnow'])  # MacOS komutuyla ekranı kilitleme
    except Exception as e:
        print(f"Ekran kilitleme hatası: {e}")  # Hata mesajı

# Gesture yapıldı mı kontrolü için değişkenler
last_gesture_time = 0  # Son yapılan hareket zamanı
gesture_cooldown = 1.0  # Hareketler arasındaki bekleme süresi (saniye)
last_music_state = False  # Son müzik durumu
last_lock_time = 0  # Son ekran kilitleme zamanı

print("Program başlatıldı. Çıkmak için 'q' tuşuna basın.")  # Program başlatıldığında yazdırılır

while True:
    success, img = cap.read()  # Kamera görüntüsünü al
    if not success:  # Eğer görüntü alınamazsa
        print("Kamera görüntüsü alınamadı!")  # Hata mesajı yazdır
        break  # Döngüyü sonlandır
    
    img = cv2.flip(img, 1)  # Görüntüyü yatayda çevir
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR'yi RGB'ye dönüştür
    
    face_results = face_mesh.process(imgRGB)  # Yüz tespiti
    hand_results = hands.process(imgRGB)  # El tespiti
    
    h, w, c = img.shape  # Görüntü boyutlarını al
    current_time = time.time()  # Geçerli zaman (saniye cinsinden)
    
    if hand_results.multi_hand_landmarks:  # Eğer eller algılandıysa
        for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):  # Her bir el için
            handedness = hand_results.multi_handedness[idx].classification[0].label  # Elin sağ mı sol mu olduğunu kontrol et
            
            if handedness == "Left":  # Sol el için
                mp.solutions.drawing_utils.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0,255,0), thickness=2),
                    mp.solutions.drawing_utils.DrawingSpec(color=(0,255,0), thickness=2)
                )  # Elin işaretlerini çiz
                
                thumb_tip = hand_landmarks.landmark[4]  # Baş parmak ucu
                index_tip = hand_landmarks.landmark[8]  # İşaret parmağı ucu
                
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)  # Baş parmak koordinatları
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)  # İşaret parmağı koordinatları
                
                distance = calculate_distance(thumb_x, thumb_y, index_x, index_y)  # Parmağın mesafesini hesapla
                volume = int((distance - 50) / 200 * 100)  # Ses seviyesini mesafeye göre hesapla
                volume = max(0, min(100, volume))  # Ses seviyesini 0 ile 100 arasında tut
                
                set_volume(volume)  # Ses seviyesini ayarla
                
                cv2.putText(img, f'Volume: {volume}%', (10, 70), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Ses seviyesi yazısını ekle
                
                # Parmaklar arasındaki mesafeyi çiz
                cv2.circle(img, (thumb_x, thumb_y), 15, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)
                
                cv2.putText(img, f'Sol El - Ses Kontrolu', (10, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)  # Sol el için yazı ekle
            
            elif handedness == "Right":  # Sağ el için
                mp.solutions.drawing_utils.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0,0,255), thickness=2),
                    mp.solutions.drawing_utils.DrawingSpec(color=(0,0,255), thickness=2)
                )  # Elin işaretlerini çiz
                
                thumb_tip = hand_landmarks.landmark[4]  # Baş parmak ucu
                index_tip = hand_landmarks.landmark[8]  # İşaret parmağı ucu
                
                distance = calculate_distance(
                    thumb_tip.x * w, thumb_tip.y * h,
                    index_tip.x * w, index_tip.y * h
                )  # Parmağın mesafesini hesapla
                
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)  # Baş parmak koordinatları
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)  # İşaret parmağı koordinatları
                cv2.circle(img, (thumb_x, thumb_y), 15, (0, 0, 255), cv2.FILLED)  # Parmakları çiz
                cv2.circle(img, (index_x, index_y), 15, (0, 0, 255), cv2.FILLED)  # Parmakları çiz
                cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 3)  # Parmağın mesafesini çiz
                
                current_music_state = distance < 40  # Müzik kontrolü için mesafe
                if current_music_state != last_music_state and current_time - last_gesture_time >= gesture_cooldown:  # Mesafe değiştiyse müzik durdurulup başlatılacak
                    print("Müzik durduruluyor/oynatılıyor...")
                    control_music()  # Müzik kontrol fonksiyonunu çalıştır
                    last_gesture_time = current_time  # Son hareket zamanını güncelle
                
                last_music_state = current_music_state  # Son müzik durumunu güncelle
                
                cv2.putText(img, f'Parmak Mesafesi: {int(distance)}', (w-300, 70), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # Parmak mesafesi yazısını ekle
                
                cv2.putText(img, f'Sag El - Muzik Kontrolu', (w-300, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # Sağ el için yazı ekle
    
    if face_results.multi_face_landmarks:  # Eğer yüz algılandıysa
        for face_landmarks in face_results.multi_face_landmarks:  # Her bir yüz için
            rotation, tilt = calculate_face_rotation(face_landmarks)  # Yüz dönüşü ve eğimini hesapla
            
            if current_time - last_gesture_time >= gesture_cooldown:  # Hareketler arasında bekleme süresi
                if rotation < -0.04:  # Yüz sağa hareket ettiyse
                    print("Sağa hareket -> Üç parmak sağa kaydırma")
                    pyautogui.keyDown('ctrl')  # Ctrl tuşuna bas
                    pyautogui.keyDown('right')  # Sağ ok tuşuna bas
                    pyautogui.keyUp('right')  # Sağ ok tuşunu bırak
                    pyautogui.keyUp('ctrl')  # Ctrl tuşunu bırak
                    last_gesture_time = current_time  # Son hareket zamanını güncelle
                elif rotation > 0.04:  # Yüz sola hareket ettiyse
                    print("Sola hareket -> Üç parmak sola kaydırma")
                    pyautogui.keyDown('ctrl')  # Ctrl tuşuna bas
                    pyautogui.keyDown('left')  # Sol ok tuşuna bas
                    pyautogui.keyUp('left')  # Sol ok tuşunu bırak
                    pyautogui.keyUp('ctrl')  # Ctrl tuşunu bırak
                    last_gesture_time = current_time  # Son hareket zamanını güncelle
            
            # Aşağı bakma kontrolü ve kilitleme
            if tilt > 0.65 and current_time - last_lock_time >= 1.0:  # 1 saniye ara ile kilitleme
                print("Aşağı bakış -> Ekran kilitleniyor...")
                lock_screen()  # Ekran kilitleme fonksiyonunu çalıştır
                last_lock_time = current_time  # Son ekran kilitleme zamanını güncelle
            
            # Yüz işaretlerini çiz
            drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1, color=(0,255,0))
            mp.solutions.drawing_utils.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )
            
            # Yüz yönü ve eğimini yazıya dök
            direction = "Sağa Dönük" if rotation < -0.05 else "Sola Dönük" if rotation > 0.05 else "Düz"
            tilt_text = "Aşağı Bakıyor" if tilt > 0.65 else "Düz"
            cv2.putText(img, f"{direction} | {tilt_text}", (10, 130), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Yüz yönünü ve eğimini ekrana yazdır
    
    cv2.imshow("Gesture Control", img)  # Görüntüyü ekranda göster
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' tuşuna basıldığında döngü durur
        break  # Döngüyü sonlandır

# Temizlik
cap.release()  # Kamerayı serbest bırak
cv2.destroyAllWindows()  # OpenCV penceresini kapat
