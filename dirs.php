<?php

// Delete directory
function delete_dir($dir_path) {
  // Get subdirectories
  if (substr($dir_path, strlen($dir_path) - 1, 1) != "/") {
    $dir_path .= "/";
  }
  // Get subfiles
  $files = glob($dir_path . "*", GLOB_MARK);
  // Iterate through each file and delete it
  foreach ($files as $file) {
    // If file is subdirectory, delete subdirectory
    if (is_dir($file)) {
      delete_dir($file);
    }
    else {
      unlink($file);
    }
  }
  // Delete directory
  rmdir($dir_path);
}

// Gets the oldest file in directory
function get_oldest_file($user) {
  $files = glob("uploads/users/" . $user . "/*.*");
  // Sorts files so oldest is index zero
  array_multisort(array_map("filemtime", $files), SORT_NUMERIC, SORT_ASC, $files);
  // Oldest file
  return $files[0];
}

// Gets size of directory
// Used guidance from StackOverflow
// https://stackoverflow.com/questions/478121/how-to-get-directory-size-in-php
function get_dir_size($user) {
  $bytes = 0;
  $path = realpath("uploads/users/" . $user);
  // If path exists, start calculation
  if ($path != false && $path != "" && file_exists($path)) {
    // Iterates through files and adds size to bytes variable
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path, FilesystemIterator::SKIP_DOTS)) as $file) {
      $bytes += $file->getSize();
    }
  }
  return $bytes;
}

// What happens if user exceeds their file storage limit
function check_file_overload($user) {
  if (file_exists("uploads/users/" . $user)) {
    // Runs until the file limit is acceptable
    while (get_dir_size($user) > 12000000) {
      // Deletes their oldest file
      unlink(get_oldest_file($user));
    }
  }
}

// If data was sent, grab it
if ($argc > 1) {
  // Grab argument data
  $json_data = $argv[1];
  // Convert JSON into PHP object
  $data = json_decode($json_data);
}

// Determine what task PHP should do
switch ($data->task) {
  // If user's account is deleted, delete their directory
  case "delete dir":
    // If directory exists, delete it
    if (file_exists("uploads/users/" . $data->user)) {
      delete_dir("uploads/users/" . $data->user);
    }
    break;

  // If user creates account, give them directory for images
  case "create dir":
    // If directory doesn't exist, create it
    if (!file_exists("uploads/users/" . $data->user)) {
      mkdir("uploads/users/" . $data->user, 0777, true);
    }
    break;

  // Checks if user has exceeded their filelimit and delete files if so
  case "check filelimit":
    check_file_overload($data->user);
    break;
}

?>
