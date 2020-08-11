require('./bootstrap')

require('./modernizr.min.js')

import Vue from 'vue'
import VueRouter from 'vue-router'

import App from './App.vue'

import Home from './views/Home.vue'

Vue.use(VueRouter)

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('./views/Login.vue')
    },
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/*',
        name: '404',
        component: () => import('./views/Error404.vue')
    }
] 

const router = new VueRouter({
    routes,
    mode: 'history'
})

const app = new Vue({
    router,
    el: '#app',
    components: {
        App
    }
})

window.routerPush = function(x) {
    router.push(x)
}
