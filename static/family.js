"use strict";

function verifylogin(results) {
    if(results == '') {
        window.location.href = '/homepage';
    }
    else {
        $("#accountValidation").html(results);
    }
    
}

function validatelogin(evt) {
    event.preventDefault();
    let formInputs = {
        "email": $("#emailInput").val(),
        "password": $("#pwdInput").val()
    };

    $.post('/validatelogin', formInputs, verifylogin);
}

$('#login-form').submit(validatelogin);
