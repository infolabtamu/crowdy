// Renderer is based on the atlas demo for arbor.js:
// http://arborjs.org/atlas/

Renderer = function(canvas){
  canvas = $(canvas).get(0)
  var ctx = canvas.getContext("2d")
  var particleSystem = null
  var labeled = null

  var that = {
    init:function(system){
      particleSystem = system
      particleSystem.screen({padding:30})

      that.resize()
      that.initMouseHandling()
    },
    redraw:function(){
      if (particleSystem===null) return

      ctx.clearRect(0,0, canvas.width, canvas.height)
      ctx.strokeStyle = "#d3d3d3"
      particleSystem.eachEdge(function(edge, pt1, pt2){
          ctx.beginPath()
          ctx.lineWidth = Math.min(10,edge.data.weight);
          ctx.moveTo(pt1.x, pt1.y)
          ctx.lineTo(pt2.x, pt2.y)
          ctx.stroke()
      })

      particleSystem.eachNode(function(node, pt){
        var label = node.name||""
        pt.x = Math.floor(pt.x)
        pt.y = Math.floor(pt.y)

        var lls = String(label)
        ctx.fillStyle = '#' + lls.substring(lls.length-3,lls.length)
        ctx.beginPath()
        ctx.arc(pt.x,pt.y,3,0,2*Math.PI)
        ctx.fill()
      })
      if(labeled) {
        var node = particleSystem.getNode(""+labeled._id)
        var pt = particleSystem.toScreen(node.p)
        var label = labeled.sn
        var w = ctx.measureText(label).width + 6
        ctx.clearRect(pt.x+3, pt.y+3, w,14)
        ctx.font = "bold 11px Arial"
        ctx.textAlign = "center"
        ctx.fillStyle = "#888888"
        ctx.fillText(label, pt.x+3+w/2, pt.y+10)
      }
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
      var dragged = null
      var startTime = null

      $(canvas).click(function(e){
        if (new Date()-startTime>500)
          return
        var pos = $(this).offset();
        var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
        var clicked = particleSystem.nearest(p);
        if (!labeled || clicked.node.name != labeled._id) {
          labeled = null
          $.getJSON('/api/1/user/id/'+clicked.node.name,function(user){
            labeled = user
          });
        }else {
          labeled = null
        }
      });

      $(canvas).mousedown(function(e){
          var pos = $(this).offset();
          var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
          dragged = particleSystem.nearest(p);
          startTime = new Date()

          if (dragged.node !== null){
            dragged.node.fixed = true
          }
          return false
      });

      $(canvas).mousemove(function(e){
          var pos = $(this).offset();
          var s = {x:e.pageX-pos.left, y:e.pageY-pos.top};

          var nearest = particleSystem.nearest(s);
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
          return false
      });
    }
  }
  return that
}

function loadCrowdNetworkGraph(canvas, users, index) {
  var nodes = {}
  $.each(users, function(i,user) {
      nodes[user._id] = user;
  });
  var edges = {};
  // make edges into a weighted undirected graph
  for(var i in index.uids) {
      var aid = index.aids[i];
      var uid = index.uids[i];
      from = Math.min(uid,aid);
      to = Math.max(uid,aid);
      if(!(from in edges))
        edges[from] = {}
      if(to in edges[from])
        edges[from][to].weight+=1;
      else
        edges[from][to] = {weight:1};
  }
  //start the force directed layout
  var sys = arbor.ParticleSystem(
          {friction:.3, stiffness:100, repulsion:10000, fps:30})
  sys.renderer = Renderer(canvas)
  sys.merge({nodes:nodes, edges:edges})
}

function loadTweets(div, tweets) {
  var page = null
  $.each(tweets, function(index, tweet) {
    if (index%5==0) {
      page = $("<div>")
      div.append(page)
    }
    page.append('<p>'+tweet.tx+'</p>')

  })
  $(".scrollable").scrollable({mousewheel:true, vertical:true});
}

function loadCrowdPopup(ev) {
    var elem = $("#crowdBox")
    elem.html("Loading...")
    jQuery.getJSON('/crowd/'+ev.data.cid, function(crowd_info) {
        elem.html(crowd_info.html)
        elem.overlay({
            load: true,
            mask: {
              color: '#000',
              effect: 'apple'
            }
        });
        elem.find('.tabs').tabs("div.pane")
        loadCrowdNetworkGraph(elem.find('canvas'), crowd_info.users, crowd_info.index);
        $('#startTime').html(new Date(1000*crowd_info.crowd.start).toString())
        $('#endTime').html(new Date(1000*crowd_info.crowd.end).toString())
        loadTweets($('#crowdTweets'), crowd_info.tweets)
    });
}
