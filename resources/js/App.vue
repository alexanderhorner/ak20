<template>
    <div>
        <vueheader></vueheader>
        <router-view></router-view>
    </div>
</template>

<script>
import Header from './components/Header'

export default {
    name: 'app',
    components: {
        'vueheader': Header,
    }
}
</script>

<style lang="scss">
html, body {
    overflow-x: hidden;
    font-family: 'Nunito Sans', sans-serif;
    color: hsl(0, 0%, 15%);
    background: linear-gradient(to right, #a8ff78, #78ffd6);
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    text-align: center;
}
</style>