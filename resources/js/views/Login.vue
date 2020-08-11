<template>
    <div>
        <div class="container">
            <span class="question">Was ist Herr Schönberger's Lieblingswort?</span>
            <form class="login-form" method="post">
                <input type="hidden" name="_token" :value="csrf">

                <div class="sqr-shadow-container">
                    <input autocomplete="current-password" class="textfield sqr-shadow-element" type="password" name="password" placeholder="Passwort...">
                    <div class="sqr-shadow"></div>
                </div>

                <div class="sqr-shadow-container2">
                    <input class="submit sqr-shadow-element" type="submit" value="Entsperren">
                    <div class="sqr-shadow"></div>
                </div>
                
            </form>
        </div>
    </div>
</template>

<script>
export default {
    data: () => ({
        csrf: document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
    })
}



const axios = require('axios').default;
const bcrypt = require('bcryptjs');

class Login {
    constructor() {
        this.textfield = document.querySelector("form .textfield");
        this.form = document.querySelector("form.login-form")

        this.formListener();
    }

    formListener() {
        var self = this;
        this.form.addEventListener("submit", function() {
            event.preventDefault();
            self.check();
        });
    }

    input() {
        return this.textfield.value;
    }

    getCsrfToken() {
        return document.querySelector('form input[name=_token]').getAttribute('value')
    }

    check() {
        var self = this;
        var csrfToken = self.getCsrfToken();
        var input = self.input()
        
        // check password    
        axios.post('/api/v1/login', {
            password: input
        })
        .then(function (response) {
            if (response.data.data.success) {
                routerPush('/')
            } else {
                // trigger error animation
                self.textfield.parentNode.classList.add("error"); // attach error class to trigger css animation
                window.setTimeout(function() {
                    self.textfield.parentNode.classList.remove("error"); // remove it so it can be triggered again
                }, 500);

                self.textfield.value = ''; // clear textfield
            }
        })
        .catch(function (error) {
            console.log(error);
        });
    }
}

window.addEventListener('load', function () {
  const login = new Login();
  window.login = login;
})




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
    flex-direction: column;

    .question {
        font-size: 2rem;
        margin-bottom: 20px;
        font-weight: lighter;
    }

    form {
        display: flex;
        flex-direction: column;
        align-items: center;

        .textfield {
            width: 100%;
            padding: 0 0.9rem;
            font-weight: lighter;
            border-radius: unset;
            -webkit-appearance: none;
        }

        .submit {
            width: 100%;
            height: 100%;
            background-color: #FFF;
            color: #000;
            border: 2px solid black;
            font-weight: lighter;
            font-size: 24px;
            outline: none;
            cursor: pointer;
            border-radius: unset;
            -webkit-appearance: none;
        }
    }
}

.sqr-shadow-container {
    display: inline-block;
    position: relative;
    transform-style: preserve-3d;
    width: 90vw;
    max-width: 350px;

    .sqr-shadow-element {
        transition: transform 0.15s;
        outline: none !important;
        background-color: #FFF;
        border: 2px solid #000;
        height: 62px;
        font-size: 29px;
        font-family: 'Nunito Sans', sans-serif;

        &:focus {
            transform: translate(-5px, 5px);
        }
    }

    .sqr-shadow {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background-color: #000;
        transform: translate3d(-5px, 5px, -1px);
    }

    &.error {
        animation-name: shake;
        animation-duration: 0.4s;
        animation-timing-function: ease-in-out;
        animation-direction: normal;
    }
}

@keyframes shake {
    0% { transform: translateX(0) }
    12.5% { transform: translateX(5px) }
    37.5% { transform: translateX(-5px) }
    62.5% { transform: translateX(5px) }
    87.5% { transform: translateX(-5px) }
    100% { transform: translateX(0) }
}

.sqr-shadow-container2 {
    display: inline-block;
    position: relative;
    transform-style: preserve-3d;
    height: 50px;
    margin-top: 20px;
    width: 180px;

    .sqr-shadow-element {
        transition: transform 0.15s;
        outline: none !important;
        background-color: #FFF;
        border: 2px solid #000;
        height: 62px;
        font-size: 29px;
        font-family: 'Nunito Sans', sans-serif;

        &:focus {
            transform: translate(-5px, 5px);
        }
    }

    .sqr-shadow {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background-color: #000;
        transform: translate3d(-5px, 5px, -1px);
    }
}

.sqr-shadow-container2 .sqr-shadow-element:hover {
    transform: translate(-5px, 5px);
}

</style>