<template>
  <router-view></router-view>
</template>

<script lang="ts">
import $store from '@/store/index'
import router from "@/router";
export default {
  
  name: 'App',
  mounted() {
    const Token = $store.getters.getToken
    if(!Token){
      localStorage.removeItem("userToken");
      $store.commit('setToken', '');
      router.replace({ path: "/" });
    }
    
  },
}
</script>
