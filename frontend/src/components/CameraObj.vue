<template>
    <div class="screen_components">
      
      <div class="back_block">
        <div class="close_button"><img width="20" src="@/assets/img/x.png" alt=""></div>
        <div class="sound_title"><img src="@/assets/img/music.png" alt="">Sound</div>
        <div class="reload_button"><img src="@/assets/img/reload.png" alt=""></div>
      </div>
      <div class="control_block">
        <div>
          
        </div>
        <div class="">
          <div class="control_button">
            <img src="@/assets/img/speed.png"  alt="">
            <span></span>
          </div>
          <div class="control_button">
            <img src="@/assets/img/rotate.png"  alt="">
            <span></span>
          </div>
          <div class="control_button">
            <img src="@/assets/img/star.png"  alt="">
            <span></span>
          </div>
        </div>
        <CLoader class="loader"></CLoader>
      </div>
      
      <div class="empty_block"></div>
      <div class="empty_block"></div>
      <div class="empty_block"></div>
      <div class="empty_block"></div>
      <div class="camera_block">
        <div class="effect_obj">
          <img src="@/assets/img/luky.png" alt="">
          <span>Эффекты</span>
        </div>
        <div class="camera_obj">
          <img src="@/assets/img/came.png" alt="">
          
        </div>
        <div class="upload_obj">
          <img src="@/assets/img/square.png" alt="">
          <span>Загрузить</span>
        </div>
      </div>
    </div>
  
</template>

<script>
import CLoader from './cLoader.vue';

export default {
  name: 'CameraComponent',
  components: {
    CLoader
  },

}
</script>

<style>
*{
  font-family: 'Roboto', sans-serif;
}
.loader{
  position: absolute;
  display: block;
  margin: auto;

}
.screen_components{
  border-radius: 16px;
  padding: 20px 0;
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
  width: 500px;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  justify-content: space-between;
}
.back_block{
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.close_button{
  font-size: 30px;
}
.sound_title img{
  width: 30px;
  height: 30px;
  margin-right: 10px; 
}
.sound_title{
  background-color: #2b2b2b;
  padding: 7px 20px;
  border-radius: 3px;

  display: flex;
  align-items: center
}
.reload_button img{
  width: 30px;
  height: 30px;
}
.control_block{
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: end;

}
.control_button{
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.control_button img{
  margin: 3px;
  width: 35px;
  height: 35px;
}
.control_button span{
  font-size: 15px;
  margin: 3px;
}
.camera_block{
  display: flex;
  justify-content: space-evenly;
  align-items: end;
}
.camera_obj, .effect_obj, .upload_obj{
  display: flex;
  flex-direction: column;
  align-items: center;
}
.camera_obj span, .effect_obj span, .upload_obj span{  
  margin-top: 4px;
  font-size: 15px;
}
.effect_obj img, .upload_obj img{
  width: 60px;
}
.camera_obj img{
  width:90px ;
}
@media (max-width:525px) {
  .sound_title img{
    width: 20px;
    height: 20px;
    margin-right: 10px;
  }
  .control_button{
    padding: 10px;

  }
  .control_button img{
    margin: 3px;
    width: 25px;
    height: 25px;
  }
  .control_button span{
    font-size: 12px;
    margin: 3px;
  }
    .screen_components{
      width: 100%;
      border-radius: 0;
      margin: 0;
    }
    .camera_obj span, .effect_obj span, .upload_obj span{  
      margin-top: 2px;
      font-size: 13px;
    }
    .effect_obj img, .upload_obj img{
      width: 40px;
    }
    .camera_obj img{
      width:60px ;
    }
}
</style>

