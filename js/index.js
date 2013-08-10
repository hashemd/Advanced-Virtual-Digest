$('#digest_name').magicSuggest({
  			allowFreeEntries: true,
  			width: 590,
  			hideTrigger: true,
  			useTabKey: true,
  			maxSelection: 1,
  			emptyText: 'Name your sample..',
  			emptyTextCls: 'darkText',
  			maxDropHeight: 0,
});

$('#vec_name').magicSuggest({
            allowFreeEntries: false,
            width: 590,
            hideTrigger: true,
            useTabKey: true,
            maxSelection: 1,
            emptyText: 'Enter vector name..',
            emptyTextCls: 'darkText',
            maxDropHeight: 140,
            data: '/json/vectors.html',
});

$('#rest_sites').magicSuggest({
            allowFreeEntries: false,
            width: 590,
            hideTrigger: true,
            useTabKey: true,
            maxSelection: 2,
            emptyText: 'Enter sites on vector surrounding insert..',
            emptyTextCls: 'darkText',
            maxDropHeight: 140,
            data: '/json/sites.html',
});

$('#options').magicSuggest({
             allowFreeEntries: false,
             width: 590,
             hideTrigger: false,
             maxSelection: 1,
             expandOnFocus: true,
             emptyText: 'Choose from the following options..',
             emptyTextCls: 'darkText',
             maxDropHeight: 120,
             data: 'Linearize Sequence,Custom Digest,Remove Insert,Map Sequence',
});

$('#shape').magicSuggest({
			allowFreeEntries: false,
            width: 590,
            hideTrigger: false,
            maxSelection: 1,
            emptyText: 'Is sequence circular or linear..',
            emptyTextCls: 'darkText',
            maxDropHeight: 70,
            data: 'Circular,Linear',
});

$('#sequence').magicSuggest({
			allowFreeEntries: true,
            width: 590,
            hideTrigger: true,
            maxSelection: 1,
            emptyText: 'Enter DNA sequence or saved sequence name..',
            emptyTextCls: 'darkText',
            maxDropHeight: 0,
});

$('#enzymes').magicSuggest({
			allowFreeEntries: false,
            width: 590,
            hideTrigger: true,
            maxSelection: 10,
            emptyText: 'Enzymes for custom digest..',
            emptyTextCls: 'darkText',
            maxDropHeight: 70,
            data: '/json/objects.html',
});


$(document).ready(function() {

  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });

});