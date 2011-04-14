// Renderer is based on the atlas demo for arbor.js:
// http://arborjs.org/atlas/

Renderer = function(canvas){
  canvas = $(canvas).get(0)
  var ctx = canvas.getContext("2d")
  var particleSystem = null

  var that = {
    init:function(system){
      particleSystem = system
      particleSystem.screen({padding:[10, 50, 10, 50]})

      //$(window).resize(that.resize)
      that.resize()
    
      that.initMouseHandling()
    },
    redraw:function(){
      if (particleSystem===null) return

      ctx.clearRect(0,0, canvas.width, canvas.height)
      ctx.strokeStyle = "#d3d3d3"
      particleSystem.eachEdge(function(edge, pt1, pt2){
          ctx.beginPath()
          ctx.lineWidth = edge.data.weight;
          ctx.moveTo(pt1.x, pt1.y)
          ctx.lineTo(pt2.x, pt2.y)
          ctx.stroke()
      })

      particleSystem.eachNode(function(node, pt){
        var label = node.data.sn||""
        var w = ctx.measureText(label).width + 6
        pt.x = Math.floor(pt.x)
        pt.y = Math.floor(pt.y)

        ctx.clearRect(pt.x-w/2, pt.y-7, w,14)

        // draw the text
        if (label){
          ctx.font = "bold 11px Arial"
          ctx.textAlign = "center"
          ctx.fillStyle = "#888888"
          ctx.fillText(label, pt.x, pt.y+4)
        }
      })    		
    },
    resize:function(){
      var w = 480, //$(window).width(),
          h = 240; //$(window).height();
      canvas.width = w; canvas.height = h
      particleSystem.screenSize(w,h)
      that.redraw()
    },
    initMouseHandling:function(){
      // no-nonsense drag and drop (thanks springy.js)
      selected = null;
      nearest = null;
      var dragged = null;
      var oldmass = 1

      $(canvas).mousedown(function(e){
          var pos = $(this).offset();
          var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
          selected = nearest = dragged = particleSystem.nearest(p);

          if (selected.node !== null){
          dragged.node.fixed = true
          }
          return false
      });

      $(canvas).mousemove(function(e){
        var old_nearest = nearest && nearest.node._id
          var pos = $(this).offset();
          var s = {x:e.pageX-pos.left, y:e.pageY-pos.top};

          nearest = particleSystem.nearest(s);
        if (!nearest) return

          if (dragged !== null && dragged.node !== null){
          var p = particleSystem.fromScreen(s)
              dragged.node.p = {x:p.x, y:p.y}
          }

        return false
      });

      $(window).bind('mouseup',function(e){
        if (dragged===null || dragged.node===undefined) return
        dragged.node.fixed = false
        dragged.node.tempMass = 100
          dragged = null;
          selected = null
          return false
      });
    }
  }
  return that
}

function loadCrowdNetworkGraph(canvas,users,tweets) {
  var nodes = {}
  $.each(users, function(i,user) {
      nodes[user._id] = user;
  });
  var edges = {};
  // make edges into a weighted undirected graph
  $.each(tweets, function(i,tweet) {
    if('ats' in tweet) {
      $.each(tweet.ats, function(j,at) {
        if(at in nodes && tweet.uid in nodes) {
          from = Math.min(tweet.uid,at);
          to = Math.max(tweet.uid,at);
          if(!(from in edges))
            edges[from] = {}
          if(to in edges[from])
            edges[from][to].weight+=1;
          else
            edges[from][to] = {weight:1};
        }
      });
    }
  });
  //start the force directed layout
  var sys = arbor.ParticleSystem(4000, 500, 0.5, 55)
  sys.renderer = Renderer(canvas)
  sys.merge({nodes:nodes, edges:edges})
  sys.parameters({stiffness:600})
}

function filterTweets(tweets,start,end){
	var subTweet = new Array();
	var count = 0;
	var i = 0;
	for (i = start; i < end; i++){
		subTweet[count] = tweets[i];
		count = count + 1;
	}
	return subTweet
}

function showTweets(list,tweets,users,start){
	if(tweets.length-start>5)
                subTweets = filterTweets(tweets,start,start + 5);
        else
                subTweets = tweets

	var nodes = {}
        $.each(users, function(i,user) {
                nodes[user._id] = user.sn;
        });

        var tweetInfo = '';
	while ( list.childNodes.length >= 1 )
        	list.removeChild( list.firstChild );      
	 
        jQuery.each(subTweets, function(i,tweet) {
        	tweetInfo = nodes[tweet.uid]+ ' : '

                var li = document.createElement('li');
                var p = document.createElement('p');
                p.appendChild(document.createTextNode(tweetInfo));
                p.appendChild(document.createElement('br'));
                p.appendChild(document.createTextNode(tweet.tx));
                li.appendChild(p)
                list.appendChild(li);
        });
}

//function nextPage(tweets,users,start){
//	alert(start)
//	var nextpage=document.getElementById('next');
//	nextpage.onclick=showTweets(tweets,users,start);
//}

function loadCrowdPopup(cid,elem) {
  jQuery.getJSON('/api/1/crowd/users/'+cid, function(users) {
    jQuery.getJSON('/api/1/crowd/tweets/'+cid, function(tweets) {
        loadCrowdNetworkGraph(elem.find('canvas'),users,tweets);
	
	var start = 0;
	var list=document.getElementById('mylist');
		
	showTweets(list,tweets,users,start);
	start += 5;
	if(start < tweets.length){
		var nextpage=document.getElementById('next');
		nextpage.appendChild(document.createTextNode('Next 5 tweets'));
		//nextpage.appendChild(document.createElement('a'));
		//nextpage.setAttribute('onclick', 'showTweets(tweets,users,start)'); 
		//nextpage.onclick=showTweets(tweets,users,start);
		start += 5;
	}
    });
  });
}
