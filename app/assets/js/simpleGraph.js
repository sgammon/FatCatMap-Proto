var simpleData = {
  nodes:[
    {nodeName:"One", group:1},
    {nodeName:"Two", group:1},
    {nodeName:"Three", group:1},
    {nodeName:"Four", group:1},
    {nodeName:"Five", group:1},
    {nodeName:"Six", group:1}
  ],
  links:[
    {source:0, target:1, value:1},
    {source:1, target:2, value:8},
    {source:0, target:3, value:10},
    {source:3, target:5, value:6},
    {source:3, target:4, value:6},
    {source:4, target:2, value:6}
  ]
};


function drawContextPane(n)
{
	$('#contextPane_kind').text(n.nodeKey['kind']);
	$('#contextPane_parent').text(n.nodeKey['parent']);
	$('#contextPane_idorname').text(n.nodeKey['id_or_name']);
}