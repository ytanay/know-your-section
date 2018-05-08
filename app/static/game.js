var socket = io.connect('http://' + document.domain + ':' + location.port + '/game');

socket.on('connect', function(data){
    console.log('Connected!');

})

socket.on('start-game', function(data){
    $('.mCSB_container').html('');
    $('#game-end-message').hide();
    $('#vote').hide();

    $('#player-name').text(data['player-name']);
    $('#human-name').text(data['human-name']);

    $('#option-real').text(data['human-name'] + ' האמיתי')
    $('#option-fake').text('מישהו אחר')

    var secondary = data['computer-name'] ? '(אבל בעצם ' + data['computer-name'] + ')' : ''

     $('#chat-input').toggle(data['is-player'] || data['is-computer']);

    $('#loading').hide()

    $('#game-status').html(`${data['player-name']} נגד ${data['human-name']} ${secondary}`)

    $("#countdown")
                  .countdown(Date.now() + data.duration * 1000, function(event) {
                    $(this).text(
                      event.strftime('%M:%S')
                    );
                  });
});


socket.on('message', function(message){
    console.log(message);
    var ours = message['team'] == MY_TEAM;

    $('<div class="message ' + (ours ? 'message-personal' : 'new') + '">' + (ours ? '' : '<figure class="avatar"><img src="/static/user-icon.png" /></figure>') + message.contents + '</div>').appendTo($('.mCSB_container')).addClass('new');

    //setDate();
    updateScrollbar();
});


socket.on('end-game', function(message){
    $('#chat-input').hide();
    $('#game-end-message').show();
    $("#countdown").countdown('stop');

    if(message['voting-team'] === MY_TEAM)
        $('#vote').show();

})


$('.vote-button').click(function(e){
    e.preventDefault();
    socket.emit('vote', this.id);
    $('#vote').fadeOut();
})


$(function(){
    $('#chat-form').submit(function(e){
        console.log('Test')
        e.preventDefault();
        e.stopPropagation();

        var message = $('#chat-input').val();

        if(!message)
            return false

        socket.emit('message', message);
        $('#chat-input').val('');

        return false;
    });
});







///

var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function() {
  $messages.mCustomScrollbar();

});


function updateScrollbar() {
  $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate(){
  d = new Date()
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    $('<div class="checkmark-sent-delivered">&check;</div>').appendTo($('.message:last'));
    $('<div class="checkmark-read">&check;</div>').appendTo($('.message:last'));
  }
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  socket.emit('message', msg);
  //$('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  //setDate();
  $('.message-input').val(null);
  updateScrollbar();
}

$('#message-submit').click(function() {
  insertMessage();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
})

