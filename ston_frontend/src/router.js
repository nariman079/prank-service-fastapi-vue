import { createWebHistory, createRouter } from 'vue-router'
import MainPage from './MainPage.vue'


const routes = [
  {  path: '/:telegram_hash', component: MainPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router