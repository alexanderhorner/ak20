<template>
    <div>
        <div class="content">
            <span class="title">Abschlusszeitung 2020</span>

            <span class="description">Abschlusszeitung2020.pdf (20MB)</span>

            <div class="btn-group">
                <a class="shadow-btn" href="#"><span>Anschauen</span></a>
                <a class="shadow-btn" href="#" download><span>Download</span></a>
            </div>
        </div>
        <div class="legal">
            <span>Copyright © 2020 Alexander Horner. All rights reserved.</span>
        </div>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
.content {
    margin: auto 20px;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    font-weight: lighter;
    margin-top: 30px;
    margin-bottom: 14px;

    @media (max-height: 444px) {
        margin-top: 80px;
    }

    .title {
        font-family: 'Montserrat', sans-serif;
        font-size: 2.6rem;
        font-weight: bold;
        margin-bottom: 3px;

        @media (max-width: 444px) {
            font-size: 9.5vw;
        }
    } 

    .description {
        line-height: 1.6;
        text-align: center;
        max-width: 500px;
        color: hsla(99, 20%, 35%, 0.8);
        margin-bottom: 25px;
        font-weight: lighter;
    }

    .btn-group {
        display: flex;
        justify-content: center;
        align-items: center;

        @media (max-width: 512px) {
            margin-top: 20px;
            flex-direction: column;
        }

        .shadow-btn {
            font-size: 29px;
            background-color: white;
            position: relative;
            color: hsl(0, 0%, 0%);
            text-decoration: none;
            display: block;
            border: 2px solid hsl(0, 0%, 0%);
            transition: transform 0.15s;
            transform-style: preserve-3d;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 200px;
            height: 62px;

            @media (max-width: 512px) {
                width: 300px;
                max-width: 80%;
            }

            &:first-of-type {
                margin-right: 40px;

                @media (max-width: 512px) {
                    margin-right: unset;
                    margin-bottom: 20px;
                }
            }

            > span {
                -webkit-user-select: none; /* Safari */        
                -moz-user-select: none; /* Firefox */
                -ms-user-select: none; /* IE10+/Edge */
                user-select: none; /* Standard */
            }

            &::before {
                content: "";
                position: absolute;
                top: -2px;
                right: -2px;
                bottom: -2px;
                left: -2px;
                background-color: hsl(0, 0%, 0%);
                /* background: linear-gradient(to right, #12c2e9, #c471ed, #f64f59);; */
                /* background-color: hsl(0, 0%, 100%);
                border: 2px solid hsl(0, 0%, 0%); */
                transition: transform 0.15s;
                transform: translate(-5px, 5px) translateZ(-1px);
            }

            &:hover::before {
                transform: translate(0, 0) translateZ(-1px);
            }

            &:hover {
                transform: translate(-5px, 5px);
            }

            &:active {
                transform: translate(-5px, 5px) scale(0.98);
            }
        }
    }
}

.legal {
    position: absolute;
    left: 0;
    bottom: 0;
    right: 0;
    padding-bottom: 2px;
    font-size: 8px;
    color: hsla(99, 20%, 70%, 0.7);
}
</style>