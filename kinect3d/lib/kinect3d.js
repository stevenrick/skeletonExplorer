// Create a 3d scatter plot within d3 selection parent.
function kinect3d( parent)
{
  var csvfile = location.search.split('csv=')[1] ? location.search.split('csv=')[1] : 'data/pilot4_rightOfLegs_top_1_bodyTracking.csv';  

  var x3d = parent  
    .append("x3d")
      .style( "width", parseInt(parent.style("width"))+"px" )
      .style( "height", parseInt(parent.style("height"))+"px" )
      .style( "border", "none" )
      
  var scene = x3d.append("scene")

  scene.append("orthoviewpoint")
     .attr( "centerOfRotation", [5, 5, 5])
     .attr( "fieldOfView", [-5, -5, 15, 15])
     .attr( "orientation", [-0.5, 1, 0.2, 1.12*Math.PI/4])
     .attr( "position", [8, 4, 15])
     

  var Time = [], HipCenter = [], Spine = [], ShoulderCenter = [], Head = [], ShoulderLeft = [], ElbowLeft = [], WristLeft = [],
    		HandLeft = [], ShoulderRight = [], ElbowRight = [], WristRight = [], HandRight = [], HipLeft = [], KneeLeft = [], 
    	    AnkleLeft = [], FootLeft = [], HipRight = [], KneeRight = [], AnkleRight = [], FootRight = [];

  var rows = [];
  
  var play = false;
  var lastStep=0;
  var timer;
  var slider;
  
  var axisRange = [0, 10];
  var scales = [];
  var initialDuration = 0;
  var defaultDuration = 800;
  var ease = 'linear';
  var time = 0;
  var axisKeys = ["x", "y", "z"]

  // Helper functions for initializeAxis() and drawAxis()
  function axisName( name, axisIndex ) {
    return ['x','y','z'][axisIndex] + name;
  }

  function constVecWithAxisValue( otherValue, axisValue, axisIndex ) {
    var result = [otherValue, otherValue, otherValue];
    result[axisIndex] = axisValue;
    return result;
  }

  // Used to make 2d elements visible
  function makeSolid(selection, color) {
    selection.append("appearance")
      .append("material")
         .attr("diffuseColor", color||"black")
    return selection;
  }

  // Initialize the axes lines and labels.
  function initializePlot() {
    initializeAxis(0);
    initializeAxis(1);
    initializeAxis(2);
  }

  function initializeAxis( axisIndex )
  {
    var key = axisKeys[axisIndex];
    drawAxis( axisIndex, key, initialDuration );

    var scaleMin = axisRange[0];
    var scaleMax = axisRange[1];

    // the axis line
    var newAxisLine = scene.append("transform")
         .attr("class", axisName("Axis", axisIndex))
         .attr("rotation", ([[0,0,0,0],[0,0,1,Math.PI/2],[0,1,0,Math.PI/2]][axisIndex]))
      .append("shape")
    newAxisLine
      .append("appearance")
      .append("material")
        .attr("emissiveColor", "lightgray")
    newAxisLine
      .append("polyline2d")
         // Line drawn along y axis does not render in Firefox, so draw one
         // along the x axis instead and rotate it (above).
        .attr("lineSegments", "0 0," + scaleMax + " 0")

   // axis labels
   var newAxisLabel = scene.append("transform")
       .attr("class", axisName("AxisLabel", axisIndex))
       .attr("translation", constVecWithAxisValue( 0, scaleMin + 1.1 * (scaleMax-scaleMin), axisIndex ))

	if(axisIndex=='2'){
		newAxisLabel = scene.append("transform")
       .attr("class", axisName("AxisLabel", axisIndex))
       .attr("translation", constVecWithAxisValue( 0, scaleMin -1.1 * (scaleMax-scaleMin), axisIndex ))

	}

   var newAxisLabelShape = newAxisLabel
     .append("billboard")
       .attr("axisOfRotation", "0 0 0") // face viewer
     .append("shape")
     .call(makeSolid)

   var labelFontSize = 0.6;

   newAxisLabelShape
     .append("text")
       .attr("class", axisName("AxisLabelText", axisIndex))
       .attr("solid", "true")
       .attr("string", key)
    .append("fontstyle")
       .attr("size", labelFontSize)
       .attr("family", "SANS")
       .attr("justify", "END MIDDLE" )
  }

  // Assign key to axis, creating or updating its ticks, grid lines, and labels.
  function drawAxis( axisIndex, key, duration ) {

    var scale = d3.scale.linear()
      .domain( [-5,5] ) // demo data range
      .range( axisRange )
    
    scales[axisIndex] = scale;

    var numTicks = 0;
    var tickSize = 0.1;
    var tickFontSize = 0.5;

    // ticks along each axis
    var ticks = scene.selectAll( "."+axisName("Tick", axisIndex) )
       .data( scale.ticks( numTicks ));
    var newTicks = ticks.enter()
      .append("transform")
        .attr("class", axisName("Tick", axisIndex));
    newTicks.append("shape").call(makeSolid)
      .append("box")
        .attr("size", tickSize + " " + tickSize + " " + tickSize);
    // enter + update
    ticks.transition().duration(duration)
      .attr("translation", function(tick) { 
         return constVecWithAxisValue( 0, scale(tick), axisIndex ); })
    ticks.exit().remove();

    // tick labels
    var tickLabels = ticks.selectAll("billboard shape text")
      .data(function(d) { return [d]; });
    var newTickLabels = tickLabels.enter()
      .append("billboard")
         .attr("axisOfRotation", "0 0 0")     
      .append("shape")
      .call(makeSolid)
    newTickLabels.append("text")
      .attr("string", scale.tickFormat(10))
      .attr("solid", "true")
      .append("fontstyle")
        .attr("size", tickFontSize)
        .attr("family", "SANS")
        .attr("justify", "END MIDDLE" );
    tickLabels // enter + update
      .attr("string", scale.tickFormat(10))
    tickLabels.exit().remove();

  }

  // Update the data points (spheres) and stems.
  function plotData( duration ) {
    
    if (!rows) {
     console.log("no rows to plot.")
     return;
    }

    var x = scales[0], y = scales[1], z = scales[2];
    var sphereRadius = 0.1	;

    // Draw a sphere at each x,y,z coordinate.
    var datapoints = scene.selectAll(".datapoint").data( rows );
    datapoints.exit().remove()

    var newDatapoints = datapoints.enter()
      .append("transform")
        .attr("class", "datapoint")
        .attr("scale", [sphereRadius, sphereRadius, sphereRadius])
      .append("shape");
    newDatapoints
      .append("appearance")
      .append("material");
    newDatapoints
      .append("sphere")
       // Does not work on Chrome; use transform instead
       //.attr("radius", sphereRadius)

    datapoints.selectAll("shape appearance material")
        .attr("diffuseColor", 'steelblue' )

    datapoints.transition().ease(ease).duration(duration)
        .attr("translation", function(row) { 
          xCoord = row[axisKeys[0]] *5;
          yCoord = -row[axisKeys[1]] * 5;
          zCoord = -row[axisKeys[2]] * 5;
          return x(xCoord) + " " + y(yCoord) + " " + z(zCoord)})

    // Draw a stem from the x-z plane to each sphere at elevation y.
    // This convention was chosen to be consistent with x3d primitive ElevationGrid. 
    // var stems = scene.selectAll(".stem").data( rows );
//     stems.exit().remove();
// 
//      var newStems = stems.enter()
//       .append("transform")
//         .attr("class", "stem")
//       .append("shape");
//     newStems
//       .append("appearance")
//       .append("material")
//         .attr("emissiveColor", "gray")
//     newStems
//       .append("polyline2d")
//         .attr("lineSegments", function(row) { return "0 1, 0 0"; })
// 
//  	stems.transition().ease(ease).duration(duration)
//         .attr("translation", 
//            function(row) { 
// 	          xCoord = row[axisKeys[0]] *5;
//     	      yCoord = row[axisKeys[1]] * 5;
//         	  zCoord = -row[axisKeys[2]] * 5;
// 	          return "" + x(xCoord) + " 0 " + z(zCoord); 
// 	        })
//         .attr("scale",
//            function(row) { return [1, y(row[axisKeys[1]] * 5)]; })


  }

  function initializeDataGrid() {
    d3.csv(csvfile, function(csv){
		csv.map(function(d) {
	   	 	Time.push(d.Time);
    		HipCenter.push([d.HipCenterX, d.HipCenterY, d.HipCenterZ]);    	
    		Spine.push([d.SpineX, d.SpineY, d.SpineZ]);    	
    		ShoulderCenter.push([d.ShoulderCenterX, d.ShoulderCenterY, d.ShoulderCenterZ]); 
			Head.push([d.HeadX, d.HeadY, d.HeadZ]);    	
    		ShoulderLeft.push([d.ShoulderLeftX, d.ShoulderLeftY, d.ShoulderLeftZ]);    	
    		ElbowLeft.push([d.ElbowLeftX, d.ElbowLeftY, d.ElbowLeftZ]);    	
    		WristLeft.push([d.WristLeftX, d.WristLeftY, d.WristLeftZ]);    	
    		HandLeft.push([d.HandLeftX, d.HandLeftY, d.HandLeftZ]);    	
    		ShoulderRight.push([d.ShoulderRightX, d.ShoulderRightY, d.ShoulderRightZ]);    	
    		ElbowRight.push([d.ElbowRightX, d.ElbowRightY, d.ElbowRightZ]);    	
    		WristRight.push([d.WristRightX, d.WristRightY, d.WristRightZ]);    	
    		HandRight.push([d.HandRightX, d.HandRightY, d.HandRightZ]);
    		HipLeft.push([d.HipLeftX, d.HipLeftY, d.HipLeftZ]);    	
    		KneeLeft.push([d.KneeLeftX, d.KneeLeftY, d.KneeLeftZ]);    	
    		AnkleLeft.push([d.AnkleLeftX, d.AnkleLeftY, d.AnkleLeftZ]);    	
    		FootLeft.push([d.FootLeftX, d.FootLeftY, d.FootLeftZ]);    	
    		HipRight.push([d.HipRightX, d.HipRightY, d.HipRightZ]);    	
    		KneeRight.push([d.KneeRightX, d.KneeRightY, d.KneeRightZ]);    	
    		AnkleRight.push([d.AnkleRightX, d.AnkleRightY, d.AnkleRightZ]);    	
    		FootRight.push([d.FootRightX, d.FootRightY, d.FootRightZ]);  

		});    
		var frame = gup( 'frame' );
		if(frame==null) frame =0;
		updateData(frame);
		var axis = d3.svg.axis().orient("top").ticks(4);
		//var maxTime=Time[Time.length-1];
		//var a = maxTime.split(':'); // split it at the colons
		//var seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]); 
    	
    	
    	slider=$( "#slider" ).slider({
      		range: "max",
     		min: 1,
      		max: Time.length-1,
      		value: frame,
      		slide: function( event, ui ) {
	      		updateData(ui.value);
  				plotData(5);
      		}
    	});
        d3.select("#selector")
      	  .on("change", function(d) {
          var value = d3.select(this).property("value");
          console.log(value)
          initializeDataGrid(value);
        });
    	
		$( "#frame" ).val( $( "#slider" ).slider( "value" ) );
		
		d3.select('#buttons').append('input')
          .attr('type', 'image')
          .attr('src', 'images/blue-play-button-md.png')
          .attr('class', 'play')
    		.on("click", function(evt, value) {
  				play = toggle(this);
  				if(play){
  					timer = window.setInterval(clock, 34);
  					//console.log('start')
  				}
  				else{
  					//console.log('clear')
  					clearInterval(timer);
  				}	
			});

    });
  }


  function clock() {
  		//console.log('tick')
  		updateData(lastStep+1)
  }
  
  function updateData(step) {
  		//console.log(play)
  		//console.log(step)
  		lastStep=step;
  		rows=[];
		if(HipCenter[step] !=null && HipCenter[step][0]!="") rows.push({x:HipCenter[step][0] , y: HipCenter[step][1], z: HipCenter[step][2]});
		if(Spine[step] != null && Spine[step][0]!="") rows.push({x:Spine[step][0] , y: Spine[step][1], z: Spine[step][2]});
		if(ShoulderCenter[step] != null && ShoulderCenter[step][0]!="") rows.push({x:ShoulderCenter[step][0] , y: ShoulderCenter[step][1], z: ShoulderCenter[step][2]});
		if(Head[step] != null && Head[step][0]!="") rows.push({x:Head[step][0] , y: Head[step][1], z: Head[step][2]});
		if(ShoulderLeft[step] != null && ShoulderLeft[step][0]!="") rows.push({x:ShoulderLeft[step][0] , y: ShoulderLeft[step][1], z: ShoulderLeft[step][2]});
		if(ElbowLeft[step] != null && ElbowLeft[step][0]!="") rows.push({x:ElbowLeft[step][0] , y: ElbowLeft[step][1], z: ElbowLeft[step][2]});
		if(WristLeft[step] != null && WristLeft[step][0]!="") rows.push({x:WristLeft[step][0] , y: WristLeft[step][1], z: WristLeft[step][2]});
		if(HandLeft[step] != null && HandLeft[step][0]!="") rows.push({x:HandLeft[step][0] , y: HandLeft[step][1], z: HandLeft[step][2]});
		if(ShoulderRight[step] != null && ShoulderRight[step][0]!="") rows.push({x:ShoulderRight[step][0] , y: ShoulderRight[step][1], z: ShoulderRight[step][2]});
		if(ElbowRight[step] != null && ElbowRight[step][0]!="") rows.push({x:ElbowRight[step][0] , y: ElbowRight[step][1], z: ElbowRight[step][2]});
		if(WristRight[step] != null && WristRight[step][0]!="") rows.push({x:WristRight[step][0] , y: WristRight[step][1], z: WristRight[step][2]});
		if(HandRight[step] != null && HandRight[step][0]!="") rows.push({x:HandRight[step][0] , y: HandRight[step][1], z: HandRight[step][2]});
		if(HipLeft[step] != null && HipLeft[step][0]!="") rows.push({x:HipLeft[step][0] , y: HipLeft[step][1], z: HipLeft[step][2]});
		if(KneeLeft[step] != null && KneeLeft[step][0]!="") rows.push({x:KneeLeft[step][0] , y: KneeLeft[step][1], z: KneeLeft[step][2]});
		if(AnkleLeft[step] != null && AnkleLeft[step][0]!="") rows.push({x:AnkleLeft[step][0] , y: AnkleLeft[step][1], z: AnkleLeft[step][2]});
		if(FootLeft[step] != null && FootLeft[step][0]!="") rows.push({x:FootLeft[step][0] , y: FootLeft[step][1], z: FootLeft[step][2]});
		if(HipRight[step] != null && HipRight[step][0]!="") rows.push({x:HipRight[step][0] , y: HipRight[step][1], z: HipRight[step][2]});
		if(KneeRight[step] != null && KneeRight[step][0]!="") rows.push({x:KneeRight[step][0] , y: KneeRight[step][1], z: KneeRight[step][2]});
		if(AnkleRight[step] != null && AnkleRight[step][0]!="") rows.push({x:AnkleRight[step][0] , y: AnkleRight[step][1], z: AnkleRight[step][2]});
		if(FootRight[step] != null && FootRight[step][0]!="") rows.push({x:FootRight[step][0] , y: FootRight[step][1], z: FootRight[step][2]});
		
		if(step==0) plotData(defaultDuration);
		else plotData(5);
		
		if(slider!=null && slider.value!=step){
			slider.slider( "value", step );
			$( "#frame" ).val( $( "#slider" ).slider( "value" ) );
		}
		
		return true;
  }
  
  function toggle(el){
    if(el.className!="pause")
    {
        el.src='images/pause+button.jpg';
        el.className="pause";
        return true;
    }
    else if(el.className=="pause")
    {
        el.src='images/blue-play-button-md.png';
        el.className="play";
        return false;
    }
}
  
  initializeDataGrid();
  initializePlot();
}

function gup( name )
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if( results == null )
    return null;
  else
    return results[1];
}

  