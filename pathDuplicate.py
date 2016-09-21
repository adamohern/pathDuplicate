#python
#Constrain to Path And Duplicate Assembly script
#Author: Erik Karlsson - www.erka.se
#ver: 0.96
#sep 21 2016

#Description
#This script is useful when you want to path constrain multiple objects to a curve. 
#The script creates a rig with controlobjects to easily  control the spacing, movement, axis and more of multiple objects.

#Installation
#Put the script file pathDuplicate.py in users script folder
#Put the config file pathDuplicate.CFG in users config folder
#In Modo go to System> Form Editor and look for the form "Constrain to Path and Duplicate" 
#Place the form where ever you like.

#Or
#Run the script @pathDuplicate_pop.LXM and it will pop up the form in a new palette.
#You can then map this command to a key or button for easy access to the pop-up window.

#How to use
#Select the object you want to duplicate and constrain to the cuve. Then select the curve you want to constrain to.
#Run the script from the form.

#Updates 
# 0.9:
# 	- Added option for the type of path constrain, align and position.
# 	- Added automatic resizing of locators
# 	- Added roll value for the controlobjects
# 0.95:
#	- Added option for instances and replicators
#	- The script will now work with a object that already has a user channel named "nr". This channel will be overwritten.
#	- Added wraptoggle for the controlobject
# 0.96:
#   - channelModifier.create commands updated to use "cmMathBasic:add" syntax for 90x compatibility

#Known bugs
# - In Modo 401 x64, using replicators and then running the script and then undo will only work first time.
#   If you run the script again and then undo it, modo will crash. No problems with this in Modo 401 x32.



import lx

#Assigning variables for the selected objects
mySelection = lx.eval('query sceneservice selection ? all');
myItem = mySelection[0]
curve = mySelection[1]

#Getting the user value for what type of object to duplicate, Instances or Replicators
toggleInstances = lx.eval('user.value toggleInstances ?')
toggleReplicators = lx.eval('user.value toggleReplicators ?')
lx.eval('select.drop item')

if toggleInstances == 1:
	lx.eval('select.Item %s' %(myItem))
	lx.eval('item.duplicate true type:locator all:true')
	myItem = lx.eval('query sceneservice selection ? all');
	lx.eval('select.drop item')
else:
	if toggleReplicators == 1:
		lx.eval('item.create mesh')
		lx.eval('item.name pointCloud mesh')
		pointCloudItem = lx.eval('query sceneservice selection ? all')
		lx.eval('tool.set prim.makeVertex on')
		lx.eval('tool.attr prim.makeVertex cenX 0.0')
		lx.eval('tool.attr prim.makeVertex cenY 0.0')
		lx.eval('tool.attr prim.makeVertex cenZ 0.0')
		lx.eval('tool.apply')
		lx.eval('tool.set prim.makeVertex off')
		lx.eval('item.create replicator')
		lx.eval('replicator.source %s' % (myItem))
		lx.eval('replicator.particle %s' % (pointCloudItem))
		myItem = lx.eval('query sceneservice selection ? all')
		lx.eval('select.drop item')	
		
lx.eval('select.subItem %s set' %(myItem))
lx.eval('select.subItem %s add' %(curve))

#Determing what type of pathconstrain to build
alignValue = lx.eval('user.value toggleAlign ?')
posValue = lx.eval('user.value togglePos ?')

if posValue == 1 and alignValue == 1:
	lx.eval('constraintCurve path both')
else:
	if alignValue ==1:
		lx.eval('constraintCurve path norm')
	if posValue ==1:
		lx.eval('constraintCurve path pos')
	if alignValue == 0 and posValue == 0:
		lx.eval('constraintCurve path both')

#Creating a pathconstraint with the selected curve and object
constrain = lx.eval('query sceneservice selection ? cmPathConstraint')
lx.eval('select.drop item')

#creating new channel named "nr" for the object
lx.eval('select.subItem %s set' %(constrain))
lx.eval('item.selectLinkIO output')
lx.eval('query sceneservice item.ID ? %s' % (myItem))
channelLength = lx.eval('query sceneservice channel.N ?')
lx.eval('query sceneservice item.ID ? %s' % (myItem))
NR = "nr"
i = 0
while i<channelLength:
	checkNr = lx.eval('query sceneservice channel.name ? %s' % (i))
	i = i+1
	if checkNr == "nr":
		lx.eval('select.channel {%s:%s} set' % (myItem, NR))
		lx.eval('channel.delete')
lx.eval('channel.create %s' %(NR))
lx.eval('select.channel {%s:%s} set' % (myItem, NR))
lx.eval('channel.value %s' %('0'))

#Getting the size of the object
lx.eval('select.drop item')
lx.eval('select.Item %s' %(myItem))
lx.eval('query sceneservice item.ID ? %s' %(myItem))
if lx.eval('query sceneservice isType ? mesh'):
	lx.eval('@Absolute.pl grab')
	sizeGrab = lx.eval('user.value lux_absolute_size_Uniform ?')
else:
	sizeGrab = lx.eval('item.channel locator$size ?')
	

#Creating another locator and pathconstraint to help calculating length of the curve
lx.eval('select.drop item')
lx.eval('item.create locator')
lx.eval('item.name "dummyLocator" xfrmcore')
lx.eval('select.subItem %s set'%(curve))
lx.eval('constraintCurve path both')
dummyLocator = lx.eval('query sceneservice selection ? cmPathConstraint')
lx.eval('item.channel locator$visible off')

#creating new controlItem Locator and sets new channels, Spacing, Move, Roll, Wrap and AxisXYZ.
lx.eval('select.drop item')
lx.eval('item.create locator')
lx.eval('item.name "MainController" xfrmcore')
lx.eval('item.help add label MainController')
lx.eval('item.channel locator$ihLabel.Y 0.0')
controlItem = lx.eval('query sceneservice selection ? all')
lx.eval('item.channel locator$drawShape custom')
lx.eval('item.channel locator$isShape circle')
lx.eval('item.channel locator$isAxis y')
lx.eval('item.channel locator$isSolid false')
lx.eval('item.channel locator$isRadius %s' %(sizeGrab))
lx.eval('item.channel locator$isStyle replace')
lx.eval('item.command add "item.channelHaul"')
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(controlItem))
lx.eval('channel.create Spacing distance')
lx.eval('channel.create Move distance')
lx.eval('channel.create Roll angle')
lx.eval('channel.create AxisXYZ integer scalar true 0.0 true 2.0 1.0')
lx.eval('channel.create Wrap boolean')

#creating new individual controlItem Locator and creating new channels, Offset and Roll. 
lx.eval('select.drop item')
lx.eval('item.create locator')
lx.eval('item.name "Offset Controller" xfrmcore')
IndividualControlItem = lx.eval('query sceneservice selection ? all')
lx.eval('item.channel locator$drawShape custom')
lx.eval('item.channel locator$isShape circle')
lx.eval('item.channel locator$isAxis z')
lx.eval('item.channel locator$isSolid false')
lx.eval('item.channel locator$isRadius %s' %(sizeGrab*0.5))
lx.eval('item.channel locator$isStyle replace')
lx.eval('item.command add "item.channelHaul"')
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(IndividualControlItem))
lx.eval('channel.create Offset distance')
lx.eval('channel.create Roll angle')
lx.eval('select.subItem %s add' %(myItem))
lx.eval('item.parent')

#Adding Add modifier for individual offset
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(myItem))
lx.eval('channelModifier.create "cmMathBasic:add"')
OffsetIMod = lx.eval('query sceneservice selection ? all')
lx.eval('select.channel {%s:Spacing} set' % (controlItem))
lx.eval('select.channel {%s:input1} add' % (OffsetIMod))
lx.eval('channel.link toggle')
lx.eval('select.channel {%s:Offset} set' % (IndividualControlItem))
lx.eval('select.channel {%s:input2} add' % (OffsetIMod))
lx.eval('channel.link toggle')

#Adding Divide modifier to calculate distance
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(controlItem))
lx.eval('channelModifier.create "cmMathBasic:div"')
DivideMod = lx.eval('query sceneservice selection ? all')
lx.eval('select.channel {%s:output} set' % (OffsetIMod))
lx.eval('select.channel {%s:input1} add' % (DivideMod))
lx.eval('channel.link toggle')
lx.eval('select.channel {%s:length} set' % (dummyLocator))
lx.eval('select.channel {%s:input2} add' % (DivideMod))
lx.eval('channel.link toggle')

#Adding Multiply modifier, using the unique nr channel of the object
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(controlItem))
lx.eval('channelModifier.create "cmMathBasic:mul"')
MultiMod = lx.eval('query sceneservice selection ? all')
lx.eval('select.channel {%s:output} set' % (DivideMod))
lx.eval('select.channel {%s:input1} add' % (MultiMod))
lx.eval('channel.link toggle')

#Linking The result to the path constrain
lx.eval('select.drop item')
lx.eval('select.channel {%s:output} set' % (MultiMod))
lx.eval('select.channel {%s:offset} add' % (constrain))
lx.eval('channel.link toggle')

#Linking nr to multiply modifier
lx.eval('select.drop item')
lx.eval('select.channel {%s:%s} set' % (myItem, NR))
lx.eval('select.channel {%s:input2} add' % (MultiMod))
lx.eval('channel.link toggle')

#Linking the percent value to Move
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(controlItem))
lx.eval('channelModifier.create "cmMathBasic:div"')
MoveMod = lx.eval('query sceneservice selection ? all')
lx.eval('select.channel {%s:Move} set' % (controlItem))
lx.eval('select.channel {%s:input1} add' % (MoveMod))
lx.eval('channel.link toggle')
lx.eval('select.drop item')
lx.eval('select.channel {%s:length} set' % (dummyLocator))
lx.eval('select.channel {%s:input2} add' % (MoveMod))
lx.eval('channel.link toggle')
lx.eval('select.drop item')
lx.eval('select.channel {%s:output} set' % (MoveMod))
lx.eval('select.channel {%s:percent} add' % (constrain))
lx.eval('channel.link toggle')

#Linking Pathconstrain axis to controlItem
lx.eval('select.drop item')
lx.eval('select.channel {%s:AxisXYZ} set' % (controlItem))
lx.eval('select.channel {%s:axis} add' % (constrain))
lx.eval('channel.link toggle')

#Linking Wrap to controlItem
lx.eval('select.drop item')
lx.eval('select.channel {%s:Wrap} set' % (controlItem))
lx.eval('select.channel {%s:wrap} add' % (constrain))
lx.eval('channel.link toggle')

#Linking Pathconstraint roll to controlItem
lx.eval('select.drop item')
lx.eval('select.subItem %s set' %(controlItem))
lx.eval('channelModifier.create "cmMathBasic:add"')
addRoll = lx.eval('query sceneservice selection ? all')
lx.eval('select.channel {%s:Roll} set' % (controlItem))
lx.eval('select.channel {%s:input1} add' % (addRoll))
lx.eval('channel.link toggle')
lx.eval('select.channel {%s:Roll} set' % (IndividualControlItem))
lx.eval('select.channel {%s:input2} add' % (addRoll))
lx.eval('channel.link toggle')
lx.eval('select.channel {%s:output} set' % (addRoll))
lx.eval('select.channel {%s:roll} add' % (constrain))
lx.eval('channel.link toggle')

#parent to group locator
lx.eval('select.drop item')
lx.eval('item.create groupLocator')
lx.eval('item.name "Constraint Items" groupLocator')
gLocator = lx.eval('query sceneservice selection ? all')
lx.eval('select.subItem %s set' %(myItem))
lx.eval('select.subItem %s add' %(gLocator))
lx.eval('item.parent')

spreadEven = lx.eval('user.value toggleSpread ?')
spreadEvenByNr = lx.eval('user.value toggleSpreadByNr ?')

#Calculating how to spread and duplicate the items
if spreadEven == 0 and spreadEvenByNr == 0:
	m = lx.eval('user.value offsetM ?')
	numOfItems = int(lx.eval('user.value numItems ?'))
if spreadEven == 1 and spreadEvenByNr == 0:
	m = lx.eval('user.value offsetM ?')
	lx.eval('select.drop item')
	lx.eval('query sceneservice item.ID ? %s' %(constrain))
	lengthValue = float(lx.eval('query sceneservice channel.eval ? 13'))
	numOfItems = int(lengthValue/m)
if spreadEvenByNr == 1:
	numOfItems = int(lx.eval('user.value numItems ?'))
	lx.eval('select.drop item')
	lx.eval('query sceneservice item.ID ? %s' %(constrain))
	lengthValue = float(lx.eval('query sceneservice channel.eval ? 13'))
	m = float(lengthValue/(numOfItems))
	
#Getting wrap on or off
wrapValue = lx.eval('user.value toggleWrap ?')
lx.eval('select.channel {%s:Wrap} set' % (controlItem))
lx.eval('channel.value %s' %(wrapValue))

mon = lx.Monitor()
mon.init(numOfItems)

count = 0

#Creating the duplicates
while (count < numOfItems-1):
    count = count + 1
    lx.eval('select.item %s' %(myItem))
    lx.eval('item.duplicate type:locator all:true')
    currSel = lx.eval('query sceneservice selection ? all')
    lx.eval('select.channel {%s:%s} set' % (currSel, NR))
    lx.eval('channel.value %s' %(count))
    mon.step(1)
lx.eval('select.drop item')	
lx.eval('select.item %s' %(controlItem))
lx.eval('item.channelHaul')
lx.eval('select.channel {%s:Spacing} set' % (controlItem))
lx.eval('channel.value %s'%(m))
lx.eval('select.channel {%s:Move} add' % (controlItem))
lx.eval('select.channel {%s:Roll} add' % (controlItem))
lx.eval('select.channel {%s:AxisXYZ} add' % (controlItem))
lx.eval('select.channel {%s:Wrap} add' % (controlItem))