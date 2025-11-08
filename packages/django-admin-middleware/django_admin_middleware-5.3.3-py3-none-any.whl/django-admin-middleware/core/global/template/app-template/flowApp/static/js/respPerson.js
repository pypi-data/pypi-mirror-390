const resp_form = document.getElementById('response-form')


resp_form.addEventListener('submit', (event)=> {
    event.preventDefault();
    formData = new FormData(resp_form);

    data = {
        order_id: formData.get('order-name'),
        resp_person: formData.get('responsible-name'),
    }

    fetch('/response-person/', {
        method: 'POST',
        body: formData
    })
    .then(answer => {return answer.json()})
    .then(data => {
        if (data.success) {
            location.replace('/success/send/')
        } else {
            console.log(data.errors)
        }
    })
})
