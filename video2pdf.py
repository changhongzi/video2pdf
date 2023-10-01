
import cv2
import os
from PIL import Image
from fpdf import FPDF
import numpy as np


def frame_diff(prev_frame, cur_frame):
    # 计算两帧之间的MSE
    err = np.sum((prev_frame.astype("float") - cur_frame.astype("float")) ** 2)
    err /= float(prev_frame.shape[0] * prev_frame.shape[1])
    return err


# 间隔解析视频帧，如果相近的两帧之间有差异则保存帧为图片
def video2image(video_path,img_path, threshold=1000, interval=1):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频的帧率
    frame_interval = int(fps * interval)  # 计算每秒需要跳过的帧数
    ret, prev_frame = cap.read()
    if not ret:
        print("Can't read video file!")
        return
    frame_count = 0
    while True:
        for _ in range(frame_interval):  # 跳过interval秒的帧
            ret, _ = cap.read()
            if not ret:
                break
        ret, cur_frame = cap.read()
        if not ret:
            break
        # 检查当前帧是否为None
        if cur_frame is None:
            break
        # 计算当前帧和前一帧之间的MSE
        mse = frame_diff(prev_frame, cur_frame)
        # 如果MSE得分高于阈值，则保存当前帧
        if mse > threshold:
            cv2.imwrite(f'{img_path}/frame_{frame_count}.png', cur_frame)
        prev_frame = cur_frame
        frame_count += 1
    cap.release()

# 将图片转换为pdf文件
def image2pdf(image_directory,pdf_name="output.pdf"):
    # 图片目录
    images = [img for img in os.listdir(image_directory) if img.endswith(".png")]
    if len(images) ==0:
        print(f"{image_directory}下没有可用的图片")
        return
    
    sorted_images = sorted(images, key=lambda x: os.path.getmtime(os.path.join(image_directory, x)))
    # print(sorted_images)
    pdf =None
    # 遍历图片列表
    for image in sorted_images:
        # 打开图片文件
        img = Image.open(os.path.join(image_directory, image))
        # 获取图片的原始尺寸
        width, height = img.size
        # 将图片的尺寸转换为毫米
        width, height = width * 0.264583, height * 0.264583
        # 创建一个新的FPDF对象，设置页面大小为图片的尺寸
        if pdf is None:
            pdf = FPDF(unit = "mm", format = (width, height))
        # 将图片添加到PDF
        pdf.add_page()
        pdf.image(os.path.join(image_directory, image), 0, 0, width, height)
        # 保存PDF文件
    pdf.output(f"{pdf_name}", "F")


# 删除目录下所有文件
def delete_files_in_directory(directory):
    # 获取目录中的所有文件和子目录
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 判断是否为文件
        if os.path.isfile(file_path):
            # 删除文件
            os.remove(file_path)
        # 如果是子目录，则递归调用删除函数
        elif os.path.isdir(file_path):
            delete_files_in_directory(file_path)

if __name__ == "__main__":
    img_path=".images"
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    url = input("请输入视频源链接「支持本地和远程地址,/tmp/a.mp4,https://xxx/xx/a.mp4」: ")
    while not url:
        url = input("请输入视频源链接「支持本地和远程地址,/tmp/a.mp4,https://xxx/xx/a.mp4」: ")

    pdf_name = input("请输入pdf名称:")
    if not pdf_name:
        pdf_name = "output.pdf"
        print("输入为空，将以output.pd默认输出")
    video2image(url,img_path, interval=1)
    image2pdf(img_path,pdf_name)
    delete_files_in_directory(img_path)
    print("运行完成")
