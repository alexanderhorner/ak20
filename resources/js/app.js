import "./bootstrap";
import "./modernizr.min.js";
import "../sass/app.scss";
import "../css/reset.css";

import Vue from "vue";
import VueRouter from "vue-router";

import App from "./App.vue";
import Home from "./views/Home.vue";

Vue.use(VueRouter);

const routes = [
    {
        path: "/login",
        name: "Login",
        component: () => import("./views/Login.vue"),
    },
    {
        path: "/",
        name: "Home",
        component: Home,
    },
    {
        path: "/*",
        name: "404",
        component: () => import("./views/Error404.vue"),
    },
];

const router = new VueRouter({
    routes,
    mode: "history",
});

new Vue({
    router,
    render: (h) => h(App),
}).$mount("#app");

window.routerPush = function (route) {
    router.push(route);
};
