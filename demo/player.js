// ripped from somewhere, needed some way to fetch blob from image
const toDataURL = url => fetch(url)
  .then(response => response.blob())
  .then(blob => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    document.body.backgroundImage = "url(" + reader.readAsDataURL(blob) + ")";
  }));

document.addEventListener("DOMContentLoaded", function() { startplayer(); }, false);

var player, playbutton, timestamp, b, playerContainer, trackList;
var tracks = [];
var shouldUpdate = false;
var doc, songs;
var playingID = 4;
var bgImage, bg;

function init() {
  b = document.getElementsByTagName('body')[0];
}

function getImage(fetchURL, bg){
  fetch(fetchURL)
  .then(response => response.blob())
  .then(images => {
      // then create a local URL for that image and print it
      bg.style.backgroundImage = URL.createObjectURL(images);
  })
}

function toggle_track(id) {
  // set playingID to the selected ID
  playingID = id;
  // if the track title is different
  if (bgArt.getElementsByClassName('track_title')[0].innerHTML != songs[id].getElementsByClassName('library_track_title')[0].innerHTML) {
    // change all the attributes of the player to match the new value
    bgArt.getElementsByClassName('track_title')[0].innerHTML = songs[id].getElementsByClassName('library_track_title')[0].innerHTML;
    bgArt.getElementsByClassName('track_artist')[0].innerHTML = songs[id].getElementsByClassName('library_track_artist')[0].innerHTML;
    bgArt.getElementsByClassName('album_title')[0].innerHTML = songs[id].getElementsByClassName('library_album_title')[0].innerHTML;
    player.getElementsByClassName('music_src')[0].setAttribute('src', songs[id].getElementsByClassName('library_track_src')[0].getAttribute('href'));
    timestamp.innerHTML = "" + stm(player.currentTime) + " / " + stm(player.duration);
    document.getElementById('album_art').setAttribute('src', songs[id].getElementsByClassName('library_art')[0].getAttribute('src'));
    bgArt.getElementsByTagName('a')[0].setAttribute('href', songs[id].getElementsByClassName('library_track_src')[0].getAttribute('href'));
    
    // fetch album art and convert to base64 to set to background
    toDataURL(songs[id].getElementsByClassName('library_art')[0].getAttribute('src'))
      .then(dataUrl => {
        document.body.style.backgroundImage = "url('" + songs[id].getElementsByClassName('library_art')[0].getAttribute('src') + "')";
        document.body.style.backgroundSize = "cover";
      })

    // toggle the player
    player.load();
    playAudio();
    refreshTimestamp();
  }
}

function startplayer()
{
  // get the pre-gen html file
  /*fetch('/magna_opera.html').then(function (response) {
    return response.text();
  }).then(function (html) {
    var parser = new DOMParser();
  	document.getElementById("track_list").innerHTML = html;
    doc = parser.parseFromString(html, 'text/html');
    songs = doc.getElementsByClassName('library_track');
  }).catch(function (err) {
  	// There was an error
  	console.warn('Something went wrong.', err);
  });*/

  // set all variables that will be reused throughout
  wrapper = document.getElementById('wrapper');
  player = document.getElementById('music_player');
  playButton = document.getElementById("play_button");
  player.controls = false;
  playButton.addEventListener("click", handlePlayButton, false);
  timestamp = document.getElementById("timestamp");
  bgArt = document.getElementById("player");

  trackList = document.getElementsByClassName("track_list");

  timestamp.innerHTML = "" + stm(player.currentTime) + " / " + stm(player.duration);

  playerContainer = document.getElementById("player");

  player.onloadedmetadata = function() {
    refreshTimestamp();
}

player.ontimeupdate = function() {
    refreshTimestamp();
}
}

// convert number of seconds to string mm:ss
function stm(input) {
    var mins = ~~((input % 3600) / 60);
    var secs = ~~input % 60;

    var res = "";
    res = "0" + mins + ":" + (secs < 10 ? "0" : "") + "" + secs + "";
    return res;
}

async function playAudio() {
  try {
    await player.play();
    //songs[playingID].getElementsByClassName('library_play_button')[0].setAttribute("src", "pause.png");
    playButton.setAttribute("src", "pause.png");
  } catch(err) {
    //playButton.remove("playing");
  }
  shouldUpdate = true;
  //document.body.classList.remove("fade-out");
  //document.body.classList.add("fade-in");
}

function handlePlayButton() {
  if (player.paused) {
    playAudio();
    playButton.setAttribute("src", "play.png");
    //songs[playingID].getElementsByClassName('library_play_button')[0].setAttribute("src", "play.png");
  } else {
    //b.style.background = "black";
    //document.body.classList.remove("fade-in");
    //document.body.classList.add("fade-out");
    player.pause();
    shouldUpdate = false;
    playButton.setAttribute("src", "play.png");
    //playButton.classList.remove("playing");
  }
}

function refreshTimestamp() {
    timestamp.innerHTML = "" + stm(player.currentTime) + " / " + stm(player.duration);

    var trackProgress = (player.currentTime / player.duration);
    var sliderProgress = document.getElementById('trackSlider').offsetWidth * trackProgress;

    document.getElementById('trackProgress').style.width = Math.round(sliderProgress) + "px";
}

function setLocation(percentage) {
  player.currentTime = player.duration * percentage;
}

function resetTrack() {
  player.currentTime = 0;
}

function setSongPosition(obj,e){
  var songSliderWidth = obj.offsetWidth;
  var evtobj=window.event? event : e;
  clickLocation = e.clientX - obj.offsetLeft;

  var percentage = (clickLocation/songSliderWidth);

  setLocation(percentage);
}

function change_vol() {
  player.volume=document.getElementById("change_vol").value;
}
