// Get the theme
var theme = getCookie("theme");

// Change stylesheet to selected file
function change_stylesheet(sheet) {
  document.getElementById("theme").setAttribute("href", sheet);
}

// Ensure that the passwords are the same
function checkPass(p1, p2) {
  if (document.getElementById(p1).value == document.getElementById(p2).value) {
    document.getElementById(p1).setCustomValidity("");
    return true;
  }
  else {
    document.getElementById(p1).setCustomValidity("Passwords do not match");
    return false;
  }
}

// Execute theme change
function themeChange(theme) {
  var cookieDate = new Date();
  cookieDate.setTime(cookieDate.getTime() + (1320 * 24 * 60 * 60 * 1000));
  // If dark theme selected, update cookie and show dark theme
  if (theme == "dark") {
    change_stylesheet(darkUrl);
    document.cookie = "theme=dark; expires=" + cookieDate + "; path=/;";
  }
  // If light theme selected, use light theme and update cookie
  else {
    change_stylesheet(lightUrl);
    document.cookie = "theme=light; expires=" + cookieDate + "; path=/;";
  }
}

// Retrieve cookie
// From w3schools
function getCookie(cname) {
  var name = cname + "=";
  var decoded = decodeURIComponent(document.cookie);
  var ca = decoded.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

// Copy selected text
function copy(val) {
  // Create element to copy
  var temp = document.createElement("input");
  temp.style = "position: absolute; left: -1000px; top: -1000px";
  // Add value to copy to element
  temp.value = val;
  document.body.appendChild(temp);
  temp.select();
  // Copy element
  document.execCommand("copy");
  // Remove element
  document.body.removeChild(temp);
}

$(document).ready(function() {
  themeChange(theme);
  $("body").show();

  // Determine if upload image icon will show
  $("#message").keyup(function() {
    $(this).val().length > 0 ? $("#uploadImage").css("opacity", 0) : $("#uploadImage").css("opacity", 0.65);
  });

  // Make user confirm their action
  $("#delete").click(function(e) {
    if (!confirm("This action is irreversable.  Do you confirm this action?")) {
      e.preventDefault();
    }
  });

  // If theme change switch changed, change theme
  $(".switch").change(function() {
    $(".switch input").is(":checked") ? themeChange("dark") : themeChange("light");
  });

  // Ensure that passwords match
  $("#passwordSet").submit(function(e) {
    if (!checkPass("password", "password2")) {
      e.preventDefault();
    }
  });

  // Ensure that room name isn't too long
  $("#createRoom").submit(function(e) {
    if ($("input[maxlength='32']").val().replace(/ /g, "").length == 0) {
      e.preventDefault();
    }
  });
});

// Custom autocomplete for @ mentions in chat
$("#members").ready(function() {
  // Add event listener for the message send area
  $("#message").on("input", function() {
    // Remove autocomplete if already exists
    $("#autoframe").remove();
    $("#mainarea").css("padding-bottom", "30px");
    // Get last index of message
    var message = $(this).val().split(" ")[$(this).val().split(" ").length - 1];
    if (message) {
      // Create frame
      var autoframe = $("<div id='autoframe'></div>");
      // Add item to frame if applicable
      members.forEach(function(item) {
        if (item.slice(0, message.length) == message) {
          // Bold the area the user has already typed
          autoframe.append("<p class='nameelement'><strong>" + item.slice(0, message.length) + "</strong>" + item.slice(message.length, item.length) + "</p>");
        }
      });
      // Add frame to the page
      $("#sendArea").append(autoframe);
      // Position the frame
      autoframe.css("margin-left", "5%");
      $("#mainarea").css("padding-bottom", "0");
    }
  });
});

// Append autocomplete item to message area on click
$(document).on("click", ".nameelement", function(e) {
  $("#message").val($("#message").val().substring(0, $("#message").val().lastIndexOf("@")) + event.target.innerHTML.replace(/(<([^>]+)>)/gi, ""));
  $("#autoframe").remove();
  $("#mainarea").css("padding-bottom", "30px");
});

// Ensure that all video and audio files are loaded
function checkEmbeded(which) {
  var elements = document.querySelectorAll(which);
  for (var i = 0; i < elements.length; i++) {
    // If file isn't loaded, show 'file deleted' message
    elements[i].addEventListener("error", function() {
      // Grab the file's parent node
      var parent = this.parentNode;
      // Remove all children
      while (parent.hasChildNodes()) {
        parent.removeChild(parent.firstChild);
      }
      parent.innerHTML = "";
      // Create new element
      var message = document.createElement("p");
      // Add message to element
      message.innerHTML = "file deleted";
      // Add element as a child to the parent
      parent.appendChild(message);
    }, true);
  }
}

// Use random greeting on home page depending on hour
$("#greeting").ready(function() {
  // Default greetings
  var greetings = ["Hello", "Hi", "Greetings"];
  // Get hour of day
  var now = new Date().getHours();
  // Add message depending on time
  if (now < 12) {
    greetings.push("Good morning");
  }
  else if (now < 18) {
    greetings.push("Good afternoon");
  }
  else {
    greetings.push("Good evening");
  }
  // Append to page
  $("#greeting").html(greetings[Math.floor(Math.random() * greetings.length)]);
});

function showColorPicker() {
  var options = document.getElementById("colorPicker").getElementsByTagName("input");
  for (var i = 0; i < options.length; i++) {
    options[i].parentNode.style.borderColor = options[i].value;
  }
}
