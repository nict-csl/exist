$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(function(){
    $('more').each(function(){
        var $ele = $(this);
        var $division = 5;
        $ele.find('.li').eq($division-1).after('<button class="morelink btn-sm btn-outline-info my-2">read more</button>');
        $ele.find('.li,.morelink').hide();
        for(j=0;j<$division;j++){
            $ele.find('.li').eq(j).show();
        }
        $ele.find('.morelink').show();

        $ele.find('.morelink').click(function(){
            $ele.find('.li').fadeIn();
            $ele.find('.morelink').hide();
        });
    });
});
