// Connect to server through socketio
var socket = io();

function reconnect() {
  socket = io();
}

// Allow certain text characters to format the message
String.prototype.format = function() {
  // Replace ~text~ for a code block
  // Replace *text* for bold
  return this.replace(/\~([^\~]+)\~/g, "<code>$1</code>").replace(/\*([^\*]+)\*/g, "<strong>$1</strong>");
}

// Convert all urls to clickable urls
String.prototype.urlify = function() {
  return this.replace(/(https?:\/\/[^\s]+)/g, function(url) {
    return "<a href='" + url + "' target='_blank'>" + url + "</a>";
  });
}

// Replace all HTML except for bold, underline, and italics
String.prototype.stripTags = function() {
  return this.replace(/(<([^>]+)>)/gi, "");
}

// Scroll to bottom of chat frame
function scroll() {
  $("#chatFrame").animate({
    scrollTop: $("#chatFrame").get(0).scrollHeight
  });
}

$(document).ready(function() {
  // Try to reconnect if disconnected from server
  socket.on("disconnect", function() {
    reconnect();
  });

  // Empty chat frame
  socket.on("clear", function() {
    $("#chatFrame").html("");
  });

  // Append message to chat frame
  socket.on("message", function(data) {
    // If message is private, show private icon
    if (data.length == 5) {
      data[1] = "<span class='notification'>private</span>" + data[1]
    }
    // Layer message if...
    // The previous message was sent by the same user
    // The previous message wasn't privte
    // The message is sent on the same day
    if ($("#chatFrame div:last-child .name").html() == data[0] && data.length != 5 && !$("#chatFrame div:last-child .notification").length && $("#chatFrame div:last-child .time").text().substring(0, $("#chatFrame div:last-child .time").text().length - 8) == data[1].substring(0, data[1].length-8)) {
      $("#chatFrame div:last-child .cont").html($("#chatFrame div:last-child .cont").html() + "<br />" + data[2].format());
    }
    else {
      $("#chatFrame").append("<div><p><span class='name' style='background-color: " + data[3] + "'>" + data[0] + "</span><span class='time'>" + data[1] + "</span></p><p class='cont'>" + data[2].format() + "</p></div>");
    }
    // Check for math
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, "p"]);
    // Scroll to bottom of chat frame
    scroll();
  });

  socket.on("mass message", function(data) {
    // Clear chat frame
    $("#chatFrame").html("");
    // Append each message specified
    data.forEach(function(item) {
      if (item.length == 5) {
        item[1] = "<span class='notification'>private</span>" + item[1]
      }
      // Layer message if...
      // The previous message was sent by the same user
      // The previous message wasn't privte
      // The message is sent on the same day
      if ($("#chatFrame div:last-child .name").html() == item[0] && item.length != 5 && !$("#chatFrame div:last-child .notification").length && $("#chatFrame div:last-child .time").text().substring(0, $("#chatFrame div:last-child .time").text().length - 8) == item[1].substring(0, item[1].length-8)) {
        $("#chatFrame div:last-child .cont").html($("#chatFrame div:last-child .cont").html() + "<br />" + item[2].format());
      }
      else {
        $("#chatFrame").append("<div><p><span class='name' style='background-color: " + item[3] + "'>" + item[0] + "</span><span class='time'>" + item[1] + "</span></p><p class='cont'>" + item[2].format() + "</p></div>");
      }
    });
    // Check for math
    try {
      MathJax.Hub.Queue(["Typeset", MathJax.Hub, "p"]);
    }
    catch(err) {
      // Don't do anything if error with math
    }
    // Ensure video and audio files are loaded
    checkEmbeded("video");
    checkEmbeded("audio");
    scroll();
  });

  // Open file upload window if image icon is clicked
  $("#uploadImage").click(function() {
    if ($("#sendArea").val().length == 0) {
      document.getElementById("fileToUpload").click();
    }
  });

  $("#sendArea").submit(function(e) {
    e.preventDefault();
    try {
      if (socket.connected) {
        // If message isn't blank
        if ($("#message").val().replace(/ /g, "").replace("\`", "") != "") {
          try {
            // Send message to server
            socket.emit("message", $("#message").val().stripTags().urlify());
          }
          catch(err) {
            reconnect();
            socket.emit("message", $("#message").val().stripTags().urlify());
          }
          $("#message").val("");
          $("#uploadImage").css("opacity", 0.65);
        }
      }
      else {
        reconnect();
      }
    }
    catch(err) {
      reconnect();
    }
  });

  $("#fileToUpload").change(function() {
    $("#imageUpload").submit();
  });

  $("#imageUpload").submit(function(e) {
    e.preventDefault();
    if (socket.connected) {
      // Grab selected file
      var file = $("input[type='file']").get(0).files[0];
      $(this)[0].reset();
      if (file) {
        // Ensure that the file isn't too large
        if (file.size <= 8000000) {
          try {
            // Send file, file extension, and file name to server
            socket.emit("file", [file, file.name.split(".").pop(), file.name]);
          }
          catch(err) {
            reconnect();
          }
        }
        else {
          // Notify user that their file is too large
          alert("File too large.  Max file size is 8 MB");
        }
      }
    }
    else {
      reconnect();
    }
  });
});

// Append text to send area
$(document).on("click", ".name", function() {
  if ($("#message").val()[$("#message").val().length - 1] == " " || $("#sendArea").val()[$("#sendArea").val().length-1] == null) {
    $("#message").val($("#message").val() + "@" + event.target.innerHTML + " ");
  }
  // Add a space before @ mention if there isn't a space already
  else {
    $("#message").val($("#message").val() + " @" + event.target.innerHTML + " ");
  }
  // Hide file upload button if message area has text
  $("#message").val().length > 0 ? $("#uploadImage").css("opacity", 0) : $("#uploadImage").css("opacity", 0.65);
});
