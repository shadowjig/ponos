var myTimer;
var refresh_allowed = 1;

$(function() {
  window.playing = 0;
});

$( window ).load(function() {
  console.log( "ready!" );
  $( ".hide_me" ).hide();
  
  userAgent = navigator.userAgent.toLowerCase();
  if( userAgent.match( /Android/i )) {
    //alert("It's Android!!");
	$(".android_only").show();
  } else {
	//alert("It's NOT Android!!");
  }
  
  if ($(".play_state").text() == 'playing') {
    progress_timer();
  }
});

function progress_timer() {
  current = parseInt($( ".progress-bar" ).attr('current_secs')) + 2;
  duration = parseInt($( ".progress-bar" ).attr('duration_secs'));
  //alert(current);
  //alert(duration);
	
  myTimer = setInterval( function(){
    if ((current > duration) && (refresh_allowed == 1)) {
	  clearInterval(myTimer);
	  refresh_allowed = 0;
	  window.location.reload(true);
	}
	
	if (duration > 0) {
	  percent = parseInt(100 * (current/duration));
	}
	
	hours = parseInt( current / 3600 ) % 24;
	minutes = parseInt( current / 60 ) % 60;
	seconds = current % 60;
		  
	if (hours > 0) {
	  result = hours + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds  < 10 ? "0" + seconds : seconds);
	} else {
	  result = minutes + ":" + (seconds  < 10 ? "0" + seconds : seconds);
	}
	
	document.getElementById("track_pos1").innerHTML = result;
	document.getElementById("track_pos2").innerHTML = result;
	document.getElementById("percentage").innerHTML = percent;
	$('.progress-bar').css('width', percent+'%').attr('aria-valuenow', percent);  
	current = current + 1;
  }, 1000);
}

$( ".setZone" ).click(function() {
  var zone_coordinator = $(this).attr('zone_coord');
  var short_name = $(this).attr('zone_short_name');
  var post_url_setzone = $(this).attr('post_url_setzone');

  var data = {
    'selected_zone': zone_coordinator,
	'short_name': short_name
  };

  $.ajax({
    type: 'POST',
    url: post_url_setzone,
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		$(".selected_zone").text( data[0]["short_name"] );
		window.location.reload(true);
	}
  });
  
  $('#myModal').modal('hide');
});

$( ".fetch_title_button" ).click(function() {
  var post_url = $(this).attr('post_url');
  var url_to_fetch = $(".inputURL").val();
  var data = { 'url': url_to_fetch };
  //alert(url);
  
  $.ajax({
    type: 'POST',
    url: post_url,
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		$(".inputTitle").val( data[0]["title"] );
	}
  });
  
});

$( ".play_episode" ).click(function() {
  var uri = $(this).attr('media_uri');
  var post_url_play = $(this).attr('post_url_play');
  //alert(uri);
  var data = {
	'uri': uri
  }
  
  $.ajax({
    type: 'POST',
    url: post_url_play,
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		console.log('play_uri_return', data);
		//alert(data[0]["short_name"]);
		$(".selected_zone").text( data[0]["short_name"] );
	}
  });
});

$( ".play-button" ).click(function() {
  if (window.playing == 0) {
    var data = { 'action': 'play' };
	$.ajax({
      type: 'POST',
      url: '/player_control',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
	  success: function(data){
		$( ".play-button" ).hide();
	    $( ".pause-button" ).show();
		window.playing = 1;
		progress_timer();
		/*
	    myTimer = setInterval( function(){
		  if (current > duration) {
		    window.location.reload(true);
		  }
		  
	      if (duration > 0) {
	        percent = parseInt(100 * (current/duration));
	      }
		  
		  hours = parseInt( current / 3600 ) % 24;
		  minutes = parseInt( current / 60 ) % 60;
		  seconds = current % 60;
		  
		  if (hours > 0) {
		    result = hours + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds  < 10 ? "0" + seconds : seconds);
		  } else {
		    result = minutes + ":" + (seconds  < 10 ? "0" + seconds : seconds);
		  }
		  
	      document.getElementById("track_pos").innerHTML = result;
	      document.getElementById("percentage").innerHTML = percent;
	      $('.progress-bar').css('width', percent+'%').attr('aria-valuenow', percent);  
	      current = current + 1;
	    }, 1000);
		*/
	  }
    });	
  }
  else {
    alert("Track is already playing!!");
  }
});

$( ".pause-button" ).click(function() {
  var data = { 'action': 'pause' };

  $.ajax({
    type: 'POST',
    url: '/player_control',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		clearInterval(myTimer);
		$( ".play-button" ).show();
		$( ".pause-button" ).hide();
		window.playing = 0;
		//alert("Pause (js)");
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		//$(".inputTitle").val( data[0]["title"] );
	}
  });
});

$( ".mute-button" ).click(function() {
  var data = { 'action': 'mute' };

  $.ajax({
    type: 'POST',
    url: '/player_control',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		$( ".mute-button" ).hide();
	    $( ".unmute-button" ).show();
		//alert("Muted (js)");
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		//$(".inputTitle").val( data[0]["title"] );
	}
  });
});

$( ".unmute-button" ).click(function() {
  var data = { 'action': 'unmute' };

  $.ajax({
    type: 'POST',
    url: '/player_control',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		$( ".mute-button" ).show();
	    $( ".unmute-button" ).hide();
		//alert("Unmuted (js)");
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		//$(".inputTitle").val( data[0]["title"] );
	}
  });
});

$( ".skip-back-button" ).click(function() {
  var data = { 'action': 'skip-back' };

  $.ajax({
    type: 'POST',
    url: '/player_control',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
	success: function(data){
		window.location.reload(true);
		//alert("Skipped back (js)");
		//console.log('set_zone_return', data);
		//alert(data[0]["short_name"]);
		//$(".inputTitle").val( data[0]["title"] );
	}
  });
});