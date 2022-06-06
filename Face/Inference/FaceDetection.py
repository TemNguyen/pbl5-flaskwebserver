from mtcnn import MTCNN
import cv2


def area(x, y, xw, yh):
    """
        Hàm tính diện tích 1 khung HCN
        """
    return (xw-x)*(yh-y)


class FaceDetection():
    def __init__(self):
        # Sử dụng mạng MTCNN
        self.detector = MTCNN()

    def Detect_Face(self, image, resize=True, scale=4):
        """
        Hàm trả về tọa độ 2 đỉnh 2 góc của HCN bao quanh khuôn mặt
        image : ảnh
        resize : có giảm kích thước ảnh hay không nhằm tăng tốc độ xử lý
        scale : tỉ lệ giảm kích thước ảnh
        """
        img = image.copy()
        # Giảm kích thước
        if resize:
            width = img.shape[0]
            height = img.shape[1]
            img = cv2.resize(img, (height//scale, width//scale))

        # MTCNN phát hiện gương mặt
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(rgb_img)
        # Lưu lại tọa độ 2 đỉnh HCN
        rec = []
        for f in faces:
            x, y, w, h = f["box"]
            # Nếu có giảm kích thước thì toạ độ cần trả về giá trị trước khi resize
            if resize:
                rec.append([x*scale, y*scale, (x+w)*scale, (y+h)*scale])
            else:
                rec.append([x, y, x+w, y+h])
        return rec

    def Crop_Face(self, image, rec):
        """
        Hàm trả về ma trận của khuôn mặt detect được có diện tích lớn nhất
        image : ảnh
        rec : list chứa tọa độ HCN
        """
        img = image.copy()

        # Chỉ lấy ra khung HCN có diện tích lớn nhất
        # Ứng với khuôn mặt gần Camera nhất
        max_index = -1
        max_area = 0
        for i in range(len(rec)):
            x, y, xw, yh = rec[i]
            rec_area = area(x, y, xw, yh)
            if rec_area > max_area:
                max_index = i
                max_area = rec_area
        # Tọa độ và ma trận hình ảnh khuôn mặt
        x1, y1, x2, y2 = rec[max_index]
        # Trả về list trong list để không phá vỡ cấu trúc của các API đã viết
        # và dễ dàng mở rộng hơn thành bài toàn nhận diện nhiều khuôn mặt
        return [img[y1:y2, x1:x2]]
