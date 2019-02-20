$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(function(){
    $('more').each(function(){
        var $ele = $(this);
        var $division = 5;
        $ele.find('.li').eq($division-1).after('<button class="morelink btn-sm btn-outline-info my-2">read more</button>');
        $ele.find('.li,.morelink').hide();
        for(i=0;i<$division;i++){
            $ele.find('.li').eq(i).show();
        }
        $ele.find('.morelink').show();

        $ele.find('.morelink').click(function(){
            $ele.find('.li').fadeIn();
            $ele.find('.morelink').hide();
        });
    });
});
