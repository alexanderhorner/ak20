<template>
    <div class="header">
        <span class="logo-txt">10a</span>
        <div class="vertical-line"></div>
        <span class="logo-txt">AK20</span>
    </div>
</template>

<script>
export default {
    name: 'vueheader'
}
</script>

<style lang="scss" scoped>
.header {
    position: absolute;
    left: 0;
    top: -1px;
    right: 0;
    padding-top: 1px;
    height: 80px;
    display: flex;
    align-items: center;
    color: hsl(0, 0%, 100%);
    background-color: hsl(0, 0%, 0%);
    z-index: 1000;


    .logo-txt {
        font-family: 'Montserrat', sans-serif;
        font-size: 25px;
        font-weight: lighter;

        &:first-of-type {
            margin-left: 15px;
            font-weight: bold;
        }
    }

    .vertical-line {
        margin: 0 10px;
        background-color: hsl(0, 0%, 100%);
        height: 40px;
        width: 3px;
    } 

}
</style>