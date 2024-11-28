from moviepy import VideoFileClip


def capture_middle_frame(video_path, output_image_path):
    try:
        # Загружаем видео
        clip = VideoFileClip(video_path)

        # Вычисляем время середины видео
        middle_time = clip.duration / 2

        # Получаем кадр в середине видео
        frame = clip.get_frame(middle_time)

        # Сохраняем кадр как изображение
        from PIL import Image
        image = Image.fromarray(frame)
        image.save(output_image_path)

        print(f"Скриншот сохранён: {output_image_path}")
    except Exception as e:
        print(f"Ошибка: {e}")


# Пример использования
video_path = "tests/test_uploads/uud1.webm"  # Укажите путь к видео
output_image_path = "middle_frame.png"  # Укажите путь для сохранения скриншота
capture_middle_frame(video_path, output_image_path)
