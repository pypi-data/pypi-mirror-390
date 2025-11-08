const input_message = document.querySelector('#chat-ai-input');
const message_wrapper = document.querySelector('.chat-ai-content');
const send_message_btn = document.querySelector('#send-message');
const start_chat_message = document.querySelector('.start-message')

const word_lib = {
    'привет': ['привет', 'хай', 'Здравствуйте', 'Приветки', 'Здоров', 'Здорова', 'прив'],
    'помощь': ['что умеешь', 'помоги','помощь','хелп','помочь','help','sos','помогите','помогу'],
    'заявка': ['заявка', 'зоявка', 'заявки', 'создать', 'заявку', 'новая заявка', 'новую заявку', 'создать заявку'],
    'статус': ['статус', 'посмотреть', 'все заявки', 'узнать статус', 'статусы', 'как посмотреть', 'где посмотреть', 'статус заявки'],
    'благодарность': ['спасибо', 'большое спасибо', 'спс', 'благодарю', 'отлично', 'круто', 'thanks']
}

const answer = {
    'привет': 'Привет, чем могу помочь? <br> Если хотите узнать, что могу, напишите: "помощь"',
    'помощь': 'Я могу: подсказать как сформировать заявку и как отслеживать ее статус. <br> Для этого напиши: "заявка" или "статус"',
    'заявка': 'Для того, чтобы сформировать заявку, перейдите в меню "Создать заявку", заполните все поля и нажмите кнопку "Сохранить".',
    'статус': 'Для того, чтобы посмотреть статус своей заявки, перейдите в меню "Мои заявки". <br> Там будут отображаться все ваши заявки.<br>Как только менеджер рассмотрит вашу заявку, у нее изменится статус на "В работе"',
    'благодарность': 'Спасибо, что воспользовались моими услугами! Возвращайтесь еще, я всегда готов помочь!'
}

let old_message

document.addEventListener('keypress', (event)=> {
    if (event.key == 'Enter') {
        console.log(event)
        startMessage();
    }
})


send_message_btn.addEventListener('click', (event)=> {
    startMessage();
})

function startMessage() {
    if (input_message.value || input_message.value != '') {
        old_message = input_message.value
        let message = createMessage(input_message.value, 'user')
        start_chat_message.classList.add('dissable-tapping');
        addTappingMessage();
        setTimeout(checkWordAI, 2000);
        sendMessage(message);
    } else {
        alert('Введите, пожалуйста, сообщение')
    }
}

function sendMessage(message) {
    message_wrapper.insertAdjacentElement('beforeend', message);
    input_message.value = '';
    message_wrapper.scrollTo({
        top: message_wrapper.scrollHeight,
        behavior: 'smooth'
    });
}

function createMessage(data, type) {
    const new_div = document.createElement('div');
    new_div.classList.add('chat-ai-message-wrapper');
    if (type == 'user') {
        user_first_name = input_message.dataset.username
        user_second_name = input_message.dataset.usersoname
        user_name = user_second_name + ' ' + user_first_name[0].toUpperCase() + '.'
        console.log(user_name)
        new_div.id = 'message-user';
        new_div.innerHTML = `
            <p class="message-author">${user_name}: </p>
            <p class="message_content">
                ${data}
            </p>
    `
    } else {
        new_div.id = 'message-ai';
        new_div.innerHTML = `
            <p class="message-author">AI: </p>
            <p class="message_content">
                ${data}
            </p>
    `
    }
    return new_div
}

function addTappingMessage(){
    tapp_div = document.createElement('div');
    tapp_div.classList.add('tapping-message');
    tapp_div.id = 'message-ai';
    tapp_div.innerHTML = 'AI набирает сообщение...';
    message_wrapper.insertAdjacentElement('beforeend', tapp_div);
}

function checkWordAI() {
    flag = false
    for (const key in word_lib) {
        if (!Object.hasOwn(word_lib, key)) continue;
        const element = word_lib[key];
        for (const word of element) {

            if (old_message.toLowerCase().includes(word.toLowerCase())) {
                message = createMessage(answer[key], 'ai');
                document.querySelector('.tapping-message').remove();
                sendMessage(message);
                return;
            }
        } 
    }
    if (!flag) {
        message = createMessage('Извините, я Вас не понял, обратитесь к администратору', 'ai');
        document.querySelector('.tapping-message').remove();
        sendMessage(message);   
    }
   
    
}
