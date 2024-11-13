import { createRouter, createWebHistory } from 'vue-router'

import MainPage from '@/pages/MainPage.vue'
import SuccessPage from './pages/SuccessPage.vue'
import ReplaceTG from './pages/ReplaceTG.vue'

const routes = [
  {name: 'replacetg', path: '/', component: ReplaceTG},
  { name: 'main', path: '/:telegram_id', component: MainPage  },
  { name:'success_page', path:'/p/success', component: SuccessPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router