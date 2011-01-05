$(document).ready(function() {
  $('input').click(function() {
    if ($(this).attr('checked') === true) {
      if ($(this).attr('title')) {
        dependencies = $(this).attr('title').split(',');
        version = $($(this).parents('.version')[0]).attr('id');
        for (i in dependencies) {
          $('#' + version + " input[value='" + dependencies[i] + "']").attr('checked', true);
        }
      }
    }
  });

  $('#buttonSaveConfiguration, #buttonGenerate').click(function(e) {
    $('#onPostBack').val('config');
  });

  $('#buttonLoadConfig').click(function(e) {
    e.preventDefault();
    if ($('#config').val() !== '') {
      // TODO: replace with simple object-creation
      var configs = '{ \"items\" : ' + $('#config').val().replace(/u'/gi, "'").replace(/'/gi, '\"') + '}';
      var obj = $.parseJSON(configs);
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
