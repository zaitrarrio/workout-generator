$(window).load(function() {
  //Remove class if js enabled
  $('html').removeClass('no-js').addClass('js');

  /* Nav Menu */
  $('.has-flyout').hoverIntent(function() {
    $(this).find('.flyout').eq(0).fadeIn(500);
    //This positions sub menus to the left if they go off screen
    if ($(this).children('.flyout').length > 0) {
      var elm = $(this).children('.flyout');
      var off = elm.offset();
      var l = off.left;
      var w = elm.width();
      var docW = $(window).width();

      var isEntirelyVisible = (l + w <= docW);

      if (!isEntirelyVisible) {
        $('.flyout', this).addClass('edge');
      }
    }
  }, function() {
    $(this).find('.flyout').eq(0).fadeOut(500);
  });

  /* Responsive Nav Menu */
  selectnav('nav-bar');

  /* Flexslider */
  (function() {
    var caption = $('.flex-caption');
    var loader = $('.loader');

    $('.flexslider').flexslider({
      animation : "fade",
      controlNav : true,
      prevText : "",
      nextText : "",
      initDelay : 500,
      controlsContainer : ".flex-container",
      start : function() {
        loader.fadeOut();
        caption.delay(700).fadeIn(1000);
      },
      before : function() {
        caption.fadeOut('fast');
      },
      after : function() {
        caption.fadeIn(1000);
      }
    });
  })();

  /* Fancybox */
  $("a.fancybox").fancybox({
    'transitionIn'  : 'fade',
    'transitionOut' : 'fade',
    'speedIn'   : 600,
    'speedOut'    : 200,
    'overlayColor'  :   '#000',
    'padding'   :   0
  });
  //video
  $("a.fancy_youtube").click(function() {
    $.fancybox({
      'transitionIn'  : 'fade',
      'transitionOut' : 'fade',
      'autoScale'   : true,
      'speedIn'   : 800,
      'overlayColor'  : '#000',
      'title'     : this.title,
      'href'      : this.href.replace(/watch\?v=/g, "embed/"),
      'type'      : 'iframe'
    });
    return false;
  });
  $("a.fancy_vimeo").click(function() {
    $.fancybox({
      'transitionIn'  : 'fade',
      'transitionOut' : 'fade',
      'autoScale'   : true,
      'speedIn'   : 800,
      'overlayColor'  : '#000',
      'title'     : this.title,
      'href'      : this.href.replace(/vimeo.com/g,"player.vimeo.com/video"),
      'type'      : 'iframe'
    });
    return false;
  });

   /* Fitvids */
  $(".image-container").fitVids();

  /* Hover Effects */
  (function() {
    var img_cont = $('.image-container');
    var read_more = $('.read-more');
    var port_title = $('.port-title');
    var port_action = $('.port-action');

    img_cont.hover(function() {
      $(this).find(read_more).stop().animate({
        bottom : '0'
      });
      $(this).find(port_title).stop(true, true).fadeIn();
      $(this).find(port_action).stop(true, true).delay(300).animate({
        bottom : '0'
      });
    }, function() {
      $(this).find(read_more).stop(true, true).animate({
        bottom : '-60px'
      });
      $(this).find(port_action).stop(true, true).animate({
        bottom : '-100px'
      });
      $(this).find(port_title).delay(300).fadeOut();
    })
  })();

  /* Contact form */
  $('#send').click(function(){
    $('.error').fadeOut('slow');

    var error = false;

    var name = $('input#name').val();
    if(name == "" || name == " ") {
      $('#err-name').fadeIn('slow');
      error = true;
    }

    var email_compare = /^([A-Za-z0-9_.-]+)@([dA-Za-z.-]+).([A-Za-z.]{2,6})$/;
    var email = $('input#email').val();
    if (email == "" || email == " ") {
      $('#err-email').fadeIn('slow');
      error = true;
    } else if (!email_compare.test(email)) {
      $('#err-emailvld').fadeIn('slow');
      error = true;
    }

    if(error == true) {
      return false;
    }

    var data_string = $('#ajax-form').serialize();

    $.ajax({
      type: "POST",
      url: $('#ajax-form').attr('action'),
      data: data_string,
      timeout: 6000,
      error: function(request,error) {
        if (error == "timeout") {
          $('#err-timedout').fadeIn('slow');
        }
        else {
          $('#error').slideDown('slow');
          $("#error").html('Error! Please try again');
        }
      },
      success: function() {
        $('#ajax-form').slideUp('slow');
        $('#email-success').fadeIn('slow');
      }
    });

    return false;
  });

  /* UI Elements */
  //accordion
  $(".accordion").accordion({
    heightStyle : "content"
  });

  //tabs
  $(".tabs").tabs().addClass("ui-tabs-vertical ui-helper-clearfix");

  //toggle
  $('#toggle').find('.toggle').click(function() {
    var header = $(this).find('h5');
    var text = $(this).find('.content');

    if (text.is(':hidden')) {
      header.addClass('active');
      text.slideDown('fast');
    } else {
      header.removeClass('active');
      text.slideUp('fast');
    }
  });

  //tooltips
  $(".tool").tipTip({
    defaultPosition: 'top',
    delay: 0
  });

	/* Isotope */
	var container = $('.portfolio');
	var $optionSets = $('.filter'), $optionLinks = $optionSets.find('a');

	container.isotope({
		itemSelector : '.column, .columns',
		animationEngine : 'best-available',
		animationOptions : {
			duration : 500
		}
	});

	$(window).smartresize(function() {
		container.isotope({
			masonry : {
				columnWidth : container.width() / 12
			}
		});
	});

	$('a', $optionSets).click(function() {
		var selector = $(this).attr('data-filter');
		container.isotope({
			filter : selector
		});
		return false;
	});

	$optionLinks.click(function() {
		var $this = $(this);
		if ($this.parents('li').hasClass('selected')) {
			return false;
		}

		var $optionSet = $this.parents('.option-set');
		$optionSet.find('.selected').removeClass('selected');
		$this.parents('li').addClass('selected');

		return false;
	});

  /* Flickr feed */
  $('.flickr').jflickrfeed({
    limit: 4,
    qstrings: {
      id: '25197839@N00'
    },
    itemTemplate:
    '<li>' +
      '<a href="{{link}}" title="{{title}}" target="_blank"><img src="{{image_q}}" alt="{{title}}" /></a>' +
    '</li>'
  });

  /* Google Maps */
  $("#gmap").gmap3({
    map:{
      address:"Miami Beach, FL",
      options:{
        zoom:12,
        styles: [{
          "stylers": [
            { "saturation": -50 }
          ]
        }]
      }
    }
  });

});
