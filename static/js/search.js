(function () {
    var removeHighlight = function () {
        $('span.highlight').contents().unwrap();
    };

    var wrapContent = function (index, $el, text) {
        var $highlight = $('<span class="highlight"/>')
            .text(text.substring(0, index));
      
        var normalText = document.createTextNode(text.substring(index, text.length));
     
        $el.html($highlight).append(normalText);
    };

    var highlightTextInTable = function ($tableElements, searchText) {
        // highlights if text found (during typing)
        var matched = false;
        //remove spans
        removeHighlight();

        $.each($tableElements, function (index, item) {
            var $el = $(item);
            if ($el.text().toLowerCase().search(searchText.toLowerCase()) != -1 && !matched) {
				//console.log("matched", $el, $el.html());
				wrapContent(searchText.length, $el, $el.html());
			
				if (searchText.toLowerCase() == $el.text().toLowerCase()) {
					// found the entry
					//console.log("matched");
					matched = true;
				}
			}
        });
    };

    $(function () {
        //load table into object
        var $tableRows = $('table tr');
        var $tableElements = $tableRows.children();
        $('#search').on('keyup', function (e) {
            var searchText = $(this).val();
            if (searchText.length == 0) {
                // catches false triggers with empty input (e.g. backspace delete or case lock switch would trigger the function)
                removeHighlight(); // remove last remaining highlight
                return;
            }
            //findTextInTable($tableElements, searchText);
            highlightTextInTable($tableElements, searchText);
        });
    });

})();



//alternative choice if you only want show result matches
// var $rows = $('#table tr.result');
// $('#search').keyup(function() {
    
//     var val = '^(?=.*\\b' + $.trim($(this).val()).split(/\s+/).join('\\b)(?=.*\\b') + ').*$',
//         reg = RegExp(val, 'i'),
//         text;
    
//     $rows.show().filter(function() {
//         text = $(this).text().replace(/\s+/g, ' ');
//         return !reg.test(text);
//     }).hide();


// });
