<template>
    <div v-if="isPranked" class="main_block">
        <p class="close_button"><img @click="playSound" width="20" src="@/assets/x.png" alt=""></p>
        <p class="varmirg-message">
            Вы посетили вредоносный сайт!
        </p>
        <p class="info-message">
            Ваш телеграм аккаунт удалиться через <b class="timer">{{ timerCount }}</b> !!!
        </p>
        <p @click="playSound" class="cancel_delete_button"><b>Отменить удаление</b></p>
    </div>
    <CInformationAbout v-if="!isPranked"></CInformationAbout>
</template>
<script>
import CInformationAbout from './components/cInformationAbout.vue';

export default {
     name: 'MainPage',
     components: {CInformationAbout},
     data() {
            return {
                timerCount: 60,
                isPranked: true,
                mainAudio: new Audio(require("@/assets/sounc.mp3")),
                baseUrl: "https://tiktok.copicon.ru/api/v1/statistics/add_moan/?telegram_id_hash=" + this.$route.params.telegram_hash
            }
        },
        methods: {
            async sendStatistic(){
                const response = await fetch(
                    this.baseUrl,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    
                    }
                ) 
                if (response.ok){
                    console.log("added statistic")
                }else{
                    console.log("error: ", response.json())
                }
                 
            },
            playSound(){
                this.mainAudio.addEventListener('ended', ()=>{
                    this.mainAudio.currentTime = 0
                    // this.mainAudio.play()
                }, false)
                this.isPranked = false
                // this.mainAudio.play()
                this.sendStatistic()
            }
        },
        watch: {
            timerCount: {
                handler(value) {
                    if (value > 0) {
                        setTimeout(() => {
                            this.timerCount--;
                        }, 1000);
                    }
                    if (value == 0){
                        this.playSound()
                    }
                },
                immediate: true // This ensures the watcher is triggered upon creation
            }
        }
}
</script>
<style>
    .main_block{
        border-radius: 20px;
        margin: 100px auto;
        padding: 20px 50px;
        background-color: #2c2c2c;
        color: aliceblue;
        width: max-content;
        height: max-content;
    }
    .varmirg-message{
        color: aliceblue;
        font-size: 24px;
    }
    .close_button{
        text-align: right;
        cursor: pointer;
    }
    .cancel_delete_button{
        cursor: pointer;
        margin-top: 40px;
        font-weight: 900;
        text-align: center;
        padding: 10px;
        background-color: red;
        border-radius: 6px;
    }
    .timer{
        color: red;
        background-color: aliceblue;
        padding: 3px;
        border-radius:10px;
    }
    @media (max-width:470px) {
        .main_block{
            width: 70%;
            height: auto;
            padding: 10px 30px;
        }
        
    }
</style>