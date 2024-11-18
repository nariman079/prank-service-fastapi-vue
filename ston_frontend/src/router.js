import { createWebHistory, createRouter } from 'vue-router'
import MainPage from './MainPage.vue'
import ReplaceTG from './components/ReplaceTG.vue'


const routes = [
  {path: '/', component: ReplaceTG},
  {  path: '/:telegram_hash', component: MainPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router