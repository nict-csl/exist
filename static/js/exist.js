$(function(){
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

$(function(){
    $('[data-toggle="tab"]').on('show.bs.tab', function(e){
        switch((e.target).id){
            case 'virustotal-tab':
                $.ajax({
                    url: location.href + 'update_vt',
                    method: "GET",
                })
                .then(
                    data => $('#virustotal').html(data),
                    error => $('#virustotal').html('<div class="alert alert-danger" role="alert">Failed to access VirusTotal</div>')
                );
                break;
            case 'threatminer-tab':
                $.ajax({
                    url: location.href + 'update_tm',
                    method: "GET"
                })
                .then(
                    data => $('#threatminer').html(data),
                    error => $('#threatminer').html('<div class="alert alert-danger" role="alert">Failed to access ThreatMiner</div>')
                );
                break;
        }
    });
});
