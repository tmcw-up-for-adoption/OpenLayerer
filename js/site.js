$(document).ready(function() {
  $('input').click(function() {
    var dependencies, version;
    if ($(this).attr('checked') === true && $(this).attr('title')) {
      dependencies = $(this).attr('title').split(',');
      version = $($(this).parents('.version')[0]).attr('id');
      for (i = 0, l = dependencies.length; i < l; i++) {
        $('#' + version + " input[value='" + dependencies[i] + "']").attr('checked', true);
      }
    }
  });

  $('#buttonSaveConfiguration, #buttonGenerate').click(function(e) {
    $('#onPostBack').val('config');
  });

  $('#buttonLoadConfig').click(function(e) {
    var obj;
    e.preventDefault();
    if ($('#config').val() !== '') {
      obj = $.parseJSON($('#config').val());
      $(':checkbox').attr('checked', null);
      $.each(obj.items, function(i,item) {
          $(':checkbox[value='+ item + ']').attr('checked', 'checked');
      });
    }
  });

  $('#buttonSelectAll').click(function(e) {
     e.preventDefault();
     $(':checkbox').attr('checked', 'checked');
  });

  $('#buttonSelectNone').click(function(e) {
    e.preventDefault();
    $(':checkbox').attr('checked', null);
  });
});
