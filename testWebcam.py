from Face.Inference.Facenet import Facenet
import cv2

fn = Facenet()
camera = cv2.VideoCapture(0)

while True:
    ret, img = camera.read()
    if ret:
        try:
            # Lấy ra danh tính, khoảng cách và HCN bao gương mặt
            identity, distance = fn.Get_People_Identity_SVM(img)[0]
            # In ra console
            print("Identity : ", identity, " - ", "Distance : ", distance)
        except Exception as e:
            print(e)
        # Hiển thị khung hình
        cv2.imshow("Picture", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

# 255,0,0 : blue
