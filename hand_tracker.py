import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self):
        # 1. Khởi tạo MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, # Chế độ video (luồng liên tục)
            max_num_hands=1,         # Chỉ nhận diện 1 tay
            min_detection_confidence=0.7, # Ngưỡng tin cậy phát hiện tay
            min_tracking_confidence=0.7   # Ngưỡng tin cậy theo dõi tay
        )
        
        # 2. Khởi tạo công cụ vẽ của MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        # Định nghĩa cách vẽ: Màu sắc, độ dày cho điểm và đường nối
        self.hand_drawing_spec = self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2) # Điểm xanh lá
        self.connector_drawing_spec = self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2) # Đường đỏ

        # 3. Mở Camera mặc định (0)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            # Nếu không được, thử Camera ID khác (1)
            self.cap = cv2.VideoCapture(1)
            
        if not self.cap.isOpened():
            print("--- LOI: Khong tim thay Camera! ---")

        self.is_pinched = False # Biến trạng thái để tránh chim nhảy liên tục

    def check_jump(self):
        # Kiểm tra xem camera có mở không
        if not self.cap or not self.cap.isOpened():
            return False
            
        success, img = self.cap.read()
        if not success:
            print("--- LOI: Khong doc duoc anh tu Camera! ---")
            return False
            
        # --- XỬ LÝ ẢNH ---
        img = cv2.flip(img, 1) # Lật ảnh gương để hướng tay đúng chiều
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Chuyển đổi sang hệ màu RGB cho MediaPipe
        results = self.hands.process(img_rgb) # Nhận diện bàn tay
        
        # --- VẼ KHUNG TRACKING LÊN ẢNH ---
        jump = False
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ các điểm và đường nối bàn tay lên ảnh 'img'
                self.mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.hand_drawing_spec,
                    self.connector_drawing_spec
                )
                
                # --- LOGIC NHẬN DIỆN CHỤM TAY ---
                # Lấy tọa độ đầu ngón cái (4) và ngón trỏ (8)
                thumb = hand_landmarks.landmark[4]
                index = hand_landmarks.landmark[8]
                
                # Tính khoảng cách giữa 2 đầu ngón tay
                distance = math.hypot(index.x - thumb.x, index.y - thumb.y)
                
                # Ngưỡng chụm tay (0.05 là rất gần)
                if distance < 0.05:
                    if not self.is_pinched: # Chỉ nhảy 1 lần khi bắt đầu chụm
                        jump = True
                        self.is_pinched = True
                        # Vẽ một vòng tròn lớn ở vị trí chụm để báo hiệu
                        h, w, c = img.shape
                        cx, cy = int(index.x * w), int(index.y * h)
                        cv2.circle(img, (cx, cy), 15, (0, 255, 255), cv2.FILLED)
                else:
                    self.is_pinched = False
                    
        # --- HIỂN THỊ CỬA SỔ CAMERA ---
        # Thêm dòng chữ hướng dẫn lên màn hình cam
        #cv2.putText(img, "CHUM NGON CÁI & TRO DE NHAY/CHOI LAI", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Hiển thị cửa sổ cam với tên là "MediaPipe Hand Tracking"
        cv2.imshow("MediaPipe Hand Tracking", img)
        
        # Một dòng quan trọng để OpenCV cập nhật cửa sổ và xử lý sự kiện
        cv2.waitKey(1) 
                    
        return jump

    def close(self):
        print("--- Dang dong Camera... ---")
        if self.cap and self.cap.isOpened():
            self.cap.release() # Giải phóng camera
        cv2.destroyAllWindows() # Đóng tất cả cửa sổ OpenCV