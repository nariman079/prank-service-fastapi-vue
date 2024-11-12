<template>
    <div class="info-block">
        <img src="@/assets/img/result_prank.png" alt="">
        <h1>Вас пранканули с помошью телеграм бота @WallPrankBot</h1>
        <h3>Вы сели на подушку пердушку </h3>
        <h5>Ваша фотография отправлена владельцу ссылки </h5>

        <a href="https://t.me/@WallPrankBot">Попробывать также </a>
    </div>
</template>
<script>
export default {
    name: 'cInformationAbout',
    data () {
        return {
            prankBotURL: 'https://t.me/@WallPrankBot'
        }
    }
}
</script>
<style scoped>
    .info-block{
        display: flex;
        margin: auto;
        height: max-content;
        background-color: #2b2b2b;
        color: aliceblue;
        border-radius: 30px;
        padding: 10%;
        border: 3px solid black;
        flex-direction: column;
    }
    img{
        width: 200px;
        height: 200px;
        margin: auto
    }
    a{
        text-align: center;
        display: block;
        text-decoration: none;
        color: white;
        padding: 10px 50px;
        background-color: #000000;
        border-radius: 6px;
        margin-bottom: 5px;
    }
    p{
        font-size: 30px;
        font-weight: 900;
    }
</style>