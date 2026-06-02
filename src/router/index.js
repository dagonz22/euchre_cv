import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: () => import('../views/HomeView.vue') },
    { path: '/lobby/:code', component: () => import('../views/LobbyView.vue') },
    { path: '/game/:code',  component: () => import('../views/GameView.vue') },
  ],
})

export default router
