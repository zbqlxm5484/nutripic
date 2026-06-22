import { createRouter, createWebHistory } from 'vue-router'
import { homePage, notFoundPage } from '../pages'
import {
  adminRoutes,
  authRoutes,
  communityRoutes,
  mypageRoutes,
  reportRoutes,
  surveyRoutes,
} from '../domains/routes'

const routes = [
  { path: '/', component: homePage },
  ...authRoutes,
  ...surveyRoutes,
  ...reportRoutes,
  ...mypageRoutes,
  ...communityRoutes,
  ...adminRoutes,
  { path: '/:pathMatch(.*)*', component: notFoundPage },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
