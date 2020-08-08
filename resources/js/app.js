require('./bootstrap');

import Vue from 'vue'
import VueRouter from 'vue-router'

import App from './App.vue'

const Login = () => import('./views/Login.vue')
import Home from './views/Home.vue'
const Error404 = () => import('./views/Error404.vue')

Vue.use(VueRouter)

const routes = [
    { path: '/login', component: Login },
    { path: '/', component: Home },
    { path: '/*', component: Error404 }
] 

const router = new VueRouter({
    routes,
    mode: 'history'
})

const app = new Vue({
    router,
    render: h => h(App)
}).$mount('#app')
