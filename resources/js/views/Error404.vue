<template>
    <div>
        <div class="back">
            <router-link class="link" :to="{name: 'Home'}">&lt; Zurück</router-link>
        </div>
        <div class="container">
            <span class="error-title">Error 404</span>
            <span class="error-description">Diese Seite existiert nicht</span>
        </div>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
.back {
    z-index: 2;
    position: absolute;
    top: 90px;
    left: 10px;

    .link {
        color: #000;
        text-decoration: none;
        display: block;
        padding: 0.2em 0.6em;
        box-shadow: -1px 1px 7px 0 hsla(0, 0%, 0%, 0.15);
        background-color: #FFF;
        border-radius: 10px;
    }
}

.container {
    z-index: 1;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: lighter;
    flex-direction: column;

    .error-title {
        font-size: 2.5rem;
    }

    .error-description {
        color: hsla(99, 20%, 25%, 0.8);
    }
}
</style>