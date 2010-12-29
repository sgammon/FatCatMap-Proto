var w = $("#viz_content").width(),
    h = $("#viz_content").height(),
    colors = pv.Colors.category19();

var vis = new pv.Panel(document.getElementById('viz_content'))
    .width(w)
    .height(h)
    .fillStyle("white")
    .event("mousedown", pv.Behavior.pan())
    .event("mousewheel", pv.Behavior.zoom());

var force = vis.add(pv.Layout.Force);
force.chargeConstant(function(d) {return -160;});
force.springLength(function(d) {return 90;});
force.nodes(graphData.nodes);
force.links(graphData.links);
edge = force.link.add(pv.Line);


force.node.add(pv.Dot)
	.shape('square')
	.width(50)
	.height(10)
    .lineWidth(1)
    .title(function(d) d.nodeName)
    .event("mousedown", pv.Behavior.drag())
    .event("drag", force);

	force.node.add(pv.Label)
	    .event("mousedown", pv.Behavior.drag())
	    .event("drag", force)
		.text(function (d) d.nodeName)
		.anchor('top')
		.extend()
		.add(pv.Bar)
		.width(50)
		.height(25);
/*



node = force.node.add(pv.Label);
node.cursor(function (d) { return 'pointer'; });
node.event("mousedown", pv.Behavior.drag());
node.event("drag", force);
node.text(function (d) d.nodeName);
anchor = node.anchor('top');
anchor.extend(node).add(pv.Bar).width(50).height(20).fillStyle(null);

///// NEW
box = force.node.add(pv.Bar);
box.width(function(d) {return 70;});
box.height(function(d) {return 20;});
//box.fillStyle(function (d) {return 'white';});
box.cursor(function (d) {return 'pointer';});
box.event('mousedown', pv.Behavior.drag());
box.event('drag', force);

anchor = box.anchor('bottom');
label = anchor.extend(box).add(pv.Label)
label.text(function (d) {return d.nodeName;});
//label.font(function(d) {return '14px "Helvetica Neue", Helvetica, "Arial Unicode MS", Arial, sans-serif';);
//label.textMargin(function (d) {return '.3ex';});

/*
force.node.add(pv.Bar)
	.event('mousedown', pv.Behavior.drag())
	.event('drag', force)
	.width(70)
	.height(25);
	
force.label.add(pv.Label)
	.text(function (d) d.nodeName);
*/

vis.render();