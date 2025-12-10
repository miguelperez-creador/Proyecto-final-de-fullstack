// main.js - jQuery helpers
$(document).ready(function(){
  // ejemplo: enviar comentario por AJAX
  $('#comment-ajax').on('click', function(e){
    e.preventDefault();
    var form = $('#comment-form');
    var action = "{{ url_for('comment_add_ajax', ticket_id=0) }}"; // no útil aquí, lo manejamos dinámicamente
    // construimos la URL real basándonos en la acción del form
    var url = form.attr('action').replace('/comments','/comments_ajax');
    var comment = form.find('textarea[name="comment"]').val();
    if(!comment.trim()){
      alert('Comentario vacío');
      return;
    }
    $.post(url, {comment: comment})
      .done(function(data){
        // prepend nuevo comentario
        var html = '<li class="list-group-item"><div class="d-flex justify-content-between"><strong>' + data.user_name + '</strong><small>' + data.created_at + '</small></div><p class="mb-0">' + data.comment + '</p></li>';
        $('#comments-list').append(html);
        form.find('textarea[name="comment"]').val('');
      })
      .fail(function(){
        alert('Error agregando comentario (AJAX).');
      });
  });
});
