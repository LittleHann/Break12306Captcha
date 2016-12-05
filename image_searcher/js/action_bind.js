$(document).ready(function() {
  $("#view-gp-1").click(function() { 
        $(".im-gp-1 img:first").click();
  });

  $("#view-gp-2").click(function() { 
        $(".im-gp-2 img:first").click();
  });

  function query_and_show(phash, max_query, container) {
    $.get("/getImage", 
        {rgb_hash: $(phash).val(), 
         max_query: $(max_query).val()}, 
         function(data) {
            data = JSON.parse(data);
            $(container).empty();
            $.each(data, function (index) {
                $(container).append('<img class="img-thumbnail" src="/static/' + data[index] + '" alt="..." />');
            });
            $(".im-gp-1").viewer();
            $(".im-gp-2").viewer();
         }
    );
  }

  $("#search-1").click(function() {
        $.get("/getImage", {rgb_hash: $("#phash1").val(), max_query: $("#max-image-query").val()});
        query_and_show($("#phash1").val(),
                       $("#max-image-query").val(),
                       "#thumbnail1");
  });
  $("#search-2").click(function() {
        $.get("/getImage", {rgb_hash: $("#phash2").val(), max_query: $("#max-image-query").val()});
        query_and_show($("#phash2").val(),
                       $("#max-image-query").val(),
                       "#thumbnail2");
  });
});
