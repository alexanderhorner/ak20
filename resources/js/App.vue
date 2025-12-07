<template>
    <div>
        <v-header></v-header>
        <transition name="page">
            <router-view></router-view>
        </transition>
        <div class="legal">
            <span>Copyright © 2020 Alexander Horner. All rights reserved.</span>
        </div>
    </div>
</template>

<script>
import Header from "./components/Header.vue";

export default {
    name: "app",
    components: {
        "v-header": Header,
    },
};
</script>

<style lang="scss" scoped>
.page-enter-active {
    animation: page-enter 0.4s;
}
.page-leave-active {
    animation: page-leave 0.4s;
}
@keyframes page-enter {
    0% {
        opacity: 0;
    }
    40% {
        opacity: 0;
    }
    100% {
        opacity: 1;
    }
}

@keyframes page-leave {
    0% {
        opacity: 1;
    }
    60% {
        opacity: 0;
    }
    100% {
        opacity: 0;
    }
}
</style>
