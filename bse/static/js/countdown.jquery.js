(function($) {
	$.fn.countdown = function(options) {
		var settings = {'date': null};
		if (options) {
			$.extend(settings, options);
		}
		this_sel = $(this);
		function count_exec() {
			eventDate = 	Date.parse(settings['date']) / 1000;
			currentDate = 	Math.floor($.now() / 1000);
			seconds = 		eventDate - currentDate;
			if(seconds == 0){
				location.href = '/token';
			}
			days = 			Math.floor(seconds / (60 * 60 * 24));
			seconds -=		days * 60 * 60 * 24;
			hours =			Math.floor(seconds / (60 * 60));
			seconds -=		hours * 60 * 60;
			minutes =		Math.floor(seconds / 60);
			seconds -=		minutes * 60;

			days = (String(days).length < 2) ? '0' + days : days;
			hours = (String(hours).length !== 2) ? '0' + hours : hours;
			minutes = (String(minutes).length !== 2) ? '0' + minutes : minutes;
			seconds = (String(seconds).length !== 2) ? '0' + seconds : seconds;

			this_sel.find('.days').text(days);
			this_sel.find('.hours').text(hours);
			this_sel.find('.minutes').text(minutes);
			this_sel.find('.seconds').text(seconds);
		}
		count_exec();
		interval = setInterval(count_exec, 1000);
	}
	$.fn.adddown = function(options) {
		var settings = {'date': null};
		if (options) {
			$.extend(settings, options);
		}
		this_sel = $(this);
		function count_exec2() {
			eventDate = 	Date.parse(settings['date']) / 1000;
			currentDate = 	Math.floor($.now() / 1000);
			seconds = 		currentDate - eventDate;
			days = 			Math.floor(seconds / (60 * 60 * 24));
			seconds -=		days * 60 * 60 * 24;
			hours =			Math.floor(seconds / (60 * 60));
			seconds -=		hours * 60 * 60;
			minutes =		Math.floor(seconds / 60);
			seconds -=		minutes * 60;

			days = (String(days).length < 2) ? '0' + days : days;
			hours = (String(hours).length !== 2) ? '0' + hours : hours;
			minutes = (String(minutes).length !== 2) ? '0' + minutes : minutes;
			seconds = (String(seconds).length !== 2) ? '0' + seconds : seconds;

			this_sel.find('.days').text(days);
			this_sel.find('.hours').text(hours);
			this_sel.find('.minutes').text(minutes);
			this_sel.find('.seconds').text(seconds);
		}
		count_exec2();
		interval = setInterval(count_exec2, 1000);
	}
	$.fn.endtime = function(options) {
		var settings = {'date': null};
		if (options) {
			$.extend(settings, options);
		}
		this_sel = $(this);
		function count_exec3() {
			eventDate = 	Date.parse(settings['date']) / 1000;
			currentDate = 	Math.floor($.now() / 1000);
			seconds = 		currentDate - eventDate;
			days = 			Math.floor(seconds / (60 * 60 * 24));
			seconds -=		days * 60 * 60 * 24;
			hours =			Math.floor(seconds / (60 * 60));
			seconds -=		hours * 60 * 60;
			minutes =		Math.floor(seconds / 60);
			seconds -=		minutes * 60;

			days = (String(days).length < 2) ? '0' + days : days;
			hours = (String(hours).length !== 2) ? '0' + hours : hours;
			minutes = (String(minutes).length !== 2) ? '0' + minutes : minutes;
			seconds = (String(seconds).length !== 2) ? '0' + seconds : seconds;

			this_sel.find('.days').text(days);
			this_sel.find('.hours').text(hours);
			this_sel.find('.minutes').text(minutes);
			this_sel.find('.seconds').text(seconds);
		}
		count_exec3();
	}
})(jQuery);