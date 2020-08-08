<template>
    <div class="container">
        <span class="error-title">Error 404</span>
        <span class="error-description">Diese Seite existiert nicht</span>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
    .container {
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