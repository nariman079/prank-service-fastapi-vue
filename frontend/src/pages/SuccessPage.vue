<template>
        
        <CInformationAbout></CInformationAbout>
</template>

<script>
import CInformationAbout from '@/components/cInformationAbout.vue';



    export default {
        name: "SuccessPage",
        components:{CInformationAbout},
        data (){
            return {

            }
        }
    }
</script>

<style>
body{
    display: flex;
    justify-content: center;

}
.cm{
    margin-top: 15px;
}
@media (max-width:525px) {
    body{
      flex-direction: column;
      justify-content: flex-start;
    }
  
  }
</style>