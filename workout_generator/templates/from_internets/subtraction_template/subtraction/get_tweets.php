<?php
session_start();
require_once("twitteroauth/twitteroauth.php"); //Path to twitteroauth library
 
$twitteruser = "BreakingNews";
$notweets = 30;
$consumerkey = "U82KywhgeaZI2bqRoEJSg";
$consumersecret = "b7uNyrwSI459XHZUsiCtVbCCkLq1t3vQ0xzXqiDj30";
$accesstoken = "334151186-rAyPs7PzXFmY0IzmisEnJG30dVFDKxpNcagzpivK";
$accesstokensecret = "JMZMZxWjp9YunVRfch6U0MBJJ9Ju6JWIyxlZMH7Tuyk";
 
function getConnectionWithAccessToken($cons_key, $cons_secret, $oauth_token, $oauth_token_secret) {
  $connection = new TwitterOAuth($cons_key, $cons_secret, $oauth_token, $oauth_token_secret);
  return $connection;
}
  
$connection = getConnectionWithAccessToken($consumerkey, $consumersecret, $accesstoken, $accesstokensecret);
 
$tweets = $connection->get("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=".$twitteruser."&count=".$notweets);
 
echo json_encode($tweets);
?>