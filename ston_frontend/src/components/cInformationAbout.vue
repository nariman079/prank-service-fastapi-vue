<template>
    <div class="info-block">
        <img src="@/assets/img/result_prank.png" alt="">
        <h1>Вас пранканули с помошью телеграм бота @WallPrankBot</h1>
        <h3>Вы сели на подушку пердушку </h3>
        <a :href="prankBotURL">Попробывать также</a>
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
        width: 500px;
        height: max-content;
        display: flex;
        margin: 50px auto;
        background-color: #2b2b2b;
        color: aliceblue;
        border-radius: 30px;
        padding: 35px;
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
        padding: 10px 30px;
        background-color: #000000;
        border-radius: 6px;
        margin-bottom: 5px;
    }
    p{
        font-size: 30px;
        font-weight: 900;
    }
    @media (max-width:1024px) {
        .info-block{
            width: 70%;
        }
    }
</style>